import os
import boto3
import time

sqs_client = boto3.client(
    "sqs",
    region_name=os.environ.get("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

if __name__ == "__main__":
    while True:
        queue_url = os.environ.get("AWS_SQS_QUEUE_URL")

        response = sqs_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=5
        )

        if "Messages" in response:
            for message in response["Messages"]:
                print("Message body:", message["Body"])

                print("Processing message:", message["MessageId"])

                time.sleep(3)

                print("Deleting message:", message["MessageId"])

                sqs_client.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
        else:
            print("No messages available")
