from django.shortcuts import render
from django.http import HttpResponse
import json
import time
import http.client

# Create your views here.

index1 = 1
index2 = 2
index3 = 3
age = 25
gender = "female"
temperature = 37
humidity = 100


def getFromXDK():
    global temperature, humidity
    conn = http.client.HTTPConnection("42.159.133.122:8082")
    conn.request("GET", "/mongodb/boschxdk20/latestdata")
    response = conn.getresponse()
    data = response.read()
    conn.close()
    data = json.loads(data)
    humidity = data['humidity']
    temperature = data['temperature']

def updateIndex():
    global index1, index2, index3

def index(request):
    getFromXDK()

    data = {
    'index1': index1,
    'index2': index2,
    'index3': index3,
    'age': age,
    'gender': gender,
    'temperature': temperature,
    'humidity': humidity,
    'time': time.strftime("%d/%m/%Y %H:%M"),
    }
    
    json_data = json.dumps(data)
    response = HttpResponse(json_data)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response;