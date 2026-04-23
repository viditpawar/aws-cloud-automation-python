import boto3,time
import os

IPv4_CIDR = os.environ['IPv4_CIDR']
AWS_Region= os.environ['AWS_Region']
az= os.environ['az']
VPC_Name= os.environ['VPC_Name']
RT_Name= os.environ['RT_Name']

#Lambda Handler function
def lambda_handler(event, context):
    ec2=boto3.resource("ec2", region_name=AWS_Region)

#Listing EC2 resources
vpc_client = boto3.client("ec2", region_name=AWS_Region)
ec2 = boto3.resource("ec2", region_name=AWS_Region)
vpc_resource = boto3.resource("ec2", region_name=AWS_Region)

#Creating VPC
vpc = ec2.create_vpc(CidrBlock=IPv4_CIDR,InstanceTenancy='default',
        TagSpecifications=[{'ResourceType':'vpc','Tags': [{'Key':'Name','Value':VPC_Name}]}]
        )
print(f'VPC ID=> {vpc.id}')

#Creating route table 
route_table = vpc_resource.create_route_table(
            VpcId=vpc.id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': RT_Name
                        },
                    ]
                },
            ]) 
print(f'Route table=> {route_table.id}')
