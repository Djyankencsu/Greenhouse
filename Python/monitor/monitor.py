from twilio.rest import Client
import os
import datetime
import time
from dateutil import parser

os.chdir(os.path.dirname(__file__))

data_dir = ""
params_dir = ""

if os.path.exists(os.path.abspath("../../../data")) and os.path.exists(os.path.abspath("../../../params")):
    data_dir = os.path.abspath("../../../data")+"/"
    params_dir = os.path.abspath("../../../params")+"/"
    print("Found Data and Parameter directories")
else:
    print("Data or Parameter directories not found.")
    data_dir = None
    params_dir = None

main_params = {}

def get_greenhouse_data():
    file_path = os.path.join(data_dir,"temps.txt")
    data_line = ""
    with open(file_path, "r") as source_file:
        data_line = source_file.readlines()[-1]
    data_line = data_line.split(",")
    timestamp = parser.parse(data_line[0])
    value = float(data_line[1])
    return timestamp, value

def read_params():
    global counter
    if params_dir is not None:
        file = open(params_dir+"twilio.txt","r")
        data = file.read().strip()
        list_params = data.split("\n")
        for each in list_params:
            holder = each.split("=")
            main_params[holder[0]]=holder[1]
        file.close()

def voice_formatter(temperature):
    temperature = str(temperature).split(".")
    decimals = list(temperature[1])
    return " ".join([temperature[0],"point",decimals[0],decimals[1],"degrees","Fahrenheit"])

read_params()

def panic(temp = None,time = None):
    client = Client(main_params.get("AccountSID"), main_params.get("AuthToken"))
    if time is not None and temp is not None:
        payload = "<Response><Say>Alert! It has been " + str(time) + " minutes since last update, and last recorded temperature was "+ voice_formatter(temp) +".</Say></Response>"
    elif temp is not None:
        payload = "<Response><Say>Alert! Current temperature is " + voice_formatter(temp) + "</Say></Response>"
    elif time is not None:
        payload = "<Response><Say>Alert! It has been " + str(time) + " minutes since last update, and temperature was less than 50 degrees.</Say></Response>"
    call = client.calls.create(
                            twiml=payload,
                            to='+19196077727',
                            from_='+17865634668'
                        )
    print("Made emergency call:",call.sid)


next_check = datetime.datetime.now()
while True:
    timenow = datetime.datetime.now()
    if timenow > next_check:
        alerted = False
        timestamp, temperature = get_greenhouse_data()
        if (timenow - timestamp) < datetime.timedelta(minutes = 4):
            next_check = timestamp + datetime.timedelta(minutes=5)
        elif (timenow - timestamp) > datetime.timedelta(minutes = 4):
            if temperature < 50.0:
                panic(temp = temperature, time = int((timenow - timestamp).seconds / 60.0))
                next_check = timenow + datetime.timedelta(minutes=5)
                alerted = True
        if temperature < 42.0 and not alerted:
            panic(temp = temperature)
            next_check = timenow + datetime.timedelta(minutes=5)
            alerted = True
    time.sleep(30)