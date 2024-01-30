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

if os.path.exists(os.path.abspath("../../../data")) and os.path.exists(os.path.abspath("../../../params")):
    data_dir = os.path.abspath("../../../data")+"/"
    params_dir = os.path.abspath("../../../params")+"/"
    print("Found Data and Parameter directories")
else:
    print("Data or Parameter directories not found.")
    data_dir = None
    params_dir = None

main_params = {}
counter =0
password_attempt =[datetime.datetime.now(),0]

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
        dict_holder = load_data_file(data_dir +main_params["TempFile"])
        dict_split = []
        for each in dict_holder:
            if ((time_reference - time_length) < each[0]) and (each[0] < time_reference):
                dict_split.append(each)
        if len(dict_split) < 2: return "Insufficient Data from Time Period Given"
        x,y = zip(*dict_split)
        xtick_holder = np.linspace((time_reference-time_length).timestamp(),time_reference.timestamp(),8)
        xtick_holder = [datetime.datetime.fromtimestamp(each) for each in xtick_holder]
        plt.rcParams["figure.figsize"] = (10,5)
        plt.plot(x,y,linestyle="solid",linewidth=1.0,color="blue")
        plt.plot(x,y,marker="o",markerfacecolor="red",markersize=3)
        plt.plot(xtick_holder,[42 for each in xtick_holder],"r")
        plt.xlabel("Timestamp (24hr EST)",labelpad=12)
        plt.ylabel("Temperature (˚F)")
        plt.yticks(np.linspace(0,120,13))
        plt.xlim([xtick_holder[0],xtick_holder[-1]])
        plt.xticks(xtick_holder)
        plt.grid(color="gray",linestyle="-", linewidth=0.5)
        tick_counter = 0
        for each in xtick_holder:
            plt.annotate(each.strftime("%X"),xy=(tick_counter/7.0,-0.085),xycoords="axes fraction",horizontalalignment="center")
            tick_counter += 1
        plt.savefig(os.path.join(os.path.abspath(os.path.dirname(__file__)),"static/graph.jpg"),dpi=600)
        plt.clf()
        return 0

def load_data_file(file_path):
    file = open(file_path,"r")
    data = file.read().strip()
    data_list = data.split("\n")
    storage_dict = {}
    for each in data_list:
        holder = each.split(",")
        time_holder = parser.parse(holder[0])
        storage_dict[time_holder] = float(holder[1])
    dict_split = storage_dict.items()
    dict_split = sorted(dict_split)
    return dict_split

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
    
def preserve_arguments(arguments,keys=True,dict_ret=False,rem_graph=False):
    query = "?"
    holder_dict = {}
    for each in arguments.keys():
        if (each in ["ReadKey","WriteKey"] and not keys):
            pass
        elif (rem_graph and (each in ["Time","EndDate"])):
            pass
        elif dict_ret:
            holder_dict[each] = arguments[each]
        else:
            query += each + "=" + arguments[each]+"&"
    query = query[0:-1]
    if not dict_ret:
        return query
    else:
        return holder_dict

app = Flask(__name__)

