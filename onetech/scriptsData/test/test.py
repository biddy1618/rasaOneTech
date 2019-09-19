import json
import os
import yaml

import pickle

import sys
import argparse
import requests

import random
import string


PATH_DIALOGFLOW_DATA = './scriptsData/migration/modifiedDFData/intents'
PATH_RESULTS_FILE = './scriptsData/test/results/results.txt'
BOT_URL = 'http://chat.onedev.zone/bot/conversations/respond'
BOT_URL_LOCAL = 'http://localhost:5005/conversations/respond'
BOT_SERVER_USE = BOT_URL

def testBot(local=False):

    global BOT_SERVER_USE 
    BOT_SERVER_USE = BOT_URL_LOCAL if local else BOT_URL

    templates = {}
    intents = []
    stories = {}
    
    for f in sorted(os.listdir(os.path.abspath(PATH_DIALOGFLOW_DATA))):
        if 'usersays' in f:
            name = f[:-17]
            if name not in templates:
                templates[name] = {}
            else:
                assert('responses' in templates[name])
            
            with open(os.path.join((os.path.abspath(PATH_DIALOGFLOW_DATA)), f), 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

            expressions = [temp['data'][0]['text'] for temp in data]

            templates[name]['expressions'] = expressions
            continue

        with open(os.path.join((os.path.abspath(PATH_DIALOGFLOW_DATA)), f), 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        
        name = data['name']
        intents.append(name)
        
        assert(len(data['responses']) == 1)

        if len(data['contexts']) != 0:
            if name not in stories:
                stories[name] = {'input': [], 'output': []}
            if name not in stories:
                stories[name] = {'input': [], 'output': []}
            for inputContext in data['contexts']:
                if inputContext not in stories:
                    stories[inputContext] = {'input': [], 'output': []}
                stories[name]['input'].append(inputContext)
                stories[inputContext]['output'].append(name)
            
        messages = []
        buttons = []
        for message in data['responses'][0]['messages']:
            if message['type'] == 0:
                if  isinstance(message['speech'], list):
                    for m in message['speech']:
                        messages.append(m)
                else:
                    messages.append(message['speech'])
            if message['type'] == 4:
                if 'quickReplyOptions' in message['payload']:
                    for button in message['payload']['quickReplyOptions']:
                        buttons.append(button['title'])
                        
                elif 'chatControl' in message['payload']:
                    for button in message['payload']['chatControl']['chatButtons']['buttons']:
                        buttons.append(button['title'])
        
        if name not in templates:
            templates[name] = {}
        else:
            assert('expressions' in templates[name])
        templates[name]['responses'] = messages
        templates[name]['buttons'] = buttons

    endIntensForStories = []
    startIntentsForStories = []
    for k, v in stories.items():
        if len(v['output']) == 0:
            endIntensForStories.append(k)
        if len(v['input']) == 0:
            startIntentsForStories.append(k)

    storiesWhole = []
    for s in endIntensForStories:
        story = [s]
        if len(stories[s]['input']) > 1:
            print(s)
            break
        temp = s
        while len(stories[temp]['input']) > 0:
            story.append(stories[temp]['input'][0])
            temp = stories[temp]['input'][0]
        storiesWhole.append(story[::-1])

    
    intentsStories = []

    for v in storiesWhole:
        for i in v:
            intentsStories.append(i)

    storySingle = sorted(list(set(intents) - set(intentsStories)))

    
    with open(PATH_RESULTS_FILE, 'w') as f:
        print(f'Checking single-level stories ({len(storySingle)} stories):')
        f.write(f'Checking single-level stories ({len(storySingle)} stories):\n')

        successSingle = 0
        for i, story in enumerate(storySingle):
            res = checkStory([story], templates)
            if res[0][0]:
                successSingle += 1
            writeStoryResult(res, i, story, f)

        print(f'Checking multi-level stories ({len(storiesWhole)} stories):')
        f.write(f'Checking multi-level stories ({len(storiesWhole)} stories):\n')
        successMulti = 0
        for i, story in enumerate(storiesWhole):
            res = checkStory(story, templates)
            if res[0][0]:
                successMulti += 1
            writeStoryResult(res, i, story[-1], f)

        print(f'Out of {len(storySingle)} single-level stories {successSingle} were successfull ({100*successSingle/len(storySingle):.1f}% accuracy).')
        f.write(f'Out of {len(storySingle)} single-level stories {successSingle} were successfull ({100*successSingle/len(storySingle):.1f}% accuracy).\n')
        print(f'Out of {len(storiesWhole)} multi-level stories {successMulti} were successfull ({100*successMulti/len(storiesWhole):.1f}% accuracy).')
        f.write(f'Out of {len(storiesWhole)} multi-level stories {successMulti} were successfull ({100*successMulti/len(storiesWhole):.1f}% accuracy).\n')
    
def id_generator(size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
   
def testCon(local=False):

    global BOT_SERVER_USE 
    BOT_SERVER_USE = BOT_URL_LOCAL if local else BOT_URL

    sender_id = id_generator()

    expression = "Ты готова?"
    data = {
        'query': expression,
        'sender_id': sender_id
    }
    response = requests.post(BOT_SERVER_USE, data=json.dumps(data)).json()[0]
    print(response)

def checkStory(story, templates):
    sender_id = id_generator()
    results = []
    for s in story:
        expression = random.choice(templates[s]['expressions'])
        buttons = None if 'buttons' not in templates[s] else templates[s]['buttons']

        if buttons is not None:
            query = {'expressions' :templates[s]['expressions'], 'expression': expression, \
                'responses': [r.strip().lower() for r in templates[s]['responses']], 'buttons': buttons}
        else:
            query = {'expressions' :templates[s]['expressions'], 'expression': expression, \
                'responses': [r.strip().lower() for r in templates[s]['responses']]}

        data = {
            'query': expression,
            'sender_id': sender_id
        }
        
        
        # try:
        response = requests.post(BOT_SERVER_USE, data=json.dumps(data)).json()[0]
        # except Exception as e:
        #     response = {'text': 'fail'}
        
        
        result = {
            'response': response['text'].strip().lower(), 
            'buttons': [r['title'] for r in response['buttons']]
        } if 'buttons' in response else {'response': response['text'].strip().lower()}
        
        results.append((expression, query['responses'], result['response']))
        res = check(query, result)
        if res[0]:
            continue
        else:
            return (res, results)

    return (res, results)

def check(query, result):
    if result['response'] not in query['responses']:
        return (False, 'response')
    
    if ('button' in query) != ('button' in result):
        return (False, 'buttons')

    if 'button' in query:
        for button in result['buttons']:
            if button not in query['buttons']:
                return (False, 'buttons')
    
    return (True, 'perfect')
    

def writeStoryResult(res, i, story, file):
    if res[0][0]:
        print(f'{i+1} --> Successful story - {story}')
        file.write(f'{i+1} --> Successful story - {story}\n')
    else:
        print(f'{i+1} --> Failed story - {story}:')
        file.write(f'{i+1} --> Failed story - {story}:\n')
        for k in range(0, len(res[1])-1):
            temp = res[1][k]
            print(f'---{temp[0]}')
            file.write(f'---{temp[0]}\n')
            print(f'------{temp[2]}')
            file.write(f'------{temp[2]}\n')
        print(f'---{res[1][-1][0]}')
        file.write(f'---{res[1][-1][0]}\n')
        if res[0][1] == 'response':
            print('------Error - response mismatch')
            file.write('------Error - response mismatch\n')
            print(f'---------DF: {res[1][-1][1]}')
            file.write(f'---------DF: {res[1][-1][1]}\n')
            print(f'---------Rasa: {res[1][-1][2]}')
            file.write(f'---------Rasa: {res[1][-1][2]}\n')
        else:
            print('------Error - buttons mismatch')
            file.write('------Error - buttons mismatch\n')
            print(f'---------{res[1][-1][1]}')
            file.write(f'---------{res[1][-1][1]}\n')

    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create Rasa Core train files from DialogFlow data')
    parser.add_argument('--test', action='store_true', help='test the server (check if it is up)')
    parser.add_argument('--local', action='store_true', help='start testing the local server (default remote)')
    args = parser.parse_args()
    
    if args.test:
        testCon(local=args.local)
    else:
        testBot(local=args.local)
        