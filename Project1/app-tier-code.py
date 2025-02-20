import asyncio
import base64
import time
import boto3
import os

## Provide proper paths
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


def receiveMessages():
    #print("receiving message")
    response = sqs.receive_message(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=30,
    )
    if 'Messages' in response:
        return response['Messages']
    else:
        time.sleep(1)
        #await asyncio.sleep(1)
        return receiveMessages()


def sendMessageToRespQ(fileName, result):
    #print("sending message")
    resp = sqs.send_message(
        QueueUrl=response_queue_url,
        MessageBody=(
                fileName + " " + result
        )
    )


def deleteMessage(receipt_handle):
    #print("deleting message")
    sqs.delete_message(
        QueueUrl=request_queue_url,
        ReceiptHandle=receipt_handle
    )


def uploadToS3InputBucket(FileName, ImagePath):
    #print("uploading input message")
    s3.Object(input_bucket_name, FileName).upload_file(Filename=ImagePath)


def uploadToS3OutputBucket(FileName, OutputFile):
    #print("uploading output message")
    s3.Object(output_bucket_name, FileName).upload_file(Filename=OutputFile)


def init():
    message = receiveMessages()[0]
    #print(message)
    receipt_handle = message['ReceiptHandle']
    fileName, encodedMssg = message['Body'].split()
    #print(fileName)
    msg_value = bytes(encodedMssg, 'utf-8')
    with open("outputFile.bin", "wb") as file:
        file.write(msg_value)
    file = open('outputFile.bin', 'rb')
    byte = file.read()
    file.close()
    qp = base64.b64decode(byte)
    with open("Imagefile", "wb") as imageFile:
        imageFile.write(qp)

    #print("Filename:", fileName)
    out = os.popen("python3 face_recognition.py Imagefile")
    result = out.read().strip()
    #print("Result:", result)
    ClassificationResultFile = open("ClassificationResult", "w")
    ClassificationResultFile.write(result)
    ClassificationResultFile.close()

    uploadToS3InputBucket(fileName, "Imagefile")
    uploadToS3OutputBucket(fileName, "ClassificationResult")

    sendMessageToRespQ(fileName, result)
    deleteMessage(receipt_handle)


while True:
    init()

