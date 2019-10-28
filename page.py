from SLC_RW_v0_4 import readFromSLC
from SLC_RW_v0_4 import writeToSLC
#from post import post
from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return readFromSLC("SLC.clifton","F8:4")

@app.route('/thermostat', methods=['GET', 'POST'])
def slc_set():
   if request.method == 'POST':
	print (request.form)
#	if (str(request.form['tempSP0_submit'])=='Set'):
        tempSP0 = str(request.form['currentSP'])
        writeToSLC("10.1.1.139","N13:2",tempSP0)
#	elif (str(request.form['tempSP1_submit'])=='Set'):
	tempSP1 = str(request.form['awaySP'])
	writeToSLC("10.1.1.139","N13:3",tempSP1)
#	elif (str(request.form['tempSP2_submit'])=='Set'):
        tempSP2 = str(request.form['homeSP'])
        writeToSLC("10.1.1.139","N13:4",tempSP2)
#	elif (str(request.form['tempSP3_submit'])=='Set'):
        tempSP3 = str(request.form['vacationSP'])
        writeToSLC("10.1.1.139","N13:5",tempSP3)
   temp    = 	readFromSLC("10.1.1.139","F8:4")#actual temp
   tempSP0 = readFromSLC("10.1.1.139","N13:2")#current temp sp
   tempSP1 = readFromSLC("10.1.1.139","N13:3")#away temp sp
   tempSP2 = readFromSLC("10.1.1.139","N13:4")#home temp sp
   tempSP3 = readFromSLC("10.1.1.139","N13:5")#vaction temp sp

   return render_template('thermostat.html',tempSP0=tempSP0,tempSP1=tempSP1,tempSP2=tempSP2,tempSP3=tempSP3,temp=temp)   

@app.route('/tempSP0_form', methods=['POST'])
def tempSP0_set():
   if request.method == 'POST':
        tempSP0 = str(request.form['currentSP'])
        writeToSLC("10.1.1.139","N13:2",tempSP0)
   temp    =    readFromSLC("10.1.1.139","F8:4")#actual temp
   tempSP0 = readFromSLC("10.1.1.139","N13:2")#current temp sp
   tempSP1 = readFromSLC("10.1.1.139","N13:3")#away temp sp
   tempSP2 = readFromSLC("10.1.1.139","N13:4")#home temp sp
   tempSP3 = readFromSLC("10.1.1.139","N13:5")#vaction temp sp

   return render_template('thermostat.html',tempSP0=tempSP0,tempSP1=tempSP1,tempSP2=tempSP2,tempSP3=tempSP3,temp=temp)

@app.route('/tempSP1_form', methods=['POST'])
def tempSP1_set():
   if request.method == 'POST':
        tempSP1 = str(request.form['awaySP'])
        writeToSLC("10.1.1.139","N13:3",tempSP1)
   temp    =    readFromSLC("10.1.1.139","F8:4")#actual temp
   tempSP0 = readFromSLC("10.1.1.139","N13:2")#current temp sp
   tempSP1 = readFromSLC("10.1.1.139","N13:3")#away temp sp
   tempSP2 = readFromSLC("10.1.1.139","N13:4")#home temp sp
   tempSP3 = readFromSLC("10.1.1.139","N13:5")#vaction temp sp

   return render_template('thermostat.html',tempSP0=tempSP0,tempSP1=tempSP1,tempSP2=tempSP2,tempSP3=tempSP3,temp=temp)

@app.route('/tempSP2_form', methods=['POST'])
def tempSP2_set():
   if request.method == 'POST':
        tempSP2 = str(request.form['homeSP'])
        writeToSLC("10.1.1.139","N13:4",tempSP2)
   temp    =    readFromSLC("10.1.1.139","F8:4")#actual temp
   tempSP0 = readFromSLC("10.1.1.139","N13:2")#current temp sp
   tempSP1 = readFromSLC("10.1.1.139","N13:3")#away temp sp
   tempSP2 = readFromSLC("10.1.1.139","N13:4")#home temp sp
   tempSP3 = readFromSLC("10.1.1.139","N13:5")#vaction temp sp

   return render_template('thermostat.html',tempSP0=tempSP0,tempSP1=tempSP1,tempSP2=tempSP2,tempSP3=tempSP3,temp=temp)

@app.route('/tempSP3_form', methods=['POST'])
def tempSP3_set():
   if request.method == 'POST':
        tempSP3 = str(request.form['vacationSP'])
        writeToSLC("10.1.1.139","N13:5",tempSP3)
   temp    =    readFromSLC("10.1.1.139","F8:4")#actual temp
   tempSP0 = readFromSLC("10.1.1.139","N13:2")#current temp sp
   tempSP1 = readFromSLC("10.1.1.139","N13:3")#away temp sp
   tempSP2 = readFromSLC("10.1.1.139","N13:4")#home temp sp
   tempSP3 = readFromSLC("10.1.1.139","N13:5")#vaction temp sp

   return render_template('thermostat.html',tempSP0=tempSP0,tempSP1=tempSP1,tempSP2=tempSP2,tempSP3=tempSP3,temp=temp)





if __name__ == '__main__':
    app.run(host='10.1.1.216', debug=True)


