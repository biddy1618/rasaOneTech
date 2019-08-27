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

## Table that corresponds to connections of intents in stories - `rasa_ui.intent_story`

3 columns:
* id - integer primary key (for indexing)
* parent_id - integer ID for the parent intent (foreign key for intents.intent_id)
* intent_id - integer ID for the intent itself (foreign key for intents.intent_id)


Operations with stories:
* `CREATE STORY` - given parent intent ID and current intent ID, create new record in `rasa_ui.intent_story` with those IDs.
* `REMOVE STORY` - when deleting parent intent from intent edit page, remove __single__ record where `intent_id` = current intent's ID and `parent_id` = parent intent's ID.
* `REMOVE INTENT` - when deleting the intent, also delete __all__ records with `intent_id` = ID of deleted intent, and `parent_id` = ID of deleted intent from table `rasa_ui.intent_story`.


**TODOS**:
* __TODO__: read about the NLU pipelines and Core policies

### Installed packages
* oyaml
* pymorphy2
