import json
import os
import yaml


with open('./onetech/scriptsData/templates.yml', 'r') as f:
    data = yaml.safe_load(f)

print(json.dumps(data, indent=4))

'''
for file in os.listdir('./onetech/scriptsData/intents'):
    if 'usersays' in file:
        continue
    with open('./onetech/scriptsData/intents/' + file, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    # print(json.dumps(data, indent=4, ensure_ascii=False))
    action_name = 'utter'+data['name']
    responses = []
    for response in data['responses']:
        messages = []
        buttons = []
        for message in response['messages']:
            if message['type'] == 0:
                messages.append(message['speech'])
            if message['type'] == 4:
                for button in message['payload']['quickReplyOptions']:
                    buttons.append({
                        'title': button['command']['text'],
                        'payload': button['title']
                    })
        responses.append({
            'messages': messages,
            'buttons': buttons
        })
    print(json.dumps({
        'action_name': action_name,
        'responses': responses
    }, indent=4, ensure_ascii=False))
    break
'''