# %load views.py
# from django.http import JsonResponse, HttpResponse
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponse
import traceback
import requests
from gensim.models.word2vec import *
from gensim.corpora.textcorpus import *
from gensim import models,similarities,corpora
import multiprocessing
from collections import namedtuple
from django.http import JsonResponse, HttpResponse
from future.standard_library import install_aliases
#import bottlenose.api
import requests
import os
from fuzzywuzzy import fuzz
from collections import namedtuple
import json
import urllib
import urllib.request
from bs4 import BeautifulSoup as bs
import re
from gensim.models.word2vec import *
from gensim.models.fasttext import *
from elasticsearch import Elasticsearch
import pickle
import sys

es = Elasticsearch(['http://127.0.0.1:9200'], sniff_on_start=True,sniff_on_connection_fail=True,sniffer_timeout=60)
#finalcor=open('final_corpus').readlines() 
f = open("final_corpus","r").readlines()
Coll = collections.namedtuple("coll","id desc")

corpus = gensim.corpora.TextCorpus()
all_docs = []

for i,j in  enumerate(f):
    hh = json.loads(j)
    all_docs.append(models.doc2vec.TaggedDocument( corpus.preprocess_text(hh['Title']+" "+hh['Description']),[str(i)]))    
doc2vec_model1 = models.doc2vec.Doc2Vec(all_docs,  window=8, min_count=5,seed=1)
doc2vec_model2 = models.doc2vec.Doc2Vec(all_docs,  window=10, min_count=5,seed=0)


def elk(query,fuzzy=0.5):
    q = {
         "query": {"multi_match": {
         "query": query,
         "fields": ["mappings.data.properties.Course Title","mappings.data.properties.Overview"],
        "type":"most_fields",
        "operator":"and",
             "fuzziness":fuzzy
          }},
          "size":20
        }
    
    new = []
    tryme = es.search(index='tata_final',body=q, request_timeout=30)
    print (json.dumps(q))
    title = []
    unique = []
    for i in tryme['hits']['hits']:
        if len(title)>0:
            if i['_source']['mappings']['data']['properties']['Course Title'] in unique:
                pass
            else: 
                source = i['_source']['mappings']['data']['properties']['Link']
                link=i['_source']['mappings']['data']['properties']['Link']
                if 'pluralsight' in source:
                    sourcce = "Pluralsight<strong>.</strong>"
                elif 'skillport' in source:
                    sourcce = "SkillSoft<strong>.</strong>"
                elif 'coursera' in source:
                    sourcce = 'Coursera<strong>.</strong>'
                else:
                    sourcce = "N/A"
                new.append(Coll(i['_source']['mappings']['data']['properties']['Course Title'],i['_source']['mappings']['data']['properties']['Overview']))
                title.append(i['_source']['mappings']['data']['properties']['Course Title']+" "+i['_source']['mappings']['data']['properties']['Overview'])
                unique.append(i['_source']['mappings']['data']['properties']['Course Title'])
        else:
            source = i['_source']['mappings']['data']['properties']['Link']
            link=i['_source']['mappings']['data']['properties']['Link']
            if 'pluralsight' in source:
                sourcce = "Pluralsight<strong>.</strong>"
            elif 'skillport' in source:
                sourcce = "SkillSoft<strong>.</strong>"
            elif 'coursera' in source:
                sourcce = 'Coursera<strong>.</strong>'
            else:
                sourcce = "N/A"
            new.append(Coll(i['_source']['mappings']['data']['properties']['Course Title'],i['_source']['mappings']['data']['properties']['Overview']))
            title.append(i['_source']['mappings']['data']['properties']['Course Title']+" "+i['_source']['mappings']['data']['properties']['Overview'])
            unique.append(i['_source']['mappings']['data']['properties']['Course Title'])

    return title, new

def pp(sims):
    a1=[]
    for i in sims:
        if i[0].isdigit():
            #print(json.loads(f[int(i[0])])['Title'])
            a1.append(Coll(json.loads(f[int(i[0])])['Title'],json.loads(f[int(i[0])])['Title']+' '+json.loads(f[int(i[0])])['Description']))
    return a1

