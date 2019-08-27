import json
import os
import yaml

import pickle

import sys
import argparse


PATH_DIALOGFLOW_DATA = './onetech/scriptsData/modifiedDFData/intents'
FILE_DOMAIN = './onetech/scriptsData/domain.yml'
FILE_STORIES = './onetech/scriptsData/stories.md'

def parseDialogFlowData(domain=True, stories=True):

    templates = {}
    actions = []
    intents = []
    stories = {}

    for f in sorted(os.listdir(os.path.abspath(PATH_DIALOGFLOW_DATA))):
        if 'usersays' in f:
            continue
        with open(os.path.join((os.path.abspath(PATH_DIALOGFLOW_DATA)), f), 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        
        print(f'Processing intent {data["name"]}')
        intents.append(data['name'])
        action_name = 'utter_'+data['name']
        actions.append(action_name)
        
        assert(len(data['responses']) == 1)

        if len(data['contexts']) != 0:
            if data['name'] not in stories:
                stories[data['name']] = {'input': [], 'output': []}
            if data['name'] not in stories:
                stories[data['name']] = {'input': [], 'output': []}
            for inputContext in data['contexts']:
                if inputContext not in stories:
                    stories[inputContext] = {'input': [], 'output': []}
                stories[data['name']]['input'].append(inputContext)
                stories[inputContext]['output'].append(data['name'])
            
        for response in data['responses']:
            messages = []
            buttons = []
            for message in response['messages']:
                if message['type'] == 0:
                    if  isinstance(message['speech'], list):
                        for m in message['speech']:
                            messages.append(m)
                    else:
                        messages.append(message['speech'])
                if message['type'] == 4:
                    if 'quickReplyOptions' in message['payload']:
                        for button in message['payload']['quickReplyOptions']:
                            buttons.append({
                                'title': button['command']['text'],
                                'payload': button['title'],
                            })
                            
                    elif 'chatControl' in message['payload']:
                        for button in message['payload']['chatControl']['chatButtons']['buttons']:
                            buttons.append({
                                'title': button['title'],
                                'payload': button['command'],
                            })
                            
            finalMessages = []
            for message in messages:
                tempDict = {}
                if len(buttons) > 0:
                    tempDict['text'] = message
                    tempDict['buttons'] = buttons
                    finalMessages.append(tempDict)
                else:
                    tempDict['text'] = message
                    finalMessages.append(tempDict)
            
            templates[action_name] = finalMessages

    if domain:  
        noalias_dumper = yaml.dumper.SafeDumper
        noalias_dumper.ignore_aliases = lambda self, data: True          
        with open(os.path.abspath(FILE_DOMAIN), 'w') as f:
            finalDict = {
                'intents': intents,
                'templates': templates,
                'actions': actions
            }
            yaml.dump(finalDict, f, default_flow_style=False, 
                allow_unicode=True, Dumper=noalias_dumper)

    if stories:
        endIntensForStories = []
        startIntentsForStories = []
        for k, v in stories.items():
            if len(v['output']) == 0:
                endIntensForStories.append(k)
            if len(v['input']) == 0:
                startIntentsForStories.append(k)

        storiesWhole = {}
        for s in endIntensForStories:
            if len(stories[s]['input']) > 1:
                print(s)
                break
            temp = s
            storiesWhole[s] = []
            while len(stories[temp]['input']) > 0:
                storiesWhole[s].append(stories[temp]['input'][0])
                temp = stories[temp]['input'][0]
            storiesWhole[s] = storiesWhole[s][::-1]

        
        intentsStories = []

        for k, v in storiesWhole.items():
            intentsStories.append(k)
            for i in v:
                intentsStories.append(i)

        print(f'Intents all - len {len(intents)}, set {len(set(intents))}')
        print(f'Intents stories - len {len(intentsStories)}, set {len(set(intentsStories))}')

        intentsSingle = sorted(list(set(intents) - set(intentsStories)))

        print(f'Intents single - {len(set(intentsSingle))}')

        with open(os.path.abspath(FILE_STORIES), 'w') as f:
            for intent in intentsSingle:
                f.write(f'## story {intent}\n')
                f.write(f'* {intent}\n')
                f.write(f'  - utter_{intent}\n\n')

            for k, v in storiesWhole.items():
                f.write(f'## story {k}_story\n')
                for sIntent in v:
                    f.write(f'* {sIntent}\n')
                    f.write(f'  - utter_{sIntent}\n')
                f.write(f'* {k}\n')
                f.write(f'  - utter_{k}\n\n') 

    if stories:
        print(f'Succesfully generated domain.yml file at {FILE_DOMAIN}')

    if domain:
        print(f'Succesfully generated stories.nd file at {FILE_STORIES}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create Rasa Core train files from DialogFlow data')
    parser.add_argument('--story', help='generate only stories')
    parser.add_argument('--domain', help='generate only domain')
    args = parser.parse_args()
    if args.story is not None and args.domain is not None:
        print('Please, use either --story or --domain option, if trying to generate only either stories or domain file')
    else:
        if args.story is not None:
            parseDialogFlowData(stories=True, domain=False)    
        elif args.domain is not None:
            parseDialogFlowData(stories=False, domain=True)
        else:
            parseDialogFlowData(stories=True, domain=True)