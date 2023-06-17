from flask import Flask, jsonify, request, redirect
import requests

app = Flask(__name__)

applications = [
    {
        "guestUrl": "http://localhost:8080",
        "healthCheckUrl": "server1.test"
    },
    {
        "guestUrl": "http://localhost:8081",
        "healthCheckUrl": "server2.test"
    },
    {
        "guestUrl": "http://localhost:8082",
        "healthCheckUrl": "server3.test"
    }
]

round_robin = {
    "index": 0
}

def health_check(application):

    return True

    try:

        response = requests.get(f'{application}/v1/ping')

        if response.status_code == 200:

            return True
        
        return False
    
    except:

        return False
    

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

    global applications, round_robin

    if len(applications) == 0:

        return jsonify({'error': 'No applications available'}), 500
    
    app = None
    
    for _ in range(len(applications)):

        if health_check(applications[round_robin["index"]]["healthCheckUrl"]):
            app = applications[round_robin["index"]]["guestUrl"]
            round_robin["index"] = (round_robin["index"] + 1) % len(applications)
            break

        round_robin["index"] = (round_robin["index"] + 1) % len(applications)

    
    if app is None:
            
            return jsonify({'error': 'No applications available'}), 500

    
    return redirect(f'{app}/{path}', 307)
    