# Greenhouse
## Setup
First, find the SampleExternalDirs and copy each subdirectory to the same folder as the GitHub repo is cloned to locally. After this, you should have a params folder and a data folder next to the root directory of the GitHub repo. 
In the params folder, go through each file and add the data and keys needed. Change the example password and any other data that needs to change for the destination system. 
Next, change directory to Greenhouse/Python/setup. Run the file c_gen.py, which will take the contents of the parameter directory files and output a config.h file. This is for use in the Arduino script. 
To add the new config header file to the Arduino script, open the destination script in the Arduino IDE. Go to Sketch and click Add File... and select the config.h file in the dialog. 