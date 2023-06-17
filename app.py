from flask import Flask, Blueprint, jsonify, request
import base64
import os
import mysql.connector

app = Flask(__name__)

apiv1 = Blueprint('v1', __name__, url_prefix='/v1')

config = {
    'user': os.environ.get('DB_USERNAME'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_DATABASE'),
    'port': '3306'
}

conn = mysql.connector.connect(**config)

cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, is_admin BOOLEAN, username VARCHAR(255), password VARCHAR(255), favorite_coffee VARCHAR(255))")

seed = [
    {
        "id" : 1,
        "username": "user1",
        "is_admin": True,
        "password": "password1",
        "favorite_coffee": "cappuccino"
    },
    {
        "id" : 2,
        "username": "user2",
        "is_admin": False,
        "password": "password2",
        "favorite_coffee": "latte"
    },
    {
        "id" : 3,
        "username": "user3",
        "is_admin": False,
        "password": "password3",
        "favorite_coffee": "espresso"
    },
    {
        "id" : 4,
        "username": "user4",
        "is_admin": False,
        "password": "password4",
        "favorite_coffee": "mocha"
    },
    {
        "id" : 5,
        "username": "user5",
        "is_admin": False,
        "password": "password5",
        "favorite_coffee": "americano"
    }
]

for user in seed:

    cursor.execute("SELECT * FROM users WHERE id = %s", (user['id'],))

    if cursor.fetchone() is None:

        cursor.execute("INSERT INTO users (is_admin, username, password, favorite_coffee) VALUES (%s, %s, %s, %s)", (user['is_admin'], user['username'], user['password'], user['favorite_coffee']))

        conn.commit()


def get_user(auth_header):

    cursor = conn.cursor()

    if not auth_header or not auth_header.startswith('Basic '):
        return None
    auth_string = base64.b64decode(auth_header[6:]).decode('utf-8')
    user, password = auth_string.split(':')

    cursor.execute("SELECT * FROM users WHERE username = %s", (user,))

    data = cursor.fetchone()

    if data is None or password != data[3]:
        return None

    return user

def is_admin(user):

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (user,))

    return cursor.fetchone()[1]

@apiv1.route("/ping",  methods=['GET'])
def hello_world():
    return "server " + os.environ.get('SERVER_ID') + " response: pong"

@apiv1.route('/coffee/favourite', methods=['GET', 'POST'])
def favourite_coffee():

    cursor = conn.cursor()

    user = get_user(request.headers.get('Authorization'))

    if user is None:
        return jsonify({'error': 'Unauthenticated'}), 401
    
    if request.method == 'GET':

        cursor.execute("SELECT * FROM users WHERE username = %s", (user,))

        data = cursor.fetchone()

        return jsonify({"data": {"favouriteCofee": data[4]}}), 200
    
    elif request.method == 'POST':

        if not request.json or not 'favouriteCofee' in request.json:
            return jsonify({'error': 'Bad request'}), 400

        cursor.execute("UPDATE users SET favorite_coffee = %s WHERE username = %s", (request.json['favouriteCofee'], user))

        conn.commit()

        cursor.execute("SELECT * FROM users WHERE username = %s", (user,))

        data = cursor.fetchone()

        return jsonify({"data": {"favouriteCofee": data[4]}}), 200
    
    
@apiv1.route('admin/coffee/favourite/leadeboard', methods=['GET'])
def top_favourite_coffee():

    cursor = conn.cursor()

    user = get_user(request.headers.get('Authorization'))

    if user is None or not is_admin(user):
        return jsonify({'error': 'Unauthenticated'}), 401

    coffee_count = {}

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    for user in users:
        coffee = user[4]
        if coffee in coffee_count:
            coffee_count[coffee] += 1
        else:
            coffee_count[coffee] = 1

    top_coffee = sorted(coffee_count, key=coffee_count.get, reverse=True)[:3]

    return jsonify({"data": {"top3": top_coffee}}), 200



app.register_blueprint(apiv1)