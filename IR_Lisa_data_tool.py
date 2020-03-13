import os
import re
import json
from elasticsearch import Elasticsearch, helpers

# Conf files paths
CONF = json.load(open(os.path.join(os.getcwd(), "elastic_conf.json")))
DOC_PATH = os.path.join(os.getcwd(), "lisa")

# Load global variable
if os.path.exists(os.path.join(os.getcwd(), "settings.json")):
    INDEX_SETTINGS = json.load(
        open(os.path.exists(os.path.join(os.getcwd(), "settings.json"))))
else:
    INDEX_SETTINGS = None

if os.path.exists(os.path.join(os.getcwd(), "settings.json")):
    INDEX_MAPPING = json.load(
        open(os.path.exists(os.path.join(os.getcwd(), "mapping.json"))))
else:
    INDEX_MAPPING = None

INDEX_NAME = CONF["index"]


def get_docs():
    doc_dic = dict()

    list_filenames = [file_name for file_name in os.listdir(
        DOC_PATH) if re.match("LISA[0-9].*", file_name)]

    prior_line = ""

    for doc_path in [os.path.join(DOC_PATH, doc_name) for doc_name in list_filenames]:
        fd = open(doc_path, 'r')
        for idx, line in enumerate(fd.readlines()):
            if line.startswith('Document') and idx == 0:
                document_number = int(
                    ' '.join(line.split()).split(" ")[-1].split('\n')[0])
                doc_dic[document_number] = str()
            elif line.startswith('Document') and prior_line.startswith("****"):
                document_number = int(
                    ' '.join(line.split()).split(" ")[-1].split('\n')[0])
                doc_dic[document_number] = str()
            elif not line.startswith("***"):
                doc_dic[document_number] += line
            prior_line = line

    return doc_dic

# Wrapper for bulk operation
def _bulk_wrapper(index_name, data_dic):
    for key, value in data_dic.items():
        yield {
            "_index": index_name,
            "_id": key,
            "body": value
        }


def send2elastic(data_dic):
    es_client = Elasticsearch(CONF["elastic_host"], http_auth=(CONF["elastic_user"], CONF["elastic_pwd"]), scheme="https",
                              port=443)

    body = dict()
    if INDEX_SETTINGS is not None:
        body["settings"] = INDEX_SETTINGS
    if INDEX_MAPPING is not None:
        body["mappings"] = INDEX_MAPPING

    if es_client.indices.exists(INDEX_NAME):
        print("Delete existing %s index" % INDEX_NAME)
        es_client.indices.delete(INDEX_NAME)
    es_client.indices.create(index=INDEX_NAME, body=body)

    response = helpers.bulk(es_client, _bulk_wrapper(INDEX_NAME, data_dic))
    es_client.indices.flush(INDEX_NAME)
    print('All done !!')


def main():
    if INDEX_NAME is None:
        raise("Please Set up an index name !!")
    data_dic = get_docs()
    send2elastic(data_dic)


if __name__ == "__main__":
    main()
