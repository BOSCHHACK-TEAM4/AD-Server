from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time
import http.client
import logging
import pandas as pd
import numpy as np
import os
import random



logger = logging.getLogger(__name__)

# Create your views here.

index1 = 1
index2 = 2
index3 = 3
age = 25
gender = "female"
humanNum = 0

temperature = 37
humidity = 100
millilux = 0
pollution = 0

filename = './grading criteria.csv'

initValue = 0
maxValue = 0


adNum = 20
featNum = 9

grades = np.zeros(adNum)

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
    millilux = data['millilux']

def loadAdMatrix(filename):
    file = open(os.path.join(os.path.dirname(__file__), filename))
    df = pd.read_csv(file)
    data = df.as_matrix()
    # return {'initValue': data[:data.shape[0]-2, 1:], 'maxValue': data[data.shape[0]-1,1:]}
    global initValue, maxValue
    initValue = data[:data.shape[0]-1, 1:]
    maxValue = data[data.shape[0]-1,1:]
    logger.error(initValue.shape)
    logger.error(maxValue.shape)


def updateIndices():
    global index1, index2, index3
    indices = grades.argsort()
    indices = indices[::-1]
    index1 = int(indices[0])
    index2 = int(indices[1])
    index3 = int(indices[2])
    logger.error("index1 " + str(index1))
    logger.error("index2 " + str(index2))
    logger.error("index3 " + str(index3))

def mappingAge(rawAge):
    if (rawAge < 6):
        return 0;
    if (rawAge < 15):
        return 1;
    if (rawAge < 25):
        return 2;
    if (rawAge < 40):
        return 3;
    return 4;

def mappingGender(rawGender):
    if (rawGender == "female"):
        return 2;
    return 0;

def mappingFacialHair(moustache, beard, sideburns):
    if (moustache + beard + sideburns > 0.6):
        return 2;
    return 0;

def mappingHair(bald, invisible):
    if (bald > 0.6):
        return 0;
    return 2;

def mappingMakeup(eyeMakeup, lipMakeup):
    return eyeMakeup or lipMakeup;

def mappingPm25(pollution):
    if (pollution > 200):
        return 2;
    return 1;

def mappingTemperature(rawTemperature):
    return rawTemperature / 20;

def mappingMillilux(rawMillilux):
    return rawMillilux / 240000;

def mappingHumidity(rawHumidity):
    return rawHumidity / 50;


def gradeFunc(infoarray):
    scale = [1, 20, 2, 3, 5, 10, 5, 3, 5]
    global grades
    for i in range(0, featNum):
        for j in range(0, adNum):
            # print(j)
            absoluteValue = np.abs(infoarray[i] - initValue[j,i])
            grades[j] += (maxValue[i] - absoluteValue) * scale[i] # * absoluteValue / maxValue[i]

@csrf_exempt
def index(request):
    global index1, index2, index3, age, gender, humanNum, temperature, humidity, millilux, pollution
    if request.method == 'GET':
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
        'humanNum': humanNum,
        }
        
        json_data = json.dumps(data)
        response = HttpResponse(json_data)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response;


    if request.method == 'POST':
        global initValue, initValue
        loadAdMatrix(filename)

        logger.error(initValue.shape)

        jsonStr = request.body

        logger.error(jsonStr)
        dataDict = json.loads(jsonStr)
        pollution = int(dataDict['air'])

        faceDictList = dataDict['face']

        humanNum = len(faceDictList)
        if (humanNum == 0):
            age = 'NONE'
            gender = 'NONE'
            # index1 = random.randint(0, 19)
            # index2 = random.randint(0, 19)
            # index3 = random.randint(0, 19)
            # logger.error("random choose")
            # logger.error("index1 " + str(index1))
            # logger.error("index2 " + str(index2))
            # logger.error("index3 " + str(index3))
        else:
            for dic in faceDictList:
                logger.error(dic)
                attributes = dic['faceAttributes']
                gender = attributes['gender']
                age = attributes['age']
                moustache = attributes['facialHair']['moustache']
                beard = attributes['facialHair']['beard']
                sideburns = attributes['facialHair']['sideburns']
                eyeMakeup = attributes['makeup']['eyeMakeup']
                lipMakeup = attributes['makeup']['lipMakeup']
                bald = attributes['hair']['bald']
                hairInvisible = attributes['hair']['invisible']
                faceInfo = np.zeros(9)
                faceInfo[0] = mappingAge(age)
                faceInfo[1] = mappingGender(gender)
                faceInfo[2] = mappingFacialHair(moustache, beard, sideburns)
                faceInfo[3] = mappingHair(bald, hairInvisible)
                faceInfo[4] = mappingMakeup(eyeMakeup, lipMakeup)
                faceInfo[5] = mappingPm25(pollution)
                faceInfo[6] = mappingTemperature(temperature)
                faceInfo[7] = mappingMillilux(millilux)
                faceInfo[8] = mappingHumidity(humidity)
                gradeFunc(faceInfo)
                updateIndices()

        return HttpResponse("Post Success!")
    else:
        logger.error("ERROR")
        return HttpResponseNotFound()