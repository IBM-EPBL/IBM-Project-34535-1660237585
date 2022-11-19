from flask import Flask, render_template, request, session, redirect, url_for
# from sklearn.externals import joblib
import joblib
import pandas as pd
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.secret_key = '12345'
 
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'heart'

mysql = MySQL(app)
print("connected")

@app.route('/')
def home():
    print(session)
    return render_template("home.html", session = session)

@app.route("/about")
def about():
    return render_template("about.html", session = session)   

@app.route("/original")
def original():
    if "loggedin" in session:
        return render_template('original.html', session = session)
    else:
        return redirect(url_for("register"))

@app.route("/register", methods = ["POST", "GET"])
def register():
    if "loggedin" in session:
        return redirect(url_for("home"))
    else:
        if request.method == 'POST':
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO users VALUES (NULL, %s, %s, %s)", (name, email, password, ))
            mysql.connection.commit()
            print(name, email, password)
        return render_template("register.html", loginError = False, session = session)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email_id = %s AND password = %s", (email, password, ))
        result = cursor.fetchone()
        if result:
            session["loggedin"] = True
            session["id"] = result["user_id"]
            session["name"] = result["name"]
            print(session)
            return redirect(url_for("original"))
        else:
            print("pee")
            return render_template("register.html", loginError = True)
    return render_template("register.html", loginError = False, session = session)


@app.route("/predict", methods=['GET','POST'])
def predict():
    res = ""
    if request.method == 'POST':
        age = float(request.form['age'])
        sex = float(request.form['sex'])
        cp = float(request.form['cp'])
        trestbps = float(request.form['trestbps'])
        chol = float(request.form['chol'])
        fbs= float(request.form['fbs'])
        restecg = float(request.form['restecg'])
        thalach = float(request.form['thalach'])
        exang = float(request.form['exang'])
        oldpeak = float(request.form['oldpeak'])
        slope = float(request.form['slope'])
        ca = float(request.form['ca'])
        thal = float(request.form['thal'])

      

        pred_args = [age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]

        mul_reg = open('heart_svm_13.pkl','rb')
        ml_model = joblib.load(mul_reg)
        model_predcition = ml_model.predict([pred_args])
        if model_predcition == 1:
            res = 'Affected'
        else:
            res = 'Not affected'
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO data VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (session["id"], int(age), int(sex), int(cp), int(trestbps), int(chol), int(fbs), int(restecg), int(thalach), int(exang), int(oldpeak), int(slope), int(ca), int(thal), res, ))
        mysql.connection.commit()
        print("inserted")
    if res == "":
        return render_template('original.html')
    else:
        return render_template('predict.html', prediction = res)

@app.route("/pastdata", methods = ["GET", "POST"])
def pastdata():
    if "loggedin" in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM data WHERE user_id = %s", (session["id"], ))
        result = cursor.fetchall()
        print(list(result))
        return render_template('pastdata.html', result = result)
    else:
        return redirect(url_for("register"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug = True)
