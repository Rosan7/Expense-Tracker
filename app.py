from flask import Flask, request, jsonify
from uuid import uuid1, uuid4
import os, json, pytz

from datetime import date, datetime, timedelta

db = {}
db_filename = "db.json"
# Check whether db.json exists in the directory or not

if os.path.exists(db_filename):
    with open(db_filename, 'r') as f:
        db = json.load(f)
else:
    accessKey = str(uuid1())
    secretKey = str(uuid4())
    item_type = ["Food", "Beverages", "Clothing", "Stationaries", "Wearables", "Electronics Accessories"]
    db = {
        "accessKey": accessKey,
        "secretKey": secretKey,
        "item_type": item_type,
        "users": []
    }
    with open(db_filename, "w+") as f:
        json.dump(db, f, indent=4)
email_list = []
password_list = []
app = Flask(__name__)


@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        password = request.form['password']
        username = request.form['username']

        userDict = {
            "name": name,
            "email": email,
            "password": password,
            "username": username,
            "purchases": {}
        }

        if len(db["users"]) == 0 or email not in email_list:
            email_list.append(email)
            password_list.append(password)
            db["users"].append(userDict)
            with open(db_filename, "r+") as f:
                f.seek(0)
                json.dump(db, f, indent=4)
        else:
            return "Users Already Exists"
        return "User added Successfully"
    return "Error : Trying to access endpoint with wrong method"


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # name = request.form['name']
        email = request.form['email']

        password = request.form['password']
        user_idx = -1
        for user in db["users"]:

            if user["email"] == email and user["password"] == password:
                user_idx = db["users"].index(user)
                response = {
                    "message": "logged in successfully",
                    "user_index": user_idx
                }
                return response
            else:
                response = {
                    "message": "Wrong Credentials",
                    "User_idx": user_idx
                }

        return response


@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    if request.method == 'POST':
        user_idx = int(request.form["user_index"])
        item_name = request.form["item_name"]
        item_type = request.form["item_type"]
        item_price = request.form["item_price"]

        curr_date = str(date.today() - timedelta(1))
        curr_time = str(datetime.now(pytz.timezone("Asia/Kolkata")))

        item_dict = {
            "user_idx": user_idx,
            "item_name": item_name,
            "item_type": item_type,
            "item_price": item_price

        }
        purchased_dates = list(db["users"][user_idx]["purchases"].keys())
        if curr_date in purchased_dates:
            db["users"][user_idx]["purchases"][curr_date].append(item_dict)
        else:
            db["users"][user_idx]["purchases"][curr_date] = []
            db["users"][user_idx]["purchases"][curr_date].append(item_dict)
        with open(db_filename, "r+") as f:
            f.seek(0)
            json.dump(db, f, indent=4)

    return "Purchase Added Successfully"


@app.route('/get_all_purchases', methods=['GET'])
def get_all_purchases():

    user_idx = int(request.args["user_index"])
    # date = request.form['date']
    todo = str(date.today())
    # start_date = request.form["start_date"]
    # end_date = request.form["end_date"]
    # dates = list(db["users"][user_idx]["purchases"].keys())
    ans_list = []
    for items in db["users"][user_idx]["purchases"][todo]:
        ans_list.append(items)
    return jsonify({"purchases": ans_list})


@app.route('/get_all_purchases_of_dates', methods=['GET'])
def get_all_purchases_of_dates():
    data = request.json
    # print(data)
    # return "Dd"
    if request.method == 'GET':
        user_idx = int(data["user_index"])
        start_date = data["start_date"]
        end_date = data["end_date"]
        dates = list(db["users"][user_idx]["purchases"].keys())
        purchase_dict = {}
        for date in dates:
            if start_date <= date <= end_date:
                purchase_dict[date] = db["users"][user_idx]["purchases"][date]
                # for items in db["users"][user_idx]["purchases"][date]:

        return purchase_dict



@app.route('/get_average_amount', methods=['POST'])
def get_average_amount():
    if request.method == 'POST':
        user_idx = int(request.form['user_index'])
        dates = list(db["users"][user_idx]["purchases"].keys())
        sum_total = 0
        count = 0
        for date in dates:
            for data in db["users"][user_idx]["purchases"][date]:
                sum_total += int(data["item_price"])
                count += 1
        average = sum_total / count
        return jsonify({'average': average})


@app.route('/get_most_purchased_item', methods=['POST'])
def get_most_purchased_item():
    item_dict = {}
    if request.method == 'POST':
        user_idx = int(request.form["user_index"])
        dates = list(db["users"][user_idx]["purchases"].keys())
        for date in dates:
            for item in db["users"][user_idx]["purchases"][date]:
                if item["item_name"] not in item_dict:
                    item_dict[item["item_name"]] = 1
                else:
                    item_dict[item["item_name"]] += 1

        frequency = 0

        for key, value in item_dict.items():
            if value > frequency:
                frequency = value
                most_purchased = key
        return jsonify({"most_purchased": most_purchased})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5000", debug=True)
