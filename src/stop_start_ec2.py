###################################################################
#Purpose: To Start EC2 instances with Tags = Environment: Non Prod
#Created By: Divya Gujarathi
#Reviewed By:
###################################################################

import boto3
from datetime import datetime

#Listing all EC2 instances in the account
ec2 = boto3.resource('ec2')
instances = ec2.instances.all()
client_ec2 = boto3.client('ec2')


#Get the current time

now = datetime.now()
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

#Creating SNS client to send emails to topic subscriptions
sns_client = boto3.client("sns")

#This string list stores instance IDs/Instance names that have been started through this script
output=[]

#SNS Topic ARN created with a email subscription
SNS_Topic= "arn:aws:sns:us-east-1:956064229902:MyTopic"


def lambda_handler(event, context):
    
    instancename = '' #To Store instance names
    body = 'No Instances to Start' #Body will be used to convert list to string. Stores a default value
    for instance in instances:
    #To check if an instance has tags
     if instance.tags:
         for tag in instance.tags:
            if tag["Key"] == 'Name':
                instancename = tag["Value"]
            if ((tag["Key"]=='Environment') and (tag["Value"]=='Non Prod') and (instance.state['Name']=='stopped')):
                body=''
                client_ec2.start_instances(InstanceIds=[instance.id])
                output.append("Started Instance " +instancename+" with Instance ID "+ str(instance.id)+ " at "+ str(instance.launch_time))
                
   #List is converted to string through this loop
    for element in output:
        body+=element+'.\n'
    
   #Sending body as message to topic
    response = sns_client.publish(
    TargetArn=SNS_Topic,
    Message=body,
    Subject="Started Instances Report for "+date_time,
    MessageStructure='text')