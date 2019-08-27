import json
import os
import yaml
import oyaml as yaml

from collections import OrderedDict 

'''
templates will have the following structure (in json format):

templates: 
    dict(
        intentName: [
            dict(
                text: text,
                buttons: [
                    dict(
                        title: text
                        payload: text
                    ), 
                    ...
                ]
            ), 
            ...
        ],
        ...
    )
    
'''

'''
NOTE:
As I understood, buttons will be stored in
messages - payload - quickReplyOptions

NOTE 2:
There are 2 structure types of responses:
    messages - payload - quickReplyOptions (command-text, title)
and
    messages - payload - chatControl - chatButtons - buttons (title, command)

NOTE 3 (regarding contexts):
input context is located at
    contexts - [list]
and output context is located at
    responses - affectedContexts -[list dict{name}]
'''
templates = {}
actions = []
intents = []
stories = {}

for file in sorted(os.listdir('./onetech/scriptsData/intents')):
    if 'usersays' in file:
        continue
    with open('./onetech/scriptsData/intents/' + file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    action_name = 'utter_'+data['name']
    actions.append(action_name)
    intents.append(data['name'])
    # print(data['name'])
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
                        # tempDict = {}
                        # tempDict['title'] = button['command']['text']
                        # tempDict['payload'] = button['title']
                        # buttons.append(tempDict)
                        buttons.append({
                            'title': button['command']['text'],
                            'payload': button['title'],
                        })
                        
                elif 'chatControl' in message['payload']:
                    for button in message['payload']['chatControl']['chatButtons']['buttons']:
                        # tempDict = {}
                        # tempDict['title'] = button['title'],
                        # tempDict['payload'] = button['command']
                        # buttons.append(tempDict)
                        buttons.append({
                            'title': button['title'],
                            'payload': button['command'],
                        })
                        # if action_name == 'utter_dialogs - bot - are you busy':
                        #     print(type(tempDict['title']))
                        #     print(tempDict['title'])
                        #     print(type(tempDict['payload']))
                        #     print(tempDict['payload'])        
                        #     print(buttons)        
                        
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
    
# with open('./onetech/scriptsData/storiesGen.md', 'w') as f:
#     for k, v in storiesWhole.items():
#         f.write(f'## story {k}_story\n')
#         for sIntent in v:
#             f.write(f'* {sIntent}\n')
#             f.write(f'  - utter_{sIntent}\n')
#         f.write(f'* {k}\n')
#         f.write(f'  - utter_{k}\n\n') 

# print(json.dumps(stories, indent=4))

# with open('./onetech/scriptsData/templatesGen.yml', 'w') as f:
#     finalDict = {
#         'templates': templates,
#         'actions': actions
#     }
#     yaml.dump(finalDict, f, default_flow_style=False, allow_unicode=True)


# with open('./onetech/scriptsData/stories.md', 'w') as f:
#     for i, intent in enumerate(intents):
#         if intent not in startIntentsForStories:
#             f.write(f'## story {intent}\n')
#             f.write(f'* {intent}\n')
#             f.write(f'  - utter_{intent}\n\n')
    
#     for k, v in storiesWhole.items():
#         f.write(f'## story {k}_story\n')
#         for sIntent in v:
#             f.write(f'* {sIntent}\n')
#             f.write(f'  - utter_{sIntent}\n')
#         f.write(f'* {k}\n')
#         f.write(f'  - utter_{k}\n\n') 
# print(json.dumps(templates, indent=4, ensure_ascii=False))
# print(json.dumps(templates['utter_dialogs - bot - how are you'], indent=4, ensure_ascii=False))


with open('./onetech/dataFromRustem/test.yml', 'r') as f:
    data = yaml.safe_load(f)

"""
intents
templates
actions
"""
intentsRF = data['intents']
actionsRF = data['actions']
templatesRF = data['templates']

print('Intents that are in DF and not in Rustem files:')
for i in intents:
    if i not in intentsRF:
        print(f'"{i}"')
print()
print('Intents that are in Rustem files system and not in DF:')
for i in intentsRF:
    if i not in intents:
        print(f'"{i}"')
print()

print('Actions that are in DF and not in Rustem files:')
for i in actions:
    if i not in actionsRF:
        print(f'"{i}"')
print()
print('Intents that are in Rustem files system and not in DF:')
for i in actionsRF:
    if i not in actions:
        print(f'"{i}"')
print()

for k, v in templates.items():
    if k not in templatesRF:
        print(f'Action {k} absent in RF')
        print()
        continue
    if len(v) != len(templatesRF[k]):
        print(f'Action {k} has different number of responses')
        print(f'DF version: {v}')
        print(f'RF version {templatesRF[k]}')
        print()
        continue
    for text in v:
        if 'buttons' in text and 'buttons' not in templatesRF[k][0]:
            print(f'Action {k} - buttons difference')
            print(f'DF version: {v}')
            print(f'RF version {templatesRF[k]}')
            print()
            continue
