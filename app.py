#!/usr/bin/env python
#coding: utf-8

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


import os
import bz2
import re
from tqdm import tqdm
import tensorflow as tf
from sklearn.utils import shuffle
from matplotlib import pyplot as plt
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding,LSTM,Dropout,Dense
from keras.callbacks import EarlyStopping, ModelCheckpoint
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from keras.models import load_model
from keras import backend as K

#sql imports
import sys
from flask import Flask, render_template, url_for,json, request, jsonify, redirect
import MySQLdb

# In[2]: Load Model


model = load_model('LSTMmodel.h5')
print("model loaded")


# # In[3]: Train Model


train_file = bz2.BZ2File('test.ft.txt.bz2')


# # # In[4]:


train_file_lines = train_file.readlines()
train_file_lines = [x.decode('utf-8') for x in train_file_lines]
train_labels = [0 if x.split(' ')[0] == '__label__1' else 1 for x in train_file_lines]
train_sentences = [x.split(' ', 1)[1][:-1].lower() for x in train_file_lines]
for i in range(len(train_sentences)):
    train_sentences[i] = re.sub('\d','0',train_sentences[i])
    
                                                       
for i in range(len(train_sentences)):
    if 'www.' in train_sentences[i] or 'http:' in train_sentences[i] or 'https:' in train_sentences[i] or '.com' in train_sentences[i]:
        train_sentences[i] = re.sub(r"([^ ]+(?<=\.[a-z]{3}))", "<url>", train_sentences[i])
X_train,X_test,y_train,y_test=train_test_split(train_sentences,train_labels,train_size=0.80,test_size=0.20,random_state=42)
tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(X_train)


# #In[5]: Find the rating


def rate(p):
   return (p*5)


# # In[6]:



# In[7]:



app = Flask(__name__)


conn = MySQLdb.connect("localhost","rahul","Rahul@123","rating")
c = conn.cursor()

session={}
# In[8]:
@app.route("/")
def start():
    return render_template('login.html')

@app.route("/ref",methods=['POST','GET'])
def ref():
    global session
    message = request.get_json(force=True)
    uname = message['uname']
    passwd = message['passwd']
  
    conn = MySQLdb.connect(host= "localhost",
                   user="rahul",
                   passwd="Rahul@123",
                   db="rating")
    c = conn.cursor()
    query="select name from user where name ='"+str(uname)+"' and password='"+str(passwd)+"'"
    c.execute(query)
    data=c.fetchall()
    if len(data)==1:
        session["user_name"]=uname
       
        return "http://127.0.0.1:5000/index"
    else:
        return "http://127.0.0.1:5000/"


@app.route("/adminsignin")
def adminsignin():
    return render_template('adminsignin.html')


@app.route("/adminlogin",methods=['POST','GET'])
def adminlogin():
    message = request.get_json(force=True)
    uname = message['uname']
    passwd = message['passwd']
  
    conn = MySQLdb.connect(host= "localhost",
                   user="rahul",
                   passwd="Rahul@123",
                   db="rating")
    c = conn.cursor()
    query="select name from admin where name ='"+str(uname)+"' and password='"+str(passwd)+"'"
    c.execute(query)
    data=c.fetchall()
    if len(data)==1:       
        return "http://127.0.0.1:5000/admin"
    else:
        return "http://127.0.0.1:5000/adminsignin"



@app.route("/admin",methods=['POST','GET'])
def admin():
    return render_template("admin.html")


@app.route("/updateproduct",methods=['POST','GET'])
def updateproduct():
    
    print("Posted file: {}".format(request.files['file']))
    file = request.files['file']

    productname=request.form.get('product')
    productprice=request.form.get('price')
    print(productname)
    print(productprice)
    
   
    conn = MySQLdb.connect(host= "localhost",
                user="rahul",
                passwd="Rahul@123",
                db="rating")
    c = conn.cursor()
    query="select * from product_details"
    c.execute(query)
    conn.commit()
    data=c.fetchall()
    count=len(data)
    file_name=str(count)+'.jpg'
    print(file_name)
    file.filename = file_name
    file.save("/home/rahul/Documents/web lab work/project/Product_Rating_based_on_user_review/static/images/"+file.filename) 
    
    print("image saved")
    query="""insert into product_details(name,price) values(%s,%s)"""
    data = (productname,productprice)
    c.execute(query,data)
    conn.commit()
    data1=c.fetchall()
    return render_template("admin.html")

@app.route("/signup",methods=['POST','GET'])
def signup():
    message = request.get_json(force=True)
    uname = message['uname1']
    passwd = message['passwd1']
    email=message['email']
    print(uname+passwd+email)
    conn = MySQLdb.connect(host= "localhost",
                   user="rahul",
                   passwd="Rahul@123",
                   db="rating")
    c = conn.cursor()
   
    c.execute("""INSERT INTO user (name, password, email) VALUES (%s, %s, %s)""",(uname,passwd,email))
    conn.commit()
    return "http://127.0.0.1:5000/"

