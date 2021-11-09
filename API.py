import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import flask
from flask import request, abort, send_from_directory
from flask_cors import CORS
import requests

# POPULAR_DISHES = "Popular Dishes"
# SALADS = "Salads"
# SANDWICHES = "Sandwiches"
DESSERTS = "Desserts"
PIZZAS = "Pizzas"
DRINKS = "Drinks"
# ------
DISHES_KEY = 'dishList'
CATEGORY_NAME_KEY = 'categoryName'
CATEGORIES_LIST_KEY = 'categoriesList'
DISH_ID = 'dishId'
DISH_NAME = 'dishName'
DISH_DESCRIPTION = 'dishDescription'
DISH_PRICE = 'dishPrice'
# -----
COMPACT_DISH_KEYS = {DISH_ID, DISH_NAME, DISH_DESCRIPTION, DISH_PRICE}
SCHEDULER_INTERVAL_SECONDS = 24 * 60 * 60

my_data = None  # this variable gets updated periodically with data from the server .
app = flask.Flask(__name__)
CORS(app)


class Dish:
    """ This class holds the dictionary info of a given dish"""
    def __init__(self, dish_dict):
        """

        :param dish_dict: a dictionary object containing atleast 4 items :
                The items are (dish-id, dish-name, dish-price and dish-description)

        """
        self.dish_dict = dish_dict
        if len(COMPACT_DISH_KEYS - dish_dict.keys()) == 0:
            self.dish_dict_compact = {DISH_ID: dish_dict[DISH_ID], DISH_NAME: dish_dict[DISH_NAME],
                                      DISH_DESCRIPTION: dish_dict[DISH_DESCRIPTION], DISH_PRICE: dish_dict[DISH_PRICE]}
        else:
            print(f"Dish doesnt have proper structure (missing keys), the dish provided is: '{dish_dict}'")
            self.dish_dict_compact = {}

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


def get_category_dict(json_content, category_name):
    """
    This function assumes at most one category of each type exists in json_content
    :return: a filled dictionary for the requested category if it exists, None if the category wasn't found
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
    """

    :param json_content: a dictionary holding the data to extract dishes from
    :param category_name: a string of any of the categories recognised by our app ("Desserts", "Pizzas", "Drinks")
    :return: a list of "compact" dictionaries of dishes, compact means it only contains (name, price, id , description)

    *note* the return list could contain empty dictionaries if the provided 'dish_dict' to class Dish wasn't valid.
    """
    category_dishes = get_category_dict(json_content, category_name=category_name)
    dishes_compact = [Dish(dish_dict).dish_dict_compact for dish_dict in category_dishes[DISHES_KEY]]
    return dishes_compact


def getByProdcut(category, product_id=None):
    """

    :param category: a string of any of the categories recognised by our app ("Desserts", "Pizzas", "Drinks")
    :param product_id: a string referring to which product from category 'category' and id 'id' to get when
    provided, otherwise (when this parameter is None), we get all of the items in that category, we don filter by ids.
    :return: a tuple, (request response as JSON formatted string, request response status code)
    """
    try:
        global my_data
        if not my_data:
            # if the data we have is empty / not initialized, fetch again
            fetch_data_from_source()

        res = get_dishes(my_data.json(), category)
        if product_id:
            for dish in res:
                if dish[DISH_ID] == int(product_id):
                    return json.dumps(dish), 200
            return "Product ID not Found", 401
        return json.dumps(res), 200
    except:
        return "", 400


@app.route("/drinks", methods=["GET"])
def GetRestaurantDrinks():
    return getByProdcut(category=DRINKS)


@app.route("/drink/<id>", methods=["GET"])
def GetRestaurantDrink(id):
    if (id):
        return getByProdcut(category=DRINKS, product_id=id)
    return "Product ID not Found", 401


@app.route("/pizzas", methods=["GET"])
def GetRestaurantPizzas():
    return getByProdcut(category=PIZZAS)


@app.route("/pizza/<id>", methods=["GET"])
def GetRestaurantPizza(id):
    if (id):
        return getByProdcut(category=PIZZAS, product_id=id)
    return "Product ID not Found", 401


@app.route("/desserts", methods=["GET"])
def GetRestaurantDeserts():
    return getByProdcut(category=DESSERTS)


@app.route("/dessert/<id>", methods=["GET"])
def GetRestaurantDesert(id):
    if (id):
        return getByProdcut(category=DESSERTS, product_id=id)
    return "Product ID not Found", 401


@app.route("/order", methods=["POST"])
def GetOrder():
    body = request.json
    amount = 0
    for category in body:
        for id in body[category]:
            res = getByProdcut(category, id)
            if res[1] == 200:
                amount += json.loads(res[0])['dishPrice']
    if amount:
        return json.dumps({"price": amount}), 200


def fetch_data_from_source():
    """
    when this function is called, it attempts to populate the variable 'my_data' in which all of our data is stored
    it prints messages to reflect the state of the response we get.
    """
    response = requests.get('https://tenbis-static.azureedge.net/restaurant-menu/19156_en', timeout=2.50)
    if response.status_code == 200:
        global my_data
        my_data = response
        print("data in database updated successfully!")
    else:
        print(f"fetching data from server Failed with error code '{response.status_code}'('{response.reason}')")
        print("keeping old data in database")


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_data_from_source, trigger="interval", seconds=SCHEDULER_INTERVAL_SECONDS)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=False)