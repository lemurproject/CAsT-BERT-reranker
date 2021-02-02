from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
import simplejson
import pprint
import sys
import time
import torch
import argparse
from bert_model import BertRank
import sys
import os
import json
from urllib3 import PoolManager
import urllib.request

app = Flask(__name__, static_url_path='')

model = torch.load('bert_model.1600000.pkl')
model.args.max_seq_length = 256
softmax = torch.nn.Softmax(dim=1)
model.eval()

def batch_iter(test_doc_ids, test_docs, batch_size=16):

    total = len(test_doc_ids)
    count = 0
    temp_ids = []
    temp_docs = []
    length = 0

    while length < total:
        temp_ids.append(test_doc_ids[length])
        temp_docs.append(test_docs[length])
        count += 1
        if count == batch_size:
            yield temp_ids, temp_docs
            count = 0
            temp_ids = []
            temp_docs = []

        length += 1

    if count > 0:
        yield temp_ids, temp_docs 
    
def rerank(query, response):

    dicter = {}
    test_doc_ids = []
    test_docs = []
    for doc in response["response"]["docs"]:
        test_doc_ids.append(doc["id"])
        test_docs.append((query, doc["fulltext"][0]))
        dicter[doc["id"]] = doc["fulltext"][0]

    output_list = []

    with torch.no_grad():
        for batch in batch_iter(test_doc_ids, test_docs):
            p_ids, passages = batch
            outputs = model(passages)
            outputs = softmax(outputs)

            for pas_id, probs in zip(p_ids, outputs):
                output_list.append((probs[1].item(), pas_id))

    torch.cuda.empty_cache()
    output_list = sorted(output_list, key=lambda x:x[0], reverse=True)

    doc_list = []
    for score, doc_id in output_list:
        temp_dict = {}
        temp_dict["fulltext"] = [dicter[doc_id]]
        temp_dict["id"] = doc_id
        temp_dict["score"] = score
        doc_list.append(temp_dict)

    return doc_list
    

@app.route("/about", methods=['GET'])
def about():
    return send_from_directory('.', 'about.html')


@app.route("/", methods=['GET'])
def index():
   return render_template('index.html')

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

def make_query(q):
    splitted = json.loads(q)["q"].split(" ")
    splitted = [each for each in splitted if len(each) > 0 and each != '?']
    return "+".join(['fulltext:' + x for x in splitted])

#endpoint search
@app.route('/search', methods=['POST', 'GET'])
def search():
    start_time = time.time()    # Do not remove.
    q = request.get_data()
    current_query = json.loads(q)["q"]
    query = make_query(q)  # Do not remove
    # Can edit following code
    collection = "[COLLECTION_NAME_1,COLLECTIOM_NAME_2]"
    url        = '[SOLR_URL]' + '/solr/' + collection + '/query?'
    q          = "q=" + query
    fl         = "fl=id,score,fulltext"
    sort       = "sort=score+desc"
    rows       = "rows=500"
    wt         = "wt=json"
    params     = [ q, fl, sort, wt, rows ]
    p          = "&".join(params)

    connection = urllib.request.urlopen(url+p)
    response   = simplejson.load(connection)
    reranked = rerank(current_query, response)
    response["response"]["docs"] = reranked
    response["queryDuration"] = time.time() - start_time    # Do not remove
    return response
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=23232, debug=True)
