# CNAM Lessons

## Steb by steb run

1. (optional) active a local en in this project
1. `pip install -r requirements.txt`
1. `mkdir lisa && tar -C ./lisa -xf lisa.tar.gz`
1. Open the `elastic_conf.json` file and fill empty fields
1. Load elasticsearch with `python IR_Lisa_data_toot.py`
1. Evaluate your result with `python IR_evaluate_lisa.py`

> Another file `play_with_data.py` is like a sandbox. Letting you able to play with requests.

> **You can play with the kiban dev_tools to understand your queries**

## LISA data

LISA stands for Library and Information Science Abstracts

Source and doc: [http://ir.dcs.gla.ac.uk/resources/test_collections/lisa/](http://ir.dcs.gla.ac.uk/resources/test_collections/lisa/)

## Manage Settings, Mappings and Query

If files `settings.json` and / or `mapping.json` exists in this root project. They are load during the index building.

### Settings file
Setting documentation [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html#indices-create-api-example) and [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html)

file example :
```json
{
    "settings" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 1
    }
}
```

### Mapping file
Mapping documentation [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) and [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html)

file example :
```json
{
  "my-index" : {
    "mappings" : {
      "properties" : {
        "age" : {
          "type" : "integer"
        },
        "email" : {
          "type" : "keyword"
        },
        "employee-id" : {
          "type" : "keyword",
          "index" : false
        },
        "name" : {
          "type" : "text"
        }
      }
    }
  }
}
```

### query_template.jinja2

Templated file to fine tune the query request body.

`{{query}}` is the substituted part of the request.

[documentation can be find here](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html)