#!/usr/bin/env python
from flask import jsonify
from flask import Flask, render_template, request
import json
import time
import datetime
from database_utils import getConn
import os,base64
import logging
from time import gmtime
import base64




app = Flask(__name__)



@app.route('/')
def display_menu():
    return render_template('menu.html')

@app.route('/filter/genre', methods=['GET', 'POST'])
def filter_by_id_route():
    if request.method == 'POST':
        # Validate myid
        try:
            myid = int(request.form['myid'])
            if 1 <= myid <= 10:
                print("Valid request..")
            else:
                print("ID must be between 1 and 10")
        
        except ValueError:
            print("ID must be a valid integer..")


        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_ROOT_PASSWORD'),
        db=os.environ.get('MYSQL_DATABASE')
        cnx = getConn(host,user,password,db)
        cur = cnx.cursor()
        query = """select genre_name from genre where id=%s;"""
        cur.execute(query,(myid,))
        rows = cur.fetchall()
        dict_data = []
        for a in rows:
           dict_data.append({'genre':a})
       
        return jsonify(dict_data)
    return render_template('filter_genre.html')


# @app.route('/quit')
# def quit():
#     return "Goodbye!"

app.run(debug=True)
