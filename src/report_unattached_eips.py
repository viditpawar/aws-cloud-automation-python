######################################
#Purpose: To report Unattached Elastic IPs
#Created By: Vidit Pawar, Maitrayee Dhumal
#Created Under: CIS Technology Office
######################################
import boto3
import logging
import os

#User input for the region required
AWS_REGION = os.environ['AWS_Region']

#This stores a default value for body
body = ''

#This string list stores the output message to be displayed
output=[]

#We are creating an SNS client to send emails to users for list of unattached IPs 
sns_client = boto3.client("sns")

#The SNS Topic ARN created with a email subscription required to publish the emails
SNS_Topic= os.environ['SNS_Topic']


def lambda_handler(event, context):
#Here we are listing EC2 Resources
    ec2_resource = boto3.resource("ec2")

client = boto3.client('ec2',AWS_REGION)

#assigning describe_address function to describe all the Elastic IP addresses.
addresses_dict = client.describe_addresses()

#Here, we are filtering through all the obtained IP addresses for unattached ones and saving them in output
print(" Region: " + AWS_REGION)
for eip_dict in addresses_dict['Addresses']:
    if "InstanceId" not in eip_dict:
        output.append(eip_dict['PublicIp'] + " => does not have any instances associated")

#Creating the list of unattached IPs and storing the list in body       
for element in output:
    body+=element+'.\n'
print(body)

#Publishing the email to user with the list of unattached IPs in the given AWS Region
sns = sns_client.publish(
    TargetArn=SNS_Topic,
    Message=body,
    Subject="List of unattached IP addresses in " + AWS_REGION,
    MessageStructure='text'
    )
             