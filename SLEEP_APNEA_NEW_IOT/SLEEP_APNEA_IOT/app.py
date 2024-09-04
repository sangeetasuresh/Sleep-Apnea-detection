from flask import Flask, render_template, request, flash, redirect
import sqlite3
import pickle
import numpy as np
from warnings import filterwarnings
filterwarnings('ignore')

app = Flask(__name__)
import pickle
rf=pickle.load(open("model/rf.pkl","rb"))

    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if result:
            import requests
            import pandas as pd
            data=requests.get("https://api.thingspeak.com/channels/2364064/feeds.json?results=2")
            ecg=data.json()['feeds'][-1]['field2']
            spo2=data.json()['feeds'][-1]['field3']
            bpm=data.json()['feeds'][-1]['field4']
            print(f"heart beat : {bpm} \n spo2 : {spo2} \n ECG : {ecg}")
            return render_template('fetal.html',spo2=spo2,ecg=ecg,bpm=bpm)
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
        cursor.execute(command)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    return render_template('index.html')


@app.route("/fetalPage", methods=['GET', 'POST'])
def fetalPage():
    import requests
    import pandas as pd
    data=requests.get("https://api.thingspeak.com/channels/2364064/feeds.json?results=2")
    ecg=data.json()['feeds'][-1]['field2']
    spo2=data.json()['feeds'][-1]['field3']
    bpm=data.json()['feeds'][-1]['field4']
    print(f"heart beat : {bpm} \n spo2 : {spo2} \n ECG : {ecg}")
    return render_template('fetal.html',spo2=spo2,ecg=ecg,bpm=bpm)




@app.route("/predict", methods = ['POST', 'GET'])
def predictPage():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        slp_d = request.form['slp_d']
        qos = request.form['qos']
        pal = request.form['pal']
        sl = request.form['sl']
        bmi = request.form['bmi']
        hr = request.form['hr']
        ds = request.form['ds']
        ecg = request.form['ecg']
        spo2 = request.form['spo2']
        
        # Temperature = request.form['Temperature']
        data = np.array([[gender, age, slp_d, qos, pal, sl, bmi,hr,ds,ecg,spo2]])
        my_prediction = rf.predict(data)
        result = my_prediction[0]
        
        print(result)

        
        if result == 1 :
            res='Normal'
        elif result == 2: 
            res='Insomia'
        elif result == 3:
            res='Sleep Apnea'
        
        # print(res)

           
        return render_template('predict.html',name=name, pred = result,status=result)

    return render_template('predict.html')

if __name__ == '__main__':
	app.run(debug = True)