import base64

import boto3
from flask import Flask, request
import time
import csv

# Provide information
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Response = dict()
aws_access_key_id = 'aws_access_key_id'
aws_secret_access_key = 'aws_secret_access_key'
region_name = 'us-east-1'
request_queue_url = 'request_queue_url'
response_queue_url = 'response_queue_url'
endpoint_url = 'https://sqs.us-east-1.amazonaws.com'
input_bucket_name = 'input_bucket_name'
output_bucket_name = 'output_bucket_name'
sqs = boto3.client('sqs', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                   endpoint_url=endpoint_url, region_name=region_name)
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                         region_name=region_name)
s3 = boto3.resource(
    service_name='s3',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
ec2_app = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
ec2_app_resources = ec2_app.resource('ec2', 'us-east-1')
ec2_app_client = ec2_app.client('ec2', 'us-east-1')
num_msg_answered = 0
running_instances = []


# Disable caching for all responses
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/', methods=["POST"])
async def uploadImage():
    if 'inputFile' not in request.files:
        return "No inputFile provided", 400

    input_file = request.files['inputFile']
    if input_file.filename == '':
        return "No selected file", 400

    filename, _ = input_file.filename.rsplit('.', 1)
    filename += ".jpg"
    try:
        byteform = base64.b64encode(input_file.read())
        value = str(byteform, 'utf-8')
        str_byte = filename + " " + value
        sqs.send_message(
            QueueUrl=request_queue_url,
            MessageBody=(
                str_byte
            )
        )
        # print(numberOfMsgsInResQ())
        output = await getResponse(filename)

        result_message = f"{filename}:{output}"
        return result_message

    except Exception as e:
        # print(str(e))
        return "Something went wrong " + str(e)


async def getResponse(image):
    result = ""
    while True:

        if image in Response.keys():
            output = Response[image]
            del Response[image]
            return output

        response = sqs.receive_message(
            QueueUrl=response_queue_url,
            MaxNumberOfMessages=10,
            AttributeNames=['All'],
            MessageAttributeNames=[
                'All'
            ],
        )

        if 'Messages' in response:
            msgs = response['Messages']
            for msg in msgs:
                msg_body = msg['Body']
                Response_image = msg_body.split(" ")[0]
                Response[Response_image] = msg_body.split(" ")[1]
                # print("Response_image: ",Response[Response_image])

                receipt_handle = msg['ReceiptHandle']
                sqs.delete_message(
                    QueueUrl=response_queue_url,
                    ReceiptHandle=receipt_handle
                )
                if Response_image == image:
                    output = Response[Response_image]
                    del Response[Response_image]
                    return output


def numberOfMsgsInRespQ():
    response = sqs.get_queue_attributes(
        QueueUrl=response_queue_url,
        AttributeNames=[
            'ApproximateNumberOfMessages',
            'ApproximateNumberOfMessagesNotVisible'
        ]
    )
    return int(response['Attributes']['ApproximateNumberOfMessages'])

def numberOfMsgsInResQ():
    response = sqs.get_queue_attributes(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'ApproximateNumberOfMessages',
            'ApproximateNumberOfMessagesNotVisible'
        ]
    )
    return int(response['Attributes']['ApproximateNumberOfMessages'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
