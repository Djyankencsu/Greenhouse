from flask import Flask, render_template, request, redirect
import os
import shutil
import datetime
from dateutil import parser
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

os.chdir(os.path.dirname(__file__))

if os.path.exists(os.path.abspath("../../data")) and os.path.exists(os.path.abspath("../../params")):
    data_dir = os.path.abspath("../../data")+"/"
    params_dir = os.path.abspath("../../params")+"/"
    print("Found Data and Parameter directories")
else:
    print("Data or Parameter directories not found.")
    data_dir = None
    params_dir = None

main_params = {}
counter =0

def read_params():
    global counter
    if params_dir is not None:
        file = open(params_dir+"main.txt","r")
        data = file.read().strip()
        list_params = data.split("\n")
        for each in list_params:
            holder = each.split("=")
            main_params[holder[0]]=holder[1]
        file.close()
        counter = int(main_params["CounterBase"])

def generate_plot(time_length, time_reference):
    if data_dir is not None:
        file = open(data_dir + "temps.txt","r")
        data = file.read().strip()
        data_list = data.split("\n")
        storage_dict = {}
        for each in data_list:
            holder = each.split(",")
            time_holder = parser.parse(holder[0])
            if ((time_reference - time_length) < time_holder) and (time_holder < time_reference):
                storage_dict[time_holder] = float(holder[1])
        dict_split = storage_dict.items()
        dict_split = sorted(dict_split)
        x,y = zip(*dict_split)
        plt.rcParams["figure.figsize"] = (10,5)
        plt.plot(x,y,"bo-")
        plt.plot(x,[42 for each in x],"r")
        plt.xlabel("Time")
        plt.ylabel("Temperature (˚F)")
        plt.yticks(np.linspace(0,120,13))
        xtick_holder = np.linspace((time_reference-time_length).timestamp(),time_reference.timestamp(),7)
        plt.xticks([datetime.datetime.fromtimestamp(each) for each in xtick_holder])
        plt.savefig(os.path.join(os.path.abspath(os.path.dirname(__file__)),"static/graph.jpg"))
        plt.clf()

def read_time_arg(input_string):
    holder_int = ""
    holder_char = ""
    input_string.strip()
    for each in input_string:
        if each.isnumeric():
            holder_int += each
        elif each in "hdw":
            holder_char = each
    holder_int = int(holder_int)
    if holder_char == "h":
        return datetime.timedelta(hours=holder_int)
    elif holder_char == "d":
        return datetime.timedelta(days=holder_int)
    elif holder_char == "w":
        return datetime.timedelta(weeks=holder_int)

app = Flask(__name__)

@app.route("/")
def index():
    arguments = request.args.to_dict()
    if ("WriteKey" in arguments.keys()) or ("ReadKey" in arguments.keys()):
        query = "?"
        for each in arguments.keys():
            query += each + "=" + arguments[each]+"&"
        query = query[0:-1]
        return render_template("options.html",Keys=query)
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) in [None,""]):
        return render_template("pwlogin.html", ImagePath="static/login.png")
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) != main_params["Password"]):
        return render_template("pwlogin.html", ImagePath="static/failure.png")
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) == main_params["Password"]):
        query_holder = "/?WriteKey"+"="+main_params["WriteKey"]+"&ReadKey"+"="+main_params["ReadKey"]
        return redirect(query_holder)
    elif (main_params["PWEnable"] == "False") and ("password" in arguments.keys()):
        return render_template("pwdisabled.html", message="Password login is currently disabled. Please enter access keys manually.")
    else:
        return render_template("pwdisabled.html",message="")
        
@app.route("/write")
def write_data():
    arguments = request.args.to_dict()
    if arguments["WriteKey"] == main_params["WriteKey"]:
        data=request.args.get(main_params["Temp"])
        if data is not None:
            file = open(data_dir+main_params["TempFile"],"a")
            file.write(datetime.datetime.now().strftime("%x-%X")+","+data+"\n")
            file.close()
            return render_template("writesuccess.html")
    return render_template("index.html")

@app.route("/image")
def show_img():
    global counter
    arguments = request.args.to_dict()
    if arguments["ReadKey"] == main_params["ReadKey"]:
        image_name = str(counter).zfill(int(main_params["ImgNameLength"]))+".jpg"
        image_path=data_dir+"images/"+image_name
        shutil.copy(image_path,(os.path.dirname(os.path.abspath(__file__))+"/static/image.jpg"))
        holder = {"ImagePath":"static/image.jpg"}
        counter += 1
        return render_template("image.html",**holder)
    
@app.route("/graph")
def show_graph():
    arguments = request.args.to_dict()
    if arguments["ReadKey"] == main_params["ReadKey"]:
        oldest_point = datetime.timedelta(days=7)
        stop_point = datetime.datetime.now()
        if "Time" in arguments.keys():
            oldest_point = read_time_arg(arguments["Time"])
        if "EndDate" in arguments.keys():
            stop_point = parser.parse(arguments["EndDate"])
        generate_plot(oldest_point,stop_point)
        holder = {"ImagePath":"static/graph.jpg"}
        return render_template("graph.html",**holder)
    
if __name__ == '__main__':
    read_params()
    app.run(debug=True,port=80,host='0.0.0.0')