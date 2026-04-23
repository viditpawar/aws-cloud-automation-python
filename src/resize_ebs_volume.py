import json
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    """
    Expected event:
    {
      "volume_id": "vol-xxxxxxxxxxxxxxxxx",
      "new_size": 30
    }
    """

    try:
        volume_id = event.get("volume_id") or os.environ.get("VOLUME_ID")
        new_size = event.get("new_size") or os.environ.get("NEW_SIZE")

        if not volume_id:
            return response(400, "Missing 'volume_id' in event or environment variable.")

        if not new_size:
            return response(400, "Missing 'new_size' in event or environment variable.")

        try:
            new_size = int(new_size)
        except ValueError:
            return response(400, "'new_size' must be an integer.")

        volume_info = ec2.describe_volumes(VolumeIds=[volume_id])
        volumes = volume_info.get("Volumes", [])

        if not volumes:
            return response(404, f"Volume {volume_id} not found.")

        volume = volumes[0]
        current_size = volume["Size"]

        volume_name = volume_id
        for tag in volume.get("Tags", []):
            if tag.get("Key") == "Name":
                volume_name = tag.get("Value")
                break

        if new_size <= current_size:
            return response(
                400,
                f"New size must be greater than current size ({current_size} GiB)."
            )

        modify_result = ec2.modify_volume(
            VolumeId=volume_id,
            Size=new_size
        )

        logger.info(
            "Volume resize initiated for %s (%s): %s -> %s GiB",
            volume_name,
            volume_id,
            current_size,
            new_size,
        )

        return response(
            200,
            "Volume resize initiated successfully.",
            {
                "volume_id": volume_id,
                "volume_name": volume_name,
                "previous_size_gib": current_size,
                "requested_size_gib": new_size,
                "modification_state": modify_result.get("VolumeModification", {}).get("ModificationState")
            },
        )

    except ClientError as e:
        logger.exception("AWS ClientError while modifying volume")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while modifying volume")
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