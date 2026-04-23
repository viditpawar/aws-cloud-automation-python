import boto3
import time
import os

#Enter the type of disk to be attached
voltype = os.environ['voltype']
#Enter the name to be given to the disk
val_name = os.environ['val_name']
#Enter instance ID
inst_id = os.environ['inst_id']
#Enter device name
device_name = os.environ['device_name']

#Enter size of disk in GB
size_of_disk = int(os.environ['size_of_disk'])
#Listing EC2 Resources
ec2 = boto3.resource("ec2")

#Creating an EC2 Client
ec2_client=boto3.client("ec2")

def lambda_handler(event, context):
    ec2 = boto3.resource("ec2")

#Filtering EC2 Instances by instance ID
instances = ec2.instances.filter(
    InstanceIds=[
        inst_id,
    ],
)

#Checking for Availibility-Zone
for instance in instances:
    availabilityzone=(instance.placement['AvailabilityZone'])

#Creating Volume
new_volume = ec2_client.create_volume(
    AvailabilityZone=availabilityzone,
    Size=size_of_disk,
    VolumeType=voltype,
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': val_name
                }
            ]
        }
    ]
)
print(f'Created volume ID: {new_volume["VolumeId"]} ')
volid=new_volume["VolumeId"] #Storing Volume-ID

#Adding buffer time
time.sleep(8)

#Attaching Volume
attach_response=ec2_client.attach_volume(Device=device_name,
      InstanceId=inst_id,
      VolumeId=volid
    )
