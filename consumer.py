from flask import Flask, Blueprint, jsonify, request
import os
import boto3

sqs_client = boto3.client(
    "sqs",
    region_name=os.environ.get("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

app = Flask(__name__)

apiv1 = Blueprint("v1", __name__, url_prefix="/v1")


@apiv1.route("/ping", methods=["GET"])
def hello_world():
    return "consumer response: pong"


app.register_blueprint(apiv1)
