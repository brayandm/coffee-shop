from flask import Flask, jsonify, request, redirect
import logging
import requests
import boto3
import os
import json

s3_client = boto3.client(
    "s3",
    region_name=os.environ.get("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)

applications = []

try:
    response = s3_client.get_object(
        Bucket=os.environ.get("AWS_BUCKET_NAME"), Key="applications.json"
    )
    content = response["Body"].read().decode("utf-8")
    applications = json.loads(content)

except:
    s3_client.put_object(
        Body=json.dumps(
            [
                {
                    "guestUrl": "http://localhost:8081",
                    "healthCheckUrl": "http://server1.test",
                },
                {
                    "guestUrl": "http://localhost:8082",
                    "healthCheckUrl": "http://server2.test",
                },
                {
                    "guestUrl": "http://localhost:8083",
                    "healthCheckUrl": "http://server3.test",
                },
            ]
        ),
        Bucket=os.environ.get("AWS_BUCKET_NAME"),
        Key="applications.json",
    )

    applications = [
        {
            "guestUrl": "http://localhost:8081",
            "healthCheckUrl": "http://server1.test",
        },
        {
            "guestUrl": "http://localhost:8082",
            "healthCheckUrl": "http://server2.test",
        },
        {
            "guestUrl": "http://localhost:8083",
            "healthCheckUrl": "http://server3.test",
        },
    ]

round_robin = {"index": 0}


def health_check(application):
    try:
        response = requests.get(f"{application}/v1/ping")

        if response.status_code == 200:
            return True

        return False

    except:
        return False


@app.route("/loadbalancer/apps", methods=["GET", "POST"])
def manage_applications():
    global applications, round_robin

    if request.method == "GET":
        return jsonify({"data": {"applications": applications}}), 200

    elif request.method == "POST":
        if not request.json or not "applications" in request.json:
            return jsonify({"error": "Bad request"}), 400

        applications = request.json["applications"]

        s3_client.delete_object(
            Bucket=os.environ.get("AWS_BUCKET_NAME"), Key="applications.json"
        )

        s3_client.put_object(
            Body=json.dumps(applications),
            Bucket=os.environ.get("AWS_BUCKET_NAME"),
            Key="applications.json",
        )

        round_robin["index"] = 0

        return jsonify({"data": {"applications": applications}}), 200


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def load_balancer(path):
    global applications, round_robin

    if len(applications) == 0:
        return jsonify({"error": "No applications available"}), 500

    application = None

    for _ in range(len(applications)):
        if health_check(applications[round_robin["index"]]["healthCheckUrl"]):
            application = applications[round_robin["index"]]["guestUrl"]
            round_robin["index"] = (round_robin["index"] + 1) % len(applications)
            break

        round_robin["index"] = (round_robin["index"] + 1) % len(applications)

    if application is None:
        return jsonify({"error": "No applications available"}), 500

    app.logger.info(f"Forwarding request to {application}/{path}")

    return redirect(f"{application}/{path}", 307)
