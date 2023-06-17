from flask import Flask, jsonify, request, redirect
import random

app = Flask(__name__)

applications = ["http://localhost:8080", "http://localhost:8081", "http://localhost:8082"]

@app.route('/loadbalancer/apps', methods=['GET', 'POST'])
def manage_applications():

    global applications

    if request.method == 'GET':

        return jsonify({"data": {"applications": applications}}), 200
    
    elif request.method == 'POST':

        if not request.json or not 'applications' in request.json:
            return jsonify({'error': 'Bad request'}), 400

        applications = request.json['applications']

        return jsonify({"data": {"applications": applications}}), 200
    
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def load_balancer(path):

    global applications

    app = random.choice(applications)

    return redirect(f'{app}/{path}', 307)
    