@app.route("/")
def index():
    global password_attempt
    arguments = request.args.to_dict()
    if ("WriteKey" in arguments.keys()) or ("ReadKey" in arguments.keys()):
        return render_template("options.html",Keys=preserve_arguments(arguments))
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) in [None,""]):
        return render_template("pwlogin.html", ImagePath="static/login.png")
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) != main_params["Password"]):
        if password_attempt[1]==0:
            password_attempt[0] = datetime.datetime.now()
            password_attempt[1] = 1
            return render_template("pwlogin.html", ImagePath="static/failure.png")
        elif password_attempt[1] < int(main_params["PasswordAttempts"]):
            password_attempt[1] += 1
            return render_template("pwlogin.html", ImagePath="static/failure.png")
        elif password_attempt[0] < (datetime.datetime.now() - datetime.timedelta(seconds=float(main_params["PasswordTime"]))):
            password_attempt = [datetime.datetime.now(),0]
            return render_template("pwlogin.html", ImagePath="static/failure.png")
        elif password_attempt[1] >= int(main_params["PasswordAttempts"]):
            password_attempt[0] = datetime.datetime.now()
            return render_template("locked.html",Time=main_params["PasswordTime"])
    elif (main_params["PWEnable"] == "True") and (arguments.get("password",None) == main_params["Password"]):
        if (password_attempt[1] >= int(main_params["PasswordAttempts"])) and (password_attempt[0] > (datetime.datetime.now() - datetime.timedelta(seconds=float(main_params["PasswordTime"])))):
            password_attempt[0] = datetime.datetime.now()
            return render_template("locked.html",Time=main_params["PasswordTime"])
        else:
            password_attempt = [datetime.datetime.now(),0]
            query_holder = "/?ReadKey"+"="+main_params["ReadKey"]
            return redirect(query_holder)
    elif (main_params["PWEnable"] == "False") and ("password" in arguments.keys()):
        return render_template("pwdisabled.html", message="Password login is currently disabled. Please enter access keys manually.")
    else:
        return render_template("pwdisabled.html",message="")
        
@app.route("/write")
def write_data():
    arguments = request.args.to_dict()
    if arguments.get("WriteKey") == main_params["WriteKey"]:
        data=request.args.get(main_params["Temp"])
        if data is not None:
            file = open(data_dir+main_params["TempFile"],"a")
            file.write(datetime.datetime.now().strftime("%x-%X")+","+data+"\n")
            file.close()
            return render_template("writesuccess.html")
        else:
            return render_template("writefail.html")
    else:
        return redirect("/"+preserve_arguments(arguments))

@app.route("/now")
def current_cond():
    arguments = request.args.to_dict()
    data_list = load_data_file(data_dir +main_params["TempFile"])
    return render_template("current.html",TimeStamp=data_list[-1][0].strftime("%a %b %-d-%X").split("-"),Temperature=data_list[-1][1])

@app.route("/image")
def show_img():
    global counter
    arguments = request.args.to_dict()
    if arguments["ReadKey"] == main_params["ReadKey"]:
        image_name = str(counter).zfill(int(main_params["ImgNameLength"]))+".jpg"
        image_path=data_dir+"images/"+image_name
        if os.path.exists(image_path):
            shutil.copy(image_path,(os.path.dirname(os.path.abspath(__file__))+"/static/image.jpg"))
            holder = {"ImagePath":"static/image.jpg"}
            counter += 1
            return render_template("image.html",**holder)
        else:
            return render_template("error.html",Err_Desc="Image Path Does not Exist",Keys=preserve_arguments(arguments))
    else:
        return redirect("/"+preserve_arguments(arguments,False))
    
@app.route("/graph")
def show_graph():
    arguments = request.args.to_dict()
    if arguments.get("ReadKey") == main_params["ReadKey"]:
        oldest_point = datetime.timedelta(days=7)
        stop_point = datetime.datetime.now()
        if "Time" in arguments.keys():
            oldest_point = read_time_arg(arguments["Time"])
        if "EndDate" in arguments.keys():
            stop_point = parser.parse(arguments["EndDate"])
        success = generate_plot(oldest_point,stop_point)
        if success == 0:
            holder = {"ImagePath":"static/graph.jpg","Keys":preserve_arguments(arguments,rem_graph=True)}
            return render_template("graph.html",**holder, KeyDict=preserve_arguments(arguments,dict_ret=True))
        else:
            holder = {"Err_Desc":success,"Keys":preserve_arguments(arguments)}
            return render_template("error.html",**holder)
    else:
        return redirect("/"+preserve_arguments(arguments,False))

@app.route("/help")
def show_help():
    arguments = request.args.to_dict()
    return render_template("statichelp.html",Keys=preserve_arguments(arguments))
    
if __name__ == '__main__':
    read_params()
    app.run(debug=True,port=23507,host='0.0.0.0')