def query(q):
    #q="leaning to deal with difficult people"
    qury=doc2vec_model2.infer_vector(q.split(),alpha=0.1, min_alpha=0.0001, steps=5)
    qury1=doc2vec_model1.infer_vector(q.split(),alpha=0.1, min_alpha=0.0001, steps=5)
    sims = doc2vec_model2.docvecs.most_similar([qury], topn=500)
    sims1=doc2vec_model1.docvecs.most_similar([qury1],topn=500)
    res_title, res_all= elk(q)
    res2=pp(sims1)+res_all
    
    res1=[]
    dicti=corpora.Dictionary.load('/datadisk/jatin/tata/dictionary')
    for i in res2:
        res1.append(dicti.doc2bow(corpus.preprocess_text(i.desc+" "+i.id)))
    gensim.corpora.SvmLightCorpus.serialize("repeat.svmlight", res1)
    mm = gensim.corpora.SvmLightCorpus("repeat.svmlight")
    tfidf = models.tfidfmodel.TfidfModel(mm)
    index_tfidf_rep=similarities.MatrixSimilarity(tfidf[mm])
    vec=dicti.doc2bow(corpus.preprocess_text(q))
    sims5=index_tfidf_rep[tfidf[vec]]
    res=sorted(enumerate(sims5),key=lambda x: x[1],reverse=True)[:10]
    """
    for i in res:
        print(''.join(res2[i[0]].id))"""
    res2=pp(sims)+res_all
    res1=[]
    dicti=corpora.Dictionary.load('/datadisk/jatin/tata/dictionary')
    for i in res2:
        res1.append(dicti.doc2bow(corpus.preprocess_text(i.desc+" "+i.id)))
    gensim.corpora.SvmLightCorpus.serialize("repeat.svmlight", res1)
    mm = gensim.corpora.SvmLightCorpus("repeat.svmlight")
    tfidf = models.tfidfmodel.TfidfModel(mm)
    index_tfidf_rep=similarities.MatrixSimilarity(tfidf[mm])
    vec=dicti.doc2bow(corpus.preprocess_text(q))
    sims5=index_tfidf_rep[tfidf[vec]]
    res=sorted(enumerate(sims5),key=lambda x: x[1],reverse=True)[:10]
    print("11111")
    result = []
    for i in res:
        dd = {"Title":''.join(res2[i[0]].id), "Description":''.join(res2[i[0]].desc)}
        result.append(json.dumps(dd))
    return result
url1 = "http://127.0.0.1:5007/query"
@csrf_exempt
def index(request):
    try:
        raw_data = request.read().decode('utf-8')
        print(raw_data)
        dict_data = json.loads(raw_data)
        query=dict_data['query']
        eks = []
        if 'what is' in query:
            q = ' '.join(query.split()[2:])
            url = "https://en.wikipedia.org/wiki/{}".format(q)
            headers = { 'User-Agent' : 'Mozilla/5.0' }
            req = urllib.request.Request(url, None, headers)
            resp = urllib.request.urlopen(req)
            s = bs(resp.read(), "lxml")
            eks.append(json.dumps({"Question":query,"Answer":'. '.join([re.sub('[^A-Za-z]+', ' ', x.text) for x in s.findAll('p')][:3])}))
        print (query) 
        output={}
        if(query !=""):                    #when empty string given
            qry=query.lower()
            result=repeat_repeat_search(qry,flag)
            if(len(result)!=0):
                print(result[:2])
                return JsonResponse(eks+result,safe=False)
            else:
                return JsonResponse([{"Title":"No results found!!!","Description":"Please Try with another Term.Thanks."}],safe=False)
        else:
            return JsonResponse([{"Title":"No query was received !  Please try again...","Description":" "}],safe=False)
    except Exception as e :
        print("Query Error!  Try again...")
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        traceback.print_exc()
        print(e)
        return JsonResponse([{"message":"Query Error!  Try again..."}],safe=False)
