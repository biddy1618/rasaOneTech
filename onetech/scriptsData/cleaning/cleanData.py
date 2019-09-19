import os
import sys

import json
import pandas as pd

import psycopg2

import yaml

import argparse

SOURCE_FILE_NLU_JSON = '/scriptsData/migration/dataNLU/nlu.json'
SOURCE_FILE_NLU_MD = './scriptsData/migration/dataNLU/nlu.md'
SOURCE_FILE_YAML = './scriptsData/migration/domain.yml'
SOURCE_FILE_STORIES = './scriptsData/migration/stories.md'
SOURCE_FILE_NLU_ERRORS = './errors.json'

CLEAN_FILE_DOMAIN = './scriptsData/cleaning/cleanData/domain.yml'
CLEAN_FILE_NLU = './scriptsData/cleaning/cleanData/nlu.md'
CLEAN_FILE_STORIES = './scriptsData/cleaning/cleanData/stories.md'

PATH_LOG = './scriptsData/cleaning/cleanData/logs.txt'


def cleanData(nluPath=SOURCE_FILE_NLU_MD, storiesPath=SOURCE_FILE_STORIES, 
    domainPath=SOURCE_FILE_YAML, nluJsonFormat=False, nluErrorsPath = SOURCE_FILE_NLU_ERRORS):
    
    intentsData = []
    if nluJsonFormat:
        print('\nReading nlu data in JSON format')
        with open(os.path.abspath(nluPath), 'r', encoding="utf-8") as f:
            jsonData = json.loads(f.read())['rasa_nlu_data']

        
        for intent in jsonData['common_examples']:
            intentsData.append([
                intent['intent'], 
                intent['text']
            ])
    else:
        print('\nReading nlu data in MD format')
        with open(os.path.abspath(nluPath), 'r') as f:
            nluData = f.readlines()

        intentName = None
        for line in nluData:
            if line.strip()[:2] == '##':
                intentName = line.strip()[10:]
            elif line.strip()[:1] == '-':
                expression = line.strip()[2:]
                intentsData.append([intentName, expression])
            else:
                continue
    
        
    intents = pd.DataFrame(
        columns=['intent_name', 'expression_text'],
        data = intentsData
    )

    print('\nReading domain data')
    with open(os.path.abspath(SOURCE_FILE_YAML), 'r', encoding="utf-8") as f:
        ymlFile = yaml.safe_load(f)

    for intent in ymlFile['intents']:
        if intent not in intents['intent_name'].values:
            print(f'Found intent that is not in intents but in actions {intent}')
    
    print('\nReading stories data')
    with open(os.path.abspath(storiesPath), 'r') as f:
        storiesData = f.readlines()

    stories = {}
    storyName = None
    story = []
    storyPair = []
    for line in storiesData:
        if line.strip()[:2] == '##':
            if len(story) == 0:
                storyName = line.strip()[3:]
                stories[storyName] = None
                continue
            stories[storyName] = story
            storyName = line.strip()[3:]
            stories[storyName] = None
            story = []
        elif line.strip()[:1] == '*':
            intent_name = line.strip()[2:]
            if intent_name not in intents['intent_name'].values:
                raise Exception(f'Intent {intent_name} \
                    found in stories.md but not in \
                    nlu.md and domain.yml')
            storyPair.append(intent_name)
        elif line.strip()[:1] == '-':
            action_name = line.strip()[2:]
            if action_name not in ymlFile['actions']:
                raise Exception(f'Action {action_name} \
                    found in stories.md but not in domain.yml')
            storyPair.append(action_name)
            story.append(tuple(storyPair))
            storyPair = []
        else:
            continue
    else:
        if storyName is not None:
            stories[storyName] = story
    
    with open(os.path.abspath(nluErrorsPath), 'r', encoding="utf-8") as f:
        jsonData = json.loads(f.read())
    
    errors = set()
    for error in jsonData:
        if error['intent_prediction']['name'].strip() == '':
            continue
        errors.add(tuple(sorted([error['intent'], \
            error['intent_prediction']['name']])))
    
    errors = sorted(list(errors))
    newIntents = {}

    for intent in intents['intent_name'].values:
        newIntents[intent] = intent

    '''
    Things to take into account:

    Stories in the form: [story1=[(intent, action), (intent, action), ...], 
                            story2=[(intent, action), (intent, action), ...]]
    THIS ONE MIGHT CAUSE SOME TROUBLE

    NLU training data in the form in DataFrame data structure:
        intent name1, expression1
        intent name1, expression2
        intent name1, expression3
        intent name2, expression1
        intent name2, expression2
        ...
    THIS ONE SHOULD BE EASY
    
    Domain training file:
        intents:
            list of intents
    THIS ONE SHOULD BE EASY
    '''

    mergedIntents = {}
    with open(os.path.abspath(PATH_LOG), 'w') as logs:
        for i, errorPair in enumerate(errors):
            intent1 = errorPair[0]
            intent2 = errorPair[1]
            
            exp1 = intents[intents['intent_name']==intent1]['expression_text'].values
            exp2 = intents[intents['intent_name']==intent2]['expression_text'].values
            
            print(f'Error number {i+1} out of {len(errors)}\nMerge intents "{intent1}" and "{intent2}"')
            logs.write(f'Error number {i+1} out of {len(errors)}\nMerge intents "{intent1}" and "{intent2}"\n')
            for i in range(0, max(len(exp1), len(exp2))):
                e1 = exp1[i] if i < len(exp1) else ''
                e2 = exp2[i] if i < len(exp2) else ''
                print(f'{e1:70s} {e2}')
                logs.write(f'{e1:70s} {e2}\n')
            
            print(('Please confirm if these intents should be merged (yes/no, default - yes)\n'
                'Default name will be used (first intent\'s name)'))
            logs.write(('Please confirm if these intents should be merged (yes/no, default - yes)\n'
                'Default name will be used (first intent\'s name)\n'))
            
            answer = input()
            # answer = 'yes'

            if answer.lower().strip()=='yes' or answer.strip() == '':
                exists = False
                for k, v in mergedIntents.items():
                    if intent1 in v or intent2 in v:
                        v.add(intent1)
                        v.add(intent2)
                        exists = True
                if not exists:
                    mergedIntents[intent1] = set([intent1, intent2])
            else:
                print(f'Not merging "{intent1}" and "{intent2}"\n')
                logs.write(f'Not merging "{intent1}" and "{intent2}"\n')
                continue
        
        for main, children in mergedIntents.items():
            listOfIntents = "".join([i+'\n' for i in sorted(list(children))])

            print(f'Merging intents:\n{listOfIntents}into intent {main}\n')
            logs.write(f'Merging intents:\n{listOfIntents}into intent {main}\n\n')
            
            
            for intent in children:
                
                # change NLU data
                intents.loc[intents['intent_name']==intent, 'intent_name']=main
                
                # change stories data
                for _, story in stories.items():
                    
                    for i, pair in enumerate(story):
                        if pair[0] == intent:
                            story[i] = (main, pair[1])
                    
                            
            
        ymlFile['intents'] = list(intents['intent_name'].unique())

    
    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, data: True          
    with open(os.path.abspath(CLEAN_FILE_DOMAIN), 'w') as f:
        yaml.dump(ymlFile, f, default_flow_style=False, 
            allow_unicode=True, Dumper=noalias_dumper)
    

    with open(os.path.abspath(CLEAN_FILE_NLU), 'w') as f:
        for intent in intents['intent_name'].unique():
            exp = intents[intents['intent_name']==intent]['expression_text'].values
            f.write(f'## intent:{intent}\n')
            for e in exp:
                f.write(f'  - {e}\n')
            f.write('\n')

    with open(os.path.abspath(CLEAN_FILE_STORIES), 'w') as f:
        for storyName, story in stories.items():
            f.write(f'## {storyName}\n')
            for pair in story:
                f.write(f'* {pair[0]}\n')
                f.write(f'  - {pair[1]}\n')
            f.write('\n')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Fix the errors in NLU data')
    parser.add_argument('--json', action='store_true', help='set if NLU file is in JSON format (default md format)')
    parser.add_argument('--nlu', default=None, help='path to NLU file')
    parser.add_argument('--stories', default=SOURCE_FILE_STORIES, help='path to stories file')
    parser.add_argument('--domain', default=SOURCE_FILE_YAML, help='path to domain file')
    args = parser.parse_args()
    if args.json and args.nlu is None:
        args.nlu = SOURCE_FILE_NLU_JSON
    elif not args.json and args.nlu is None:
        args.nlu = SOURCE_FILE_NLU_MD
    cleanData(nluPath=args.nlu, storiesPath=args.stories, domainPath=args.domain, nluJsonFormat=args.json)