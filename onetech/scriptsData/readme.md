# Migration

## NLU data
Create data for nlu model (`nlu.md` or `nlu.json`):
```
rasa data convert nlu -v -vv --data onetech/scriptsData/modifiedDFData --out onetech/scriptsData/data/nlu.{md, json} -l ru -f {md, json}
```
## Core data
Regarding the `domain.yml` and `stories.md`, one has to manually create them from dialogFlow data (or from the conversations history in DialogFlow admin page, if available). Thus we will write parser and generator ourselves to generate `domain.yml` and `stories.md`.

`domain.yml` structure will have the following structure (in json format):
```
intents: [
    intentName,
    ...
]
actions: [
    actionName,
    ...
]
templates: {
    intentName: [
        {
            text: text,
            buttons: [
                {
                    title: text
                    payload: text
                }, 
                ...
            ]
        }, 
        ...
    ],
    ...
}
```

`nlu.md` has the following structure:
```
## intent:{intentName}
- expression
- ...

...
```

`stories.md` has the following structure:
```
## story {storyName}
* intentName
    - actionName
...

...
```

__DialogFlow data structure__:

Names of intents are taken from the filenames.

There are 2 structure types of responses (from `dialogFlow/intents/` folder of Dialogflow):
* _messages - payload - quickReplyOptions (command-text, title)_
* _messages - payload - chatControl - chatButtons - buttons (title, command)_

Regarding the `stories.md` - in DialogFlow, we have contexts, so we should look into:
* input context - _contexts - [list]_
* output context - _responses - affectedContexts -[list dict{name}]_

**NOTES**: 
* Rasa-X UI is not suitable for editing the `domain.yml` file, since it doesn't allow editing templates with buttons - abort using Rasa-X UI for editing actions.
* intents `translate` (no need), `wiki` (no need),  `guide-forte-cards-cardissue-mib` (already exists in `guide-forte-cards-cardissueandactivation-mib`) will be removed
* some intents have several response texts with buttons like: `default`, `dialogs - bot - how are you`, `dialogs-bot-what_can_you_do`
* `guide-forte-mib-registration`, `dialogs - bot - hobby`, `help-forte-mib-fortetravel` intents is mispelled
* configuration from Rustem works really well, need to do some investigation in configuration
* `default` and `dialogs - bot - my name is ...` have interesting output context structure, discard temporarily
* `dialog-bot-email-to-contact-center` has input context as itself, discard temporarily
* as I understood, input context contains previous intent, and output context contains the intent itself

**TODOS**:
* __TODO__: fix the `dialogs - bot - my name is ...` intent so that it can handle `name` entity