import os
import re
import json
from elasticsearch import Elasticsearch, helpers
from jinja2 import Template


# conf files paths
CONF = json.load(open(os.path.join(os.getcwd(), "elastic_conf.json")))
DOC_PATH = os.path.join(os.getcwd(), "lisa")

# query template path
QUERY_TEMPLATE_PATH = os.path.join(os.getcwd(), "query_template.jinja2")

# Load global var from conf files
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


def get_reference():
"""
    Get wanted result from golden source file
"""
    res = dict()
    fd = open(os.path.join(DOC_PATH, "LISARJ.NUM"), 'r')
    data = [int(x) for x in fd.read().split()]
    data_len = len(data)
    idx = 0
    while idx < data_len:
        doc_num = data[idx]
        tot_res = data[idx + 1]
        list_res = [data[idx + 2 + x] for x in range(tot_res)]
        res[doc_num] = list_res
        idx += 2 + tot_res

    return res


def get_questions():
"""
    Load questions from file
"""
    res = dict()
    fd = open(os.path.join(DOC_PATH, "LISA.QUE"), 'r')
    data = fd.read().split("#")
    data = [ x.split("\n") for x in data]
    data = [' '.join(x).split() for x in data]
    data = [ " ".join(x[1:]) for x in data]
    
    for idx, question in enumerate(data):
        res[idx + 1] = question

    return res

def es_search(question_list):
"""
    request elastic database with questions
"""
    es_client = Elasticsearch(CONF["elastic_host"], http_auth=(CONF["elastic_user"], CONF["elastic_pwd"]), scheme="https",
                              port=443)
    if not es_client.indices.exists(INDEX_NAME):
        raise("Send data to Elastic DB before !!")

    template = Template(open(QUERY_TEMPLATE_PATH, 'r').read())

    data_result = dict()

    for key, value in question_list.items():
        query_body = template.render(query=value)
        es_res = es_client.search(index=INDEX_NAME, body=query_body)
        tmp = es_res["hits"]["hits"]
        data_result[key] = [int(x["_id"]) for x in tmp]

    return data_result

def evaluate(result_dic, ref_dic):
"""
    compute result
"""
    total_good_answer = 0
    total_answer = 0
    total_wanted_answer = 0

    for key in ref_dic.keys():
        good_answer = len(list(set([ x for x in result_dic[key] if x in ref_dic[key]])))
        total_good_answer += good_answer
        total_answer += len(list(set(result_dic[key])))
        total_wanted_answer += len(list(set(ref_dic[key])))


    ret = {
        "precision" : total_good_answer / total_answer,
        "recall" : total_good_answer / total_wanted_answer
    }
    if ret["precision"] != 0 or ret["recall"] != 0:
        ret["F1"] = (ret["precision"] * ret["recall"]) / (ret["precision"] + ret["recall"])
    else:
        ret["F1"] = 0
    return ret

def main():
    if INDEX_NAME is None:
        raise("Please Set up an index name !!")
    question_dic = get_questions()
    es_result_dic = es_search(question_dic)
    data_ref_dic = get_reference()

    result = evaluate(es_result_dic, data_ref_dic)

    print(result)


if __name__ == "__main__":
    main()
