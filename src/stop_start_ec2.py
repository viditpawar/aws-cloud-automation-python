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
        action = (event.get("action") or os.environ.get("ACTION", "")).lower()
        tag_key = event.get("tag_key") or os.environ.get("TAG_KEY", "Environment")
        tag_value = event.get("tag_value") or os.environ.get("TAG_VALUE", "NonProd")

        if action not in ["start", "stop"]:
            return response(400, "Action must be 'start' or 'stop'.")

        filters = [
            {"Name": f"tag:{tag_key}", "Values": [tag_value]},
            {"Name": "instance-state-name", "Values": ["running", "stopped"]}
        ]

        reservations = ec2.describe_instances(Filters=filters).get("Reservations", [])
        instance_ids = []

        for reservation in reservations:
            for instance in reservation.get("Instances", []):
                instance_ids.append(instance["InstanceId"])

        if not instance_ids:
            return response(
                200,
                f"No matching EC2 instances found for tag {tag_key}={tag_value}.",
                {"instance_ids": []}
            )

        if action == "start":
            ec2.start_instances(InstanceIds=instance_ids)
        else:
            ec2.stop_instances(InstanceIds=instance_ids)

        logger.info("%s action initiated for instances: %s", action, instance_ids)

        return response(
            200,
            f"EC2 {action} action initiated successfully.",
            {
                "action": action,
                "tag_key": tag_key,
                "tag_value": tag_value,
                "instance_ids": instance_ids,
            },
        )

    except ClientError as e:
        logger.exception("AWS ClientError while starting/stopping instances")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while starting/stopping instances")
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