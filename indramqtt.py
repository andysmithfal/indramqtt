import requests
import json
import paho.mqtt.client as mqtt
import time
import os
from datetime import datetime


username = os.environ['indrausername']
password = os.environ['indrapassword']
deviceID = os.environ['indradeviceid']

mqttserver = os.environ['mqttserver']
mqttport = int(os.environ['mqttport'])
mqttuser = os.environ['mqttuser']
mqttpassword = os.environ['mqttpassword']
mqtttopic = os.environ['mqtttopic']

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            # mqttpublish(client, mqtttopic)
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt.Client("py-ev-charger")
    client.username_pw_set(mqttuser, mqttpassword)
    client.on_connect = on_connect
    client.connect(mqttserver, mqttport)
    return client

def mqttpublish(client, topic):
    tokenurl = "https://identity.gridsvc.net/login"

    tokenpayload = json.dumps(
        {"username": username,"password": password,"ignoreChallenges": "True"}
    )

    tokenheaders = {
    'Accept': 'application/json',
    'Host': 'identity.gridsvc.net',
    'Content-Type': 'application/json',
    'Accept-Language': 'en-gb',
    'Origin': 'https://app.indra.co.uk',
    'Referer': 'https://app.indra.co.uk/'
    }

    tokenresponse = requests.request("POST", tokenurl, headers=tokenheaders, data=tokenpayload)
    token = tokenresponse.json().get("accessToken")
    # print(token)

    url = "https://maestro.vcharge.io/query/?k=&q=true&swc=false"

    payload = json.dumps({
    "query": "query GetCustomerDeviceState($deviceId:String) {  device(deviceId:$deviceId) {    currentState {      ev {        status                chargeRate {          total     }        stateOfCharge        isPluggedIn        lastUpdated      }    }  }}",
    "variables": {
        "deviceId": deviceID
    }
    })

    now = datetime.now()

    energypayload = json.dumps({
    "query": "query GetDeviceEnergyConsumption($from: String, $to: String, $deviceId: String) {  device(deviceId: $deviceId) {    id    energyConsumption(from: $from, to: $to) {      from      to      totals {        actualEnergyConsumptionWh        cost      }    }  }}",
    "variables": {
        "from": now.strftime("%Y-%m-%d")+"T00:00:00.000Z",
        "to": now.strftime("%Y-%m-%d")+"T23:59:59.999Z",
        "deviceId": deviceID
    }
    })

    headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-gb',
    'Authorization': 'Bearer '+token,
    'Content-Type': 'application/json',
    'Host': 'maestro.vcharge.io',
    'Origin': 'https://app.indra.co.uk',
    'Referer': 'https://app.indra.co.uk/',
    'x-client-id': 'CUSTOMER'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    energyresponse = requests.request("POST", url, headers=headers, data=energypayload)

    #status is IDLE or CHARGING
    status = response.json().get("data").get("device").get("currentState").get("ev").get("status")
    #in watts (will be a minus number when car is charging)
    chargeRate = response.json().get("data").get("device").get("currentState").get("ev").get("chargeRate").get("total")
    #bool
    pluggedIn = response.json().get("data").get("device").get("currentState").get("ev").get("isPluggedIn")
    #2022-08-11T22:59:23.052Z
    lastUpdated = response.json().get("data").get("device").get("currentState").get("ev").get("lastUpdated")
    #convert the charge rate from e.g. -7128 to 7.1kW
    chargeRate = str(round((-chargeRate)/1000,1))+"kW"

    kwhToday = energyresponse.json().get("data").get("device").get("energyConsumption").get("totals").get("actualEnergyConsumptionWh")
    kwhToday = kwhToday/1000

    costToday = energyresponse.json().get("data").get("device").get("energyConsumption").get("totals").get("cost")
    costToday = "£"+str(round(costToday/100,2))

    # print(chargeRate)
    client.publish(topic+"/status", status)
    client.publish(topic+"/chargeRate", chargeRate)
    client.publish(topic+"/pluggedIn", pluggedIn)
    client.publish(topic+"/lastUpdated", lastUpdated)
    client.publish(topic+"/kwhToday", kwhToday)
    client.publish(topic+"/costToday", costToday)

#print(response.text)
client = connect_mqtt()
client.loop_start()

while True:
    mqttpublish(client, mqtttopic)
    time.sleep(60)