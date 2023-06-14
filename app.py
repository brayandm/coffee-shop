from flask import Flask, Blueprint, jsonify, request
import base64

app = Flask(__name__)

apiv1 = Blueprint('v1', __name__, url_prefix='/v1')

database = {
    "user1": {
        "is_admin": True,
        "password": "password1",
        "favorite_coffee": "cappuccino"
    },
    "user2": {
        "is_admin": False,
        "password": "password2",
        "favorite_coffee": "latte"
    },
    "user3": {
        "is_admin": False,
        "password": "password3",
        "favorite_coffee": "espresso"
    },
    "user4": {
        "is_admin": False,
        "password": "password4",
        "favorite_coffee": "mocha"
    },
    "user5": {
        "is_admin": False,
        "password": "password5",
        "favorite_coffee": "americano"
    }
}

def get_user(auth_header):
    if not auth_header or not auth_header.startswith('Basic '):
        return None
    auth_string = base64.b64decode(auth_header[6:]).decode('utf-8')
    user, password = auth_string.split(':')

    if user not in database or password != database[user]['password']:
        return None

    return user

def is_admin(user):
    return database[user]['is_admin']

@apiv1.route("/ping",  methods=['GET'])
def hello_world():
    return "pong"

@apiv1.route('/coffee/favourite', methods=['GET', 'POST'])
def favourite_coffee():

    user = get_user(request.headers.get('Authorization'))

    if user is None:
        return jsonify({'error': 'Unauthenticated'}), 401
    
    if request.method == 'GET':

        return jsonify({"data": {"favouriteCofee": database[user]["favorite_coffee"]}}), 200
    
    elif request.method == 'POST':

        if not request.json or not 'favouriteCofee' in request.json:
            return jsonify({'error': 'Bad request'}), 400

        database[user]["favorite_coffee"] = request.json['favouriteCofee']

        return jsonify({"data": {"favouriteCofee": database[user]["favorite_coffee"]}}), 200
    
@apiv1.route('admin/coffee/favourite/leadeboard', methods=['GET'])
def top_favourite_coffee():

    user = get_user(request.headers.get('Authorization'))

    if user is None or not is_admin(user):
        return jsonify({'error': 'Unauthenticated'}), 401

    coffee_count = {}

    for user in database:
        coffee = database[user]["favorite_coffee"]
        if coffee in coffee_count:
            coffee_count[coffee] += 1
        else:
            coffee_count[coffee] = 1

    top_coffee = sorted(coffee_count, key=coffee_count.get, reverse=True)[:3]

    return jsonify({"data": {"top3": top_coffee}}), 200



app.register_blueprint(apiv1)