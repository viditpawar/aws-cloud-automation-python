import json
import boto3
import time
import os


#User-input for volume ID
VOLUME_ID = os.environ['VOLUME_ID']

#User-input for the volume size (in GB) required
Vol_Size = int(os.environ['Size'])

#String to store the name of the volume
volname= ''

##Here we are listing EC2 Resources
ec2_resource = boto3.resource('ec2')

EC2_CLIENT = boto3.client('ec2')

#Volume to be fetched
volume = ec2_resource.Volume(VOLUME_ID)


def lambda_handler(event, context):
    
    #Referencing for the lambda handler
    EC2_CLIENT = boto3.client('ec2')
    ec2_resource = boto3.resource('ec2')
    volume = ec2_resource.Volume(VOLUME_ID)

#Fetching the name of the volume
#If name of the volume does not exist, continue with VOLUME_ID
if volume.tags:
    for tag in volume.tags:
            if tag["Key"] == 'Name':
                volname = tag["Value"]
else:
    volname = VOLUME_ID
           
                
#variable to store the previous size of the volume
prev_size= volume.size

def get_modification_state(volume_id):
    response = EC2_CLIENT.describe_volumes_modifications(
        VolumeIds=[
            VOLUME_ID
        ]
    )
    return response['VolumesModifications'][0]['ModificationState']

time.sleep(15)

#Calling the function to increase the size of the volume
try:
  
    if Vol_Size > prev_size:
        modify_volume_response = EC2_CLIENT.modify_volume(
    
    #required parameters to modify the volume size
        VolumeId=VOLUME_ID,
            Size=Vol_Size
        )

    else: 
        print(f"Volume size is already {Vol_Size} GB")
        
    while True:
        state = get_modification_state(VOLUME_ID)
        if state == 'completed' or state == None:
                #Printing the update and modified size of the volume
                print(f'Volume {volname} successfully resized')
                print(f'Volume size updated from {volume.size} GB to {Vol_Size} GB')
                break
        elif state == 'failed':
                raise Exception('Failed to modify volume size')
        else:
                time.sleep(60)

except :
  
    print(f'Cannot resize volume {volname}!')
