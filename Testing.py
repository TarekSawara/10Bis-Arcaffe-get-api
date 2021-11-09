# Suggest a simple way to demonstrate the service functionality (CLI, unit tests, other)

import requests
import json

HOST = "http://127.0.0.1"
PORT = "5000"
url = "{}:{}".format(HOST, PORT)


# POST /order - receives an order and returns its total price.
def order_example():
    payload = json.dumps({
        "drinks": [
            2055846,
            2055841
        ],
        "desserts": [
            2055837
        ],
        "pizzas": [
            2055832
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url + "/order", headers=headers, data=payload)

    print(response.text)

def get_drinks_example():
    import requests
    import json

    payload = {}
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url + "/drinks", headers=headers, data=payload)

    print(response.text)


def get_drink_by_id_example(id):
    import requests
    import json

    payload = {}
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url + "/drink/{}".format(id), headers=headers, data=payload)

    print(response.text)


print("Example for purchasing, expected to return json of price as key and amount in float as value")
print("Result: ")
order_example()
print("=========")
print("Example for getting drinks data , expected to return json of all drinks in Arcaffe menu ")
print("Result: ")
get_drinks_example()
print("=========")
print("Example for getting drink data of specific id, expected to return json of "
      "the id, name, description and price of all drinks")
print("Result: ")
get_drink_by_id_example(2055841)
print("=========")
print("Example for getting drink data of specific id, expected to return not found message if id is not found")
print("Result: ")
get_drink_by_id_example(205584)
print("=========")

