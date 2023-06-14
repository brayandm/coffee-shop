from flask import Flask, Blueprint

app = Flask(__name__)

apiv1 = Blueprint('v1', __name__, url_prefix='/v1')

@apiv1.route("/ping",  methods=['GET'])
def hello_world():
    return "pong"

app.register_blueprint(apiv1)