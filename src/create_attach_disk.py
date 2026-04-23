import json
import logging
import os
import time

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    try:
        instance_id = event.get("instance_id") or os.environ.get("INSTANCE_ID")
        availability_zone = event.get("availability_zone") or os.environ.get("AVAILABILITY_ZONE")
        size = int(event.get("size") or os.environ.get("SIZE", 10))
        volume_type = event.get("volume_type") or os.environ.get("VOLUME_TYPE", "gp3")
        device_name = event.get("device_name") or os.environ.get("DEVICE_NAME", "/dev/sdf")

        if not instance_id:
            return response(400, "Missing 'instance_id'.")
        if not availability_zone:
            return response(400, "Missing 'availability_zone'.")

        create_response = ec2.create_volume(
            AvailabilityZone=availability_zone,
            Size=size,
            VolumeType=volume_type,
            TagSpecifications=[
                {
                    "ResourceType": "volume",
                    "Tags": [{"Key": "Name", "Value": f"{instance_id}-extra-volume"}]
                }
            ]
        )

        volume_id = create_response["VolumeId"]
        logger.info("Created volume %s", volume_id)

        waiter = ec2.get_waiter("volume_available")
        waiter.wait(VolumeIds=[volume_id])

        ec2.attach_volume(
            Device=device_name,
            InstanceId=instance_id,
            VolumeId=volume_id
        )

        logger.info("Attached volume %s to instance %s", volume_id, instance_id)

        return response(
            200,
            "Disk created and attachment initiated successfully.",
            {
                "instance_id": instance_id,
                "volume_id": volume_id,
                "availability_zone": availability_zone,
                "size_gib": size,
                "volume_type": volume_type,
                "device_name": device_name,
            },
        )

    except ClientError as e:
        logger.exception("AWS ClientError while creating/attaching volume")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while creating/attaching volume")
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