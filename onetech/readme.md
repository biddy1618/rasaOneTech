# Rasa for MIB Forte

**Rasa** is an **open source machine learning** framework for building contextual AI assistants and chatbots.

Rasa has 2 main modules:
* **NLU** for understanding user messages
* **Core** for holding conversations and deciding what to do next

**Rasa X** is a tool that helps you build, improve, and deploy AI Assistants that are powered by the Rasa framework. Rasa X includes a **user interface and a REST API**.

We will not be using Rasa X since it is [**not open-source**](https://rasa.com/docs/rasa-x/0.20.1/). Rasa X comes in Community ($0) and Enterprise (paid) editions. The community edition is free but not open source, see the license and faq.

## Rasa Tutorial

### Installation guide

Clone the project and install (more on `pip install -e` option - [here](https://stackoverflow.com/questions/35064426/when-would-the-e-editable-option-be-useful-with-pip-install?lq=1)):
```
git clone https://github.com/RasaHQ/rasa.git
cd rasa
pip install -r requirements.txt
pip install -e .
```

Install `spaCy` package (and dependencies):
```
pip install rasa[spacy]
python -m spacy download xx_ent_wiki_sm
python -m spacy link xx_ent_wiki_sm ru
pip install pymorphy2
```

I also installed `supervised_embeddings` pipeline (accidentally)
```
pip install rasa
```

### Getting started

Create folder for your project (`onetech`), navigate into it, and create first template project:
```
rasa init
```

Creates following files:

| Filename                  | Description                                          |
|---------------------------|------------------------------------------------------|
| __init__.py               | an empty file that helps python find your actions    |
| actions.py                | code for your custom actions                         |
| config.yml ‘*’            | configuration of your NLU and Core models            |
| credentials.yml           | details for connecting to other services             |
| data/nlu.md ‘*’           | your NLU training data                               |
| data/stories.md ‘*’       | your stories                                         |
| domain.yml ‘*’            | your assistant’s domain                              |
| endpoints.yml             | details for connecting to channels like fb messenger |
| models/<timestamp>.tar.gz | your initial model                                   |

The most important files are marked with a ‘*’.

`nlu.md` - NLU model file, turning user messages into structured data trough training examples that show how RASA should understand user messages. Can be provided as Markdown or as JSON (*Markdown is usually easier ot work with*). More about this [here](https://rasa.com/docs/rasa/nlu/training-data-format/#training-data-format).

`config.yml` - the configuration file defines the NLU and Core components that your model will use.
* Pipeline - pipeline for NLU model that allows you to customize your model and finetune it on your dataset.
* Policy - definition file for Core model that decides which action to take at every step in the conversation.

`stories.md` - representation of a conversation between a user and an AI assistant, converted into a specific format where user inputs are expressed as corresponding intents (and entities where necessary) while the responses of an assistant are expressed as corresponding action names.

`domain.tml` - defines the universe your assistant lives in: what user inputs it should expect to get, what actions it should be able to predict, how to respond, and what information to store. Rasa Core’s job is to choose the right action to execute at each step of the conversation. In this case, our actions simply send a message to the user.

### Architecture - Message Handling

![architecture](https://rasa.com/docs/rasa/_images/rasa-message-processing.png)

The steps are:

1. The message is received and passed to an Interpreter, which converts it into a dictionary including the original text, the intent, and any entities that were found. This part is handled by NLU.
2. The Tracker is the object which keeps track of conversation state. It receives the info that a new message has come in.
3. The policy receives the current state of the tracker.
4. The policy chooses which action to take next.
5. The chosen action is logged by the tracker.
6. A response is sent to the user.

**TODOS**:
* __TODO__: read about the NLU pipelines and Core policies

### Installed packages
* oyaml
* pymorphy2
* pandas
