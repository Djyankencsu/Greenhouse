from flask import Flask, render_template, request
import os
import shutil

if os.path.exists(os.path.abspath("../../data")) and os.path.exists(os.path.abspath("../../params")):
    data_dir = os.path.abspath("../../data")+"/"
    params_dir = os.path.abspath("../../params")+"/"
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

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
        
@app.route("/write")
def write_data():
    if request.args.get("WriteKey") == main_params["WriteKey"]:
        file = open(data_dir+main_params["TempFile"],"a")
        data=request.args.get(main_params["Temp"])
        if data is not None:
            file.write(data+",")
        file.close()
        return render_template("success.html")
    return render_template("index.html")

@app.route("/image")
def show_img():
    global counter
    if request.args.get("ReadKey") == main_params["ReadKey"]:
        image_name = str(counter).zfill(int(main_params["ImgNameLength"]))+".jpg"
        image_path=data_dir+"images/"+image_name
        shutil.copy(image_path,(os.path.dirname(os.path.abspath(__file__))+"/static/image.jpg"))
        holder = {"ImagePath":"static/image.jpg"}
        counter += 1
        return render_template("image.html",**holder)
    
if __name__ == '__main__':
    read_params()
    app.run(debug=True,port=80,host='0.0.0.0')