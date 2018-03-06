# %load views.py
# from django.http import JsonResponse, HttpResponse
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import sqlite3
from sqlite3 import Error
import datetime
import yagmail
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponse
import traceback
import json
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
import json
import os
from fuzzywuzzy import fuzz
from collections import namedtuple

from gensim.models.word2vec import *
from gensim.models.fasttext import *
from elasticsearch import Elasticsearch
import pickle
import sys
import re
import apiai
import uuid
import json
import requests
import sys
import urllib.request
import numpy as np
headers = {'VendorName': '8f1e76cdb1795e0489b0c87f36378b60'}
CLIENT_ACCESS_TOKEN = 'd3232251498547439e00c57310a66c94'

session_id = uuid.uuid4().hex
number_list = [111,112,113,114,115,116,117,118,119,120,121,6,7,8]

subscription_key = "96d05359d76f4e758906539daeab939e"
assert subscription_key
search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"


def main(qry):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.session_id = session_id
    request.query = qry
    response = request.getresponse()
    return json.loads(response.read().decode("utf-8"))
def QnA_scrapper(response):
    query = response['result']['parameters']['terms']
    new= {"messages": [
            {
              "type": "carousel_card",
              "platform": "google",
              "items": [

              ]
            },
            {
              "type": 0,
              "speech": ""
            }
          ]}
    driver.get("http://www.arxiv-sanity.com/search?q={0}".format(query))
    soup = BeautifulSoup(driver.page_source)
    for i in soup.findAll("div", {"class":"apaper"}):
        name = i.find("span",{"class":"ts"}).text
        pdf_link = i.find("div", {"class":"dllinks"}).find('a').get('href')
        desc = i.find("span", {"class":"tt"}).text.replace("\n"," ")
        new["messages"][0]['items'].append({
                      "optionInfo": {
                        "key": pdf_link,
                        "synonyms": []
                      },
                      "title": name,
                        "description": desc
                      
                    }) 
    return new
    
def check_intent(response,qry):
    
    try:
        if response['result']['action']=='smalltalk.user.bored':
            print("hitting this1234567898765432")
            return getingbored()
        else:
            intent = response['result']['metadata']['intentName']
            if intent == "qna":
                return QnA_scrapper(response)
            elif intent == "get_call_sheet":
                return getCallShit(response)
            elif intent=="create_schedule":
                return create_cal(response)
            elif intent=='create_schedule - yes':  
                if(len(response['result']['parameters']['email'])==0):
                    
                    return create_schedule_yes(response)
                else:
                    
                    return send_call_invite(response)
            elif intent=='create_schedule - no':
                return create_schedule_no()
            elif intent == "get_call_sheet - yes":
                return get_call_sheet_yes(response)

            elif intent == "get_call_sheet - no":
                return get_call_sheet_no(response)
            elif intent == "get_skill_name":
                return get_skill_name(response, qry)
            elif intent == "get_skill_name - yes":
                return get_skill_name_yes(response)
            elif intent == "get_skill_name - no":
                return get_skill_name_no(response)
            elif intent == "create_note":
                return create_note()
                #qry = input()
                #print(create_note_1(qry))
            elif intent == "create_note - custom":
                print("This is hit")
                return create_note_custom(response)
            elif intent == "find_record":
                return find_record(response)
            
            elif intent=='find_record - e-mail':
                if(len(response['result']['parameters']['email'])==0):
                    
                    return send_rec_ask_mail(response)
                else:
                    
                    return send_rec(response)
            elif intent == "get_Journals":
                return get_Journals(response)
            elif intent=='search_meetings':
                return search_notes(response)
            elif intent == "Welcome":
                return response['result']['fulfillment']['speech']
            elif intent == "get_profiles":
                return get_profiles(response)
            elif intent == "Help":
                return get_help(response)

            else:
                #er = []
                ##er.append(response['result']['fulfillment']['speech'])
                #er.append("These result may match your query...")
                er = bing_search(qry)
                return er
    except Exception as e:
        result = response['result']['fulfillment']['speech']
        

@csrf_exempt
def index(request):
    try:
        raw_data = request.read().decode('utf-8')
        print(raw_data)
        dict_data = json.loads(raw_data)
        #print(dict_data)
        query=dict_data['result']['resolvedQuery']
        #flag=dict_data['flag']
        print (query) 
        output={}
        if(query !=""):                    #when empty string given
            #qry=query.lower()
            #response = main(query)
            try:
                
                result = check_intent(dict_data,query)
                
            except Exception as e:
                result = dict_data['result']['fulfillment']['speech']
            
            return JsonResponse(result, content_type = "application/json", safe=False)
            
        else:
            return JsonResponse([{"Title":"No query was received !  Please try again...","Description":" "}],safe=False)
    except Exception as e :
        print("Query Error!  Try again...")
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        traceback.print_exc()
        print(e)
        return JsonResponse([{"message":"Query Error!  Try again..."}],safe=False)
