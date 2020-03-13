import os
import re
import json
from elasticsearch import Elasticsearch, helpers
from jinja2 import Template
import sys


# conf files paths
CONF = json.load(open(os.path.join(os.getcwd(), "elastic_conf.json")))
DOC_PATH = os.path.join(os.getcwd(), "lisa")

# query template path
QUERY_TEMPLATE_PATH = os.path.join(os.getcwd(), "query_template.jinja2")

INDEX_NAME = CONF["index"]

# request elastic database with questions
def es_search(query):
    es_client = Elasticsearch(CONF["elastic_host"], http_auth=(CONF["elastic_user"], CONF["elastic_pwd"]), scheme="https",
                             port=443)
    if not es_client.indices.exists(INDEX_NAME):
        raise("Unknow index. Check the variable !!")

    template = Template(open(QUERY_TEMPLATE_PATH, 'r').read())

    query_body = template.render(query=value)
    es_res = es_client.search(index=INDEX_NAME, body=query_body)
    return es_res


def main():
    if INDEX_NAME is None:
        raise("Please Set up an index name !!")

    if len(sys.argv) != 2:
        raise "ONLY ONE PARAM ALLOWED !!\nUSAGE: %s 'phrase query'" % sys.argv[0]
    ret = es_search(sys.argv[1])
    print ret


if __name__ == "__main__":
    main()
