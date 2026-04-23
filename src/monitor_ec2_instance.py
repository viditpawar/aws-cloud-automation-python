import boto3
import sys
import os
from datetime import datetime, timedelta

#User-input for EC2 instance id
instance_id =os.environ['instance_id']

#User input for the region required
AWS_REGION = os.environ['AWS_Region']

#User input for setting the start and end dates
st= datetime(int(os.environ['year']), int(os.environ['month1']), int(os.environ['day1']))

et= datetime(int(os.environ['year']), int(os.environ['month2']), int(os.environ['day2']))


#User input for the duration(in seconds) of the statistics required.
#User must input the sum of seconds of the number of days
prd= int(os.environ['prd'])


#User input for type of statistic required. 
#User can opt out of Average/Minimum/Maximum/Sum statistics
stat= os.environ['stat']

#Getting the ec2 resource we need the mertrics for
EC2_RESOURCE = boto3.resource('ec2' , AWS_REGION)
def lambda_handler(event, context):
    ec2_resource = boto3.resource('ec2', AWS_REGION)

#Monitoring the state of the EC2 Instance
instance = EC2_RESOURCE.Instance(instance_id)
client = boto3.client('cloudwatch' , AWS_REGION)
print(f' EC2 instance => "{instance_id}"')
print(f' STATE => {instance.state["Name"]}')


#Monitoring the CPU utilization of the EC2 Instance
cpuresponse = client.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId','Value': instance_id},],
            StartTime=st,
            EndTime=et,
            Period=prd,
            Statistics=[stat],
            Unit='Percent'
    )
for cpu in cpuresponse['Datapoints']:
  if stat in cpu:
    print(f" CPU UTILIZATION => {cpu[stat]}")

#Monitoring the disk read utilization of the EC2 Instance 
diskreadresponse = client.get_metric_statistics(
    Namespace='AWS/EC2',  MetricName='DiskReadBytes',
    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id,},],
        StartTime=st,
        EndTime=et,
        Period=prd,
        Statistics=[stat],
        Unit='Bytes'
    )
for disk in diskreadresponse['Datapoints']:
  if stat in disk:
    print(f" DISK READ UTILIZATION => {disk[stat]}")

#Monitoring the disk write utilization of the EC2 Instance
diskwriteresponse = client.get_metric_statistics(
    Namespace='AWS/EC2',  MetricName='DiskWriteBytes',
    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id,},],
        StartTime=st,
        EndTime=et,
        Period=prd,
        Statistics=[stat],
        Unit='Bytes'
    )
for disk in diskreadresponse['Datapoints']:
  if stat in disk:
    print(f" DISK WRITE UTILIZATION => {disk[stat]}")

#Monitoring the disk read operations utilization of the EC2 Instance     
diskreadopsresponse = client.get_metric_statistics(
    Namespace='AWS/EC2',  MetricName='DiskReadOps',
    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id,},],
        StartTime=st,
        EndTime=et,
        Period=prd,
        Statistics=[stat],
        Unit='Count'
    )
for disk in diskreadopsresponse['Datapoints']:
  if stat in disk:
    print(f" DISK READ OPS UTILIZATION => {disk[stat]}")

#Monitoring the disk write operations utilization of the EC2 Instance
diskwriteopsresponse = client.get_metric_statistics(
    Namespace='AWS/EC2',  MetricName='DiskWriteOps',
    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id,},],
        StartTime=st,
        EndTime=et,
        Period=prd,
        Statistics=[stat],
        Unit='Count'
    )
for disk in diskwriteopsresponse['Datapoints']:
  if stat in disk:
    print(f" DISK WRITE OPS UTILIZATION => {disk[stat]}")