@app.route("/index",methods=['POST','GET'])
def index():
    global session
    conn = MySQLdb.connect(host= "localhost",
                  user="rahul",
                  passwd="Rahul@123",
                  db="rating")
    c = conn.cursor()
    c.execute("select id,name,price,ROUND(avg_star,2) from product_details")
    data=c.fetchall()
    imgpath=[]
    for i in range(1,len(data)+1):
        imgpath.append("static/images/"+str(i)+".jpg")
    print(session["user_name"])
    User_name=session["user_name"]
    return render_template('index.html',data=data,imgpath=imgpath,User_name=User_name)



@app.route("/<name>",methods=['POST','GET'])
def next(name):
    global session
    conn = MySQLdb.connect(host= "localhost",
                user="rahul",
                passwd="Rahul@123",
                db="rating")
    c = conn.cursor()
    
    c.execute("""select id,price,ROUND(avg_star,2) from product_details where name=%s""",[str(name)])
    data1=c.fetchall()
    
    c.execute("""select user.name,rating.review,rating.rating_star from rating,product_details,user where user.id=rating.user_id and product_details.id=rating.product_id and product_details.name=%s""",[str(name)])
    data2=c.fetchall()
    imgpath="static/images/"+str(data1[0][0])+".jpg"
    User_name=session["user_name"]
    return render_template('complete.html',name=name,data1=data1,data2=data2,imgpath=imgpath,User_name=User_name)



# In[9]:

@app.route("/setting",methods=['POST','GET'])
def setting():
    global session
    User_name=session["user_name"]
    return render_template('setting.html',User_name=User_name)



@app.route("/updatepass",methods=['POST','GET'])
def updatepass():
    global session
    User_name=session["user_name"]
    message = request.get_json(force=True)
    email = message['emailtext']
    passwd = message['passwdtext']
    print(type(email))
    print(type(passwd))
    print(type(User_name))
    print(message)
    conn = MySQLdb.connect(host= "localhost",
                user="rahul",
                passwd="Rahul@123",
                db="rating")
    c = conn.cursor()
    query="""update user set email = %s,password = %s where name = %s"""
    data = (email,passwd,User_name)
    c.execute(query,data)
    conn.commit()
    data1=c.fetchall()
    return "http://127.0.0.1:5000/setting"



@app.route("/search",methods=['POST','GET'])
def search():
    global session
    User_name=session["user_name"]
    return render_template('search.html',User_name=User_name)



@app.route("/about")
def about():
    global session
    User_name=session["user_name"]
    return render_template('about.html',User_name=User_name)

@app.route("/find",methods=['POST','GET'])
def find():
    global session
    User_name=session["user_name"]

    message = request.get_json(force=True)
    query = message['searchBarval']
    
    conn = MySQLdb.connect(host= "localhost",
                user="rahul",
                passwd="Rahul@123",
                db="rating")
    c = conn.cursor()
    
    query=query + "%"
    print(query)
    c.execute("""select * from product_details where name like %s""",[str(query)])
    conn.commit()
    searchData=c.fetchall()
    print(searchData)
    return jsonify(searchData)


# In[10]:


@app.route("/postreview", methods=['POST','GET'])
def postreview():
    #Get the data posted from the form
    message = request.get_json(force=True)
    review = message['review']
    uname = message['uname']
    print(len(message))
    print(uname)
    print(review)
   
    product_name=message['product_name']

  
    

    #assign the review text to a variable
    a=[review]

    predict the outcome
    pred=model.predict(pad_sequences(tokenizer.texts_to_sequences(a),maxlen=100))
    value=rate(pred.item(0,0))

    

    #Save the review, user_id,product_id and predicted value to the database
    conn = MySQLdb.connect(host= "localhost",
                  user="rahul",
                  passwd="Rahul@123",
                  db="rating")
    c = conn.cursor()

    c.execute("""select id from user where name = %s""",[str(uname)])
    conn.commit()
    user_id=c.fetchone()
    
    c.execute("""select id from product_details where name = %s""",[str(product_name)])
    conn.commit()
    product_id=c.fetchone()
    

    c.execute(
      """INSERT INTO rating (product_id, user_id, review, rating_star)
      VALUES (%s, %s, %s, %s)""",(product_id, user_id , review, value ))
    
    conn.commit()
    
    c.execute("""select AVG(rating_star) from rating where product_id = %s""",(product_id))
    conn.commit()
    avg_stars=c.fetchone()

    
    c.execute("""update product_details set avg_star = %s where name = %s""",(avg_stars,product_name))
    conn.commit()
   
    return "http://127.0.0.1:5000/index"



if __name__ == "__main__":
    app.run(debug=True)




