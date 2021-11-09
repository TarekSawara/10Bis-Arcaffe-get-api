import json
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# POPULAR_DISHES = "Popular Dishes"
# SALADS = "Salads"
# SANDWICHES = "Sandwiches"
DESSERTS = "Desserts"
PIZZAS = "Pizzas"
DRINKS = "Drinks"

DISHES_KEY = 'dishList'
CATEGORY_NAME_KEY = 'categoryName'
CATEGORIES_LIST_KEY = 'categoriesList'
DISH_ID = 'dishId'
DISH_NAME = 'dishName'
DISH_DESCRIPTION = 'dishDescription'
DISH_PRICE = 'dishPrice'

import flask
from flask import request, abort, send_from_directory
from flask_cors import CORS
import requests

app = flask.Flask(__name__)
CORS(app)

app.config["DEBUG"] = True
# app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY

SCHEDULER_INTERVAL_SECONDS = 24 * 60 * 60
my_data = None


def fetch_data_from_source():
    response = requests.get('https://tenbis-static.azureedge.net/restaurant-menu/19156_en', timeout=2.50)
    if response.status_code == 200:
        global my_data
        print("data in database updated successfully!")
        my_data = response

        pass
    else:
        print(f"fetching data from server Failed with error code '{response.status_code}'('{response.reason}')")
        print("keeping old data in database")


scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_data_from_source, trigger="interval", seconds=SCHEDULER_INTERVAL_SECONDS)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Dish:
    def __init__(self, dish_dict):
        self.dish_dict = dish_dict
        self.dish_dict_compact = {DISH_ID: dish_dict[DISH_ID], DISH_NAME: dish_dict[DISH_NAME],
                                  DISH_DESCRIPTION: dish_dict[DISH_DESCRIPTION], DISH_PRICE: dish_dict[DISH_PRICE]}


def read_json(file_path):
    with open(file_path, "r") as json_file:
        content = json.load(json_file)
    return content


def get_category_dict(json_content, category_name):
    """
    This function assumes only one category of each type
    :return: a filled dictionary for the requested category if it exists, None if the category wasnt found
    """
    requested_category_dict = None
    for category_dict in json_content[CATEGORIES_LIST_KEY]:
        if category_dict[CATEGORY_NAME_KEY].lower() == category_name.lower():
            requested_category_dict = category_dict
            break
    else:
        print(f"{category_name} weren't found on the menu")
    return requested_category_dict


def get_dishes(json_content, category_name):
    desserts = get_category_dict(json_content, category_name=category_name)
    dishes = [Dish(dish_dict).dish_dict_compact for dish_dict in desserts[DISHES_KEY]]
    return dishes


def getByProdcut(catagory, drink_id=None):
    try:
        global my_data
        if (my_data == None):
            fetch_data_from_source()

        res = get_dishes(my_data.json(), catagory)
        if (drink_id):
            for drink in res:
                if drink['dishId'] == int(drink_id):
                    return json.dumps(drink), 200
            return "Product ID not Found", 401
        return json.dumps(res), 200
    except:
        return "", 400


@app.route("/drinks", methods=["GET"])
def GetRestaurantDrinks():
    return getByProdcut(catagory=DRINKS)


@app.route("/drink/<id>", methods=["GET"])
def GetRestaurantDrink(id):
    if (id):
        return getByProdcut(catagory=DRINKS, drink_id=id)
    return "Product ID not Found", 401


@app.route("/pizzas", methods=["GET"])
def GetRestaurantPizzas():
    return getByProdcut(catagory=PIZZAS)


@app.route("/pizza/<id>", methods=["GET"])
def GetRestaurantPizza(id):
    if (id):
        return getByProdcut(catagory=PIZZAS, drink_id=id)
    return "Product ID not Found", 401


@app.route("/desserts", methods=["GET"])
def GetRestaurantDeserts():
    return getByProdcut(catagory=DESSERTS)


@app.route("/dessert/<id>", methods=["GET"])
def GetRestaurantDesert(id):
    if (id):
        return getByProdcut(catagory=DESSERTS, drink_id=id)
    return "Product ID not Found", 401


@app.route("/order", methods=["POST"])
def GetOrder():
    body = request.json
    amount = 0
    for category in body:
        func_use = ''
        for id in body[category]:
            res = getByProdcut(category.lower(), id)
            if res[1] == 200:
                amount += json.loads(res[0])['dishPrice']
    if amount:
        return json.dumps({"price": amount}), 200


app.run(debug=False)
