import os

os.chdir(os.path.dirname(__file__))
params_dir = os.path.abspath("../../../params")+"/"
main_path = os.path.join(params_dir,"main.txt")
wifi_path = os.path.join(params_dir,"wifi.txt")
arduino_path = os.path.join(params_dir,"arduino.txt")
header_path = os.path.join(params_dir,"config.h")

if os.path.exists(params_dir):
    print("Found parameter directory.")
else:
    raise FileNotFoundError

if os.path.exists(main_path):
    print("Found main parameter file.")
else:
    raise FileNotFoundError

if os.path.exists(wifi_path):
    print("Found wifi parameter file.")
else:
    raise FileNotFoundError

if os.path.exists(arduino_path):
    print("Found Arduino parameter file.")
else:
    raise FileNotFoundError

header_content = ""
main_file = open(main_path)
main_lines = [x for x in main_file.readlines() if "Key" in x]
main_file.close()

for each in main_lines:
    holder = each.strip().split("=")
    header_content += "#define " + holder[0].upper()+" \""+holder[1]+"\"\n"

wifi_file = open(wifi_path)
wifi_lines = wifi_file.readlines()
wifi_file.close()

for each in wifi_lines:
    holder = each.strip().split("=")
    header_content += "#define " + holder[0].upper()+" \""+holder[1]+"\"\n"

arduino_file = open(arduino_path)
arduino_lines = arduino_file.readlines()
arduino_file.close()

for each in arduino_lines:
    holder = each.strip().split("=")
    header_content += "#define " + holder[0].upper()+" \""+holder[1]+"\"\n"

header_file = open(header_path,"w")
header_file.write(header_content)
header_file.close()