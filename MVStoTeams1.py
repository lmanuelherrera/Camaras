#Consulta datos del dispositivo

from pprint import pprint
from flask import Flask, json, request, render_template
import sys, os, getopt, json
from webexteamssdk import WebexTeamsAPI
#import adaptive_cards
#import slack_cards
import requests
import meraki
import time
import shutil
import datetime
import pymsteams

import credentials  # noqa

import time
import json
import locale
import logging
import sqlite3
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

locale.setlocale(locale.LC_ALL, '')
today = datetime.datetime.utcnow()
day_access = datetime.date.today() + datetime.timedelta(days=10)
day_refresh = datetime.date.today() + datetime.timedelta(days=85)
client_id = "Cecfb8c11e92e732d13e78d528a7714432820859b0ddd1b7238779709f611d98c"
client_secret = "0f04b932a98e6e7d54a57514605b7198208331264a7cc4d28c74cf4e66239d32"

Camaras = {
    "Camara_Frontera":"Q2GV-HY57-H937",
    "MV22_Camara_1":"Q2HV-FU4B-5CRT",
    "MV32_Camara_1":"Q2PV-AUAR-4K3G",
    "MV32_Camara_2":"Q2PV-TNTC-G8TZ",
    "MV32_Camara_3":"Q2PV-YHGR-9HGY",
    "MV32_Camara_4":"Q2PV-64NS-7G4F",
    "MV32_Camara_5":"Q2PV-C7SJ-ERD7",
    "MV32_Camara_6":"Q2PV-ZEE6-RRXG",
}

for x in Camaras:
    print(x)
    print(Camaras[x])
    print("")
    
    serial = Camaras[x]
    
    meraki_headers = {'X-Cisco-Meraki-API-Key': '8f7fae459f872d4a64493ec0df5d28c2152d68e3'}
    """
    ## Live API
    print('MV Sense Live API')
    meraki_live_url = 'https://api.meraki.com/api/v1/devices/'+serial+'/camera/analytics/live'
    meraki_live_response = requests.get(meraki_live_url, headers=meraki_headers)
    meraki_live_response_json=json.loads(meraki_live_response.text)
    num_of_person_detected=meraki_live_response_json['zones']['0']['person']
    print(num_of_person_detected)
    """
    ##Get Device
    print('Get Device')
    #nombre_device = x
    meraki_device_url = 'https://api.meraki.com/api/v1/devices/'+serial
    meraki_device_response = requests.get(meraki_device_url, headers=meraki_headers)
    meraki_device_response_json=json.loads(meraki_device_response.text)
    print("")
    pprint(meraki_device_response_json)
    print("")
    nombre_device=meraki_device_response_json['name']
    print(nombre_device)
    """
    ## Snapshot API
    print('Snapshot API')
    meraki_snapshot_url='https://api.meraki.com/api/v1/devices/'+serial+'/camera/generateSnapshot'
    meraki_snapshot_response = requests.post(meraki_snapshot_url, headers=meraki_headers)
    time.sleep(5)
    meraki_snapshot_response_json=json.loads(meraki_snapshot_response.text)
    snapshot_url=meraki_snapshot_response_json['url']
    print(snapshot_url)
    
    # Teams API 
    # MS URL
    #import requests
    #import json

    url = "https://intellego365.webhook.office.com/webhookb2/51ee0df2-da6a-4546-a7c6-c4dd1996316b@00a05ce0-bd3d-4215-a569-c6261a20a39e/IncomingWebhook/32f21017b58d4e7c9cebd78867af2e2c/6d7d8f86-a22c-4098-8447-dc58315e185b"

    payload = json.dumps({
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "0076D7",
    "summary": "Luis Herrera ha creado un nuevo mensaje 1",
    "sections": [
        {
        "activityTitle": "Luis Herrera ha creado un nuevo mensaje 2",
        "activitySubtitle": "Para las Camaras Meraki",
        "activityImage": snapshot_url,
        "facts": [
            {
            "name": "Nombre Camara",
            "value": x
            },
            {
            "name": "Personas",
            "value": num_of_person_detected
            },
            {
            "name": "Serial",
            "value": serial
            }
        ],
        "markdown": True
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
"""