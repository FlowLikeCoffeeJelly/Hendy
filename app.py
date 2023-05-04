from flask import Flask, render_template
import mysql.connector
import time
import threading
import mpld3
from mysql.connector import pooling
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors
import mpld3
import io
import json
import mysql.connector
import time
import threading
from mysql.connector import pooling
import base64
from io import BytesIO

import io
import base64
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify


from flask import jsonify

seven_day_ago = int(time.time())
app = Flask(__name__)
one_days_ago = int(time.time()) - (24 * 60 * 60 * 7)
seven_days_ago = int(time.time()) - (24 * 60 * 60 * 7)
dbconfig = {
    "host": "51.79.65.208",
    "user": "csnpricedata",
    "password": "!AdKSVk#w~X&5_fwd\C{",
    "database": "stoneworks_rath_csn",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=5, **dbconfig)
Mode = 1
def calculate_master_avg_price(item_id):
    #cnx = get_connection()
    cursor = cnx.cursor()

    one_day_ago = int(time.time()) - (24 * 60 * 60 * 7) # actually 3 days ago
    query = f"SELECT Amount, Quantity FROM csnUUID WHERE Itemid = '{item_id}' AND Time >= {one_day_ago} AND Mode = {Mode}"
    cursor.execute(query)

    prices = []
    for (amount, quantity) in cursor:
        avg_price = amount / quantity
        prices.append(avg_price)

    
    try:
        master_avg_price = sum(prices) / len(prices)
    except ZeroDivisionError:
        master_avg_price = 0
        print("zero")
    cursor.close()
    
    
    return master_avg_price
def get_connection():
    """ connection pool."""
    print("getting connection")
    return pool.get_connection()
cnx = get_connection()
print("connection gogte")
def get_highest_price(item_id):
    cursor = cnx.cursor()


    one_day_ago = int(time.time()) - (24 * 60 * 60 * 7)
    query = "SELECT MAX(Amount/Quantity) FROM csnUUID WHERE Mode = "+str(Mode)+" AND Itemid = '{}' AND Time >= {}".format(item_id, one_day_ago)
    cursor.execute(query)

    highest_price = cursor.fetchone()[0]

    cursor.close()
    

    return highest_price
def get_lowest_price(item_id):
    #cnx = get_connection()
    cursor = cnx.cursor()

    
    one_day_ago = int(time.time()) - (24 * 60 * 60 * 7)
    query = f"SELECT MIN(Amount/Quantity) FROM csnUUID WHERE Mode = {Mode} AND Itemid = '{item_id}' AND Time >= {one_day_ago}"
    cursor.execute(query)


    lowest_price = cursor.fetchone()[0]


    cursor.close()
    


    return lowest_price

#
maps = {}
MAPlist = {}
MHPlist = {}
MLPlist = {}
cursor = cnx.cursor()
cursor.execute(f"SELECT DISTINCT Itemid FROM csnUUID WHERE MODE = {Mode} AND Time >= {seven_days_ago} ")
import json

import os
import json

def save_dictionaries_to_file():
    with open("data.json", "w") as f:
        data = {"MAPlist": MAPlist, "MLPlist": MLPlist, "MHPlist": MHPlist}
        json.dump(data, f)

def load_dictionaries_from_file():
    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:# w  write read
            data = {"MAPlist": {}, "MLPlist": {}, "MHPlist": {}}
            json.dump(data, f)

    with open("data.json", "r") as f:
        data = json.load(f)
        return data["MAPlist"], data["MLPlist"], data["MHPlist"]

def update_dictionaries_with_new_entries():
    global MAPlist, MLPlist, MHPlist

    
    MAPlist, MLPlist, MHPlist = load_dictionaries_from_file()

    
   

    

    item_ids = [item_id[0] for item_id in cursor.fetchall()]
    cursor.close()
    for item_id in item_ids:
        MAP = calculate_master_avg_price(item_id)
        print(f"doing test calc of MAP or {item_id}")    
        if str(item_id) not in MAPlist or MAPlist[item_id] != MAP:
            #MAP = calculate_master_avg_price(item_id)
            MHP = get_highest_price(item_id)
            MLP = get_lowest_price(item_id)

            if MAP is not None:
                MAPlist[item_id] = MAP
          
            if MHP is not None:
                MHPlist[item_id] = MHP

            if MLP is not None:
                MLPlist[item_id] = MLP
                print(f"{item_id} done lol")

            
            save_dictionaries_to_file()

    

def populate_table():
    update_dictionaries_with_new_entries()

from flask import render_template_string



@app.route('/load_graph', methods=['GET', 'POST'])
def load_graph():
    item_id = request.json['item_id']  # Get the item_id from request
    image_base64 = generate_graph(item_id)
    return jsonify({'image_base64': image_base64})




from io import BytesIO

def generate_graph(item_id):
    cnx = get_connection()

    def calculate_master_avg_price(item_id, x, cnx):
        cursor = cnx.cursor()

        query = f"SELECT Amount, Quantity FROM csnUUID WHERE Mode = {Mode} AND Itemid = '{item_id}' AND Time BETWEEN UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL {x} DAY)) AND UNIX_TIMESTAMP(DATE_ADD(DATE_SUB(NOW(), INTERVAL {x} DAY), INTERVAL 1 DAY))"
        cursor.execute(query)

        prices = []
        for (amount, quantity) in cursor:
            if quantity == 0:
                continue
            avg_price = amount / quantity
            prices.append(avg_price)

        master_avg_price = sum(prices) / len(prices) if len(prices) > 0 else 0

        cursor.close()

        return master_avg_price

    daystoshow = 15
    x_range = range(1, daystoshow)
    x_values = []
    avg_prices = []

    for x in x_range:
        avg_price = calculate_master_avg_price(item_id, x, cnx)
        if avg_price:
            x_values.append(x)
            avg_prices.append(avg_price)

    cnx.close()

    fig, ax = plt.subplots()
    ax.invert_xaxis()
    ax.plot(x_values, avg_prices, color='green')
    ax.fill_between(x_values, avg_prices, color='lightgreen')
    ax.set_xlabel('Within x Days Ago')
    ax.set_ylabel('Price Per 1 Item, $')
    ax.set_title(item_id.upper(), fontweight='bold', color='green')
    ax.yaxis.set_major_formatter('${x:,.3f}')

    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    png_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return png_image




'''username=input("enter username")
import requests
url = f'https://api.mojang.com/users/profiles/minecraft/{username}?'
response = requests.get(url)
uuid = response.json()['id']
print(uuid)
'''





print("past defeintions")

populate_table()
print("done gathering data")





@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html', MAPlist=MAPlist, MLPlist=MLPlist, MHPlist=MHPlist)

@app.route("/price_calculator")
def price_calculator():
    return render_template('price_calculator.html', MAPlist=MAPlist)

if __name__ == "__main__":
    app.run()
