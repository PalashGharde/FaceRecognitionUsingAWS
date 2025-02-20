import time
import boto3

# Provide perper information
aws_access_key_id = 'aws_access_key_id'
aws_secret_access_key = 'aws_secret_access_key'
region_name = 'us-east-1'
request_queue_url = 'request_queue_url'
response_queue_url = 'response_queue_url'
endpoint_url = 'https://sqs.us-east-1.amazonaws.com'

sqs = boto3.client('sqs', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                   endpoint_url=endpoint_url, region_name=region_name)

ec2_app = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
ec2_app_resources = ec2_app.resource('ec2', 'us-east-1')
ec2_app_client = ec2_app.client('ec2', 'us-east-1')

running_instances = []
stopped_instances = []
stopping_instances = []
starting_instances = []
workloadStarted = 0
workloadCompleted = 0
startScaling = 0

def getNumOfMsgs():
    response = sqs.get_queue_attributes(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'ApproximateNumberOfMessages',
            'ApproximateNumberOfMessagesNotVisible'
        ]
    )

    num_visible_msgs = int(response['Attributes']['ApproximateNumberOfMessages'])
    num_not_visible_msgs = int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    # print("NUm of ========================invisible msg: ",num_not_visible_msgs)
    num_requests = num_visible_msgs + num_not_visible_msgs
    return num_requests


def getRunningInstances():
    num = 0
    running_instances.clear()
    # instances = ec2.instance.all()
    instances = ec2_app_resources.instances.filter(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    for instance in instances:
        if instance.id != "i-00d3e04b1417804d5":
            running_instances.append(instance.id)
            num += 1

    # print("Num of Running Instances: ", num)
    return num


def getStoppingInstances():
    num = 0
    stopping_instances.clear()
    instances = ec2_app_resources.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["stopping"]}]
    )
    for instance in instances:
        if instance.id != "i-00d3e04b1417804d5":
            stopping_instances.append(instance.id)
            num += 1

    # print("Num of Stopping Instances: ", num)
    return num


def getStoppedInstances():
    num = 0
    stopped_instances.clear()
    instances = ec2_app_resources.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )
    for instance in instances:
        if instance.id != "i-00d3e04b1417804d5":
            stopped_instances.append(instance.id)
            num += 1

    # print("Num of Stopped Instances: ", num)
    return num


def getStartingInstances():
    num = 0
    starting_instances.clear()
    instances = ec2_app_resources.instances.filter(
        Filters=[{"Name": "instance-state-name", "Values": ["pending"]}]
    )
    for instance in instances:
        # print(instance.id)
        if instance.id != "Web Tier id to exclude":       # write ID of web tier to exclude from autoscaling
            starting_instances.append(instance.id)
            num += 1

    # print("Num of Starting/Pending Instances: ", num)
    return num


def createNewInstances(num):
    # print("Creating " + str(num) + " New Instances")

    New_instance = ec2_app_client.run_instances(
        ImageId = "ami-0fd3cb3d5f1811ac0",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        #SecurityGroupIds=[''],
        KeyName='my_key_pair',
        #UserData=user_data,
        TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'app-tier-instance-' + str(num)}]}],
    )
    return num

def clearRespQueue():
    # print("Clearing Response Queue")
    response = sqs.purge_queue(
        QueueUrl=response_queue_url
    )
    # print("Response Queue Cleared")

def clearReqQueue():
    # print("Clearing Request Queue")
    response = sqs.purge_queue(
        QueueUrl=request_queue_url
    )
    # print("Response Queue Cleared")


def scaleUP():
    totalAppInstance = getRunningInstances() + getStartingInstances()
    totalStoppedInstance = getStoppedInstances()
    getStoppingInstances()
    NumOfMsgs = getNumOfMsgs()
    # print("Scaling UP")
    # print("Total msgs: ", NumOfMsgs)
    # print("Total app instance: ", totalAppInstance)

    if totalStoppedInstance == 0 and getStoppingInstances()>0:
        return

    if NumOfMsgs > 0 and NumOfMsgs > totalAppInstance:
        numNewInstance1 = 20 - totalAppInstance #20
        numNewInstance2 = NumOfMsgs - totalAppInstance
        numNewInstance = min(numNewInstance1, numNewInstance2)
        numNewInstance = min(numNewInstance, totalStoppedInstance)
        # print("Num of new insctance to start: ********************** :",numNewInstance)
        workloadStarted = 1
        if numNewInstance > 0 and totalStoppedInstance > 0:
            count = 0
            instanceID = []
            while count < numNewInstance:
                instanceID.append(stopped_instances.pop())
                count += 1
            if len(instanceID) > 0:
                ec2_app_client.start_instances(InstanceIds=instanceID)


def scaleDOWN():
    totalStratingInstance = getStartingInstances()
    totalStoppingInstance = getStoppingInstances()
    totalStoppedInstance = getStoppedInstances()
    totalAppInstance = getRunningInstances()
    numOfMsgs = getNumOfMsgs()
    numInstanceToStop = numOfMsgs - totalAppInstance
    # print("Scaling DOWN")
    # print("Total msgs: ", numOfMsgs)
    # print("Total app instance: ", totalAppInstance)
    # print("Num of instance to stop: ", numInstanceToStop)
    instanceID = []
    while numInstanceToStop < 0 and len(running_instances)>0:
        instanceID.append(running_instances.pop())
        numInstanceToStop += 1
    if len(instanceID)>0:
        ec2_app_client.stop_instances(InstanceIds=instanceID)




while True:
    scaleUP()
    time.sleep(5)
    if getNumOfMsgs() == 0 and getRunningInstances() > 0:
        time.sleep(30)
        if getNumOfMsgs() == 0 and getRunningInstances() > 0:
            clearRespQueue()
            clearReqQueue()
            workloadCompleted = 1
            startScaling = 0
            scaleDOWN()

    if getRunningInstances() == 0 and workloadCompleted == 1 and workloadStarted == 1:
        workloadCompleted = 0
        workloadStarted = 0

