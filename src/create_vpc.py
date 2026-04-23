import json
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    try:
        cidr_block = event.get("cidr_block") or os.environ.get("CIDR_BLOCK")
        vpc_name = event.get("vpc_name") or os.environ.get("VPC_NAME", "PortfolioVPC")

        if not cidr_block:
            return response(400, "Missing 'cidr_block' in event or environment variable.")

        create_response = ec2.create_vpc(CidrBlock=cidr_block)
        vpc_id = create_response["Vpc"]["VpcId"]

        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})

        ec2.create_tags(
            Resources=[vpc_id],
            Tags=[{"Key": "Name", "Value": vpc_name}]
        )

        logger.info("Created VPC %s with CIDR %s", vpc_id, cidr_block)

        return response(
            200,
            "VPC created successfully.",
            {
                "vpc_id": vpc_id,
                "cidr_block": cidr_block,
                "vpc_name": vpc_name,
                "dns_support": True,
                "dns_hostnames": True,
            },
        )

    except ClientError as e:
        logger.exception("AWS ClientError while creating VPC")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while creating VPC")
        return response(500, f"Boto error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error")
        return response(500, f"Unexpected error: {str(e)}")


def response(status_code, message, data=None):
    body = {
        "message": message,
        "data": data or {}
    }
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }