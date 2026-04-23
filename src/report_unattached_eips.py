import json
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")
sns = boto3.client("sns")


def lambda_handler(event, context):
    """
    Expected optional event:
    {
      "publish_to_sns": false
    }

    Optional environment variable:
    SNS_TOPIC_ARN=arn:aws:sns:region:account-id:topic-name
    """

    try:
        publish_to_sns = event.get("publish_to_sns", False)
        sns_topic_arn = os.environ.get("SNS_TOPIC_ARN")

        addresses_response = ec2.describe_addresses()
        addresses = addresses_response.get("Addresses", [])

        unattached_eips = []
        for address in addresses:
            if "AssociationId" not in address and "InstanceId" not in address and "NetworkInterfaceId" not in address:
                unattached_eips.append(
                    {
                        "public_ip": address.get("PublicIp"),
                        "allocation_id": address.get("AllocationId"),
                        "domain": address.get("Domain"),
                    }
                )

        summary = {
            "total_elastic_ips": len(addresses),
            "unattached_elastic_ips_count": len(unattached_eips),
            "unattached_elastic_ips": unattached_eips,
        }

        logger.info("Elastic IP scan complete: %s", json.dumps(summary))

        if publish_to_sns and sns_topic_arn:
            message = build_sns_message(summary)
            sns.publish(
                TopicArn=sns_topic_arn,
                Subject="AWS Unattached Elastic IP Report",
                Message=message,
            )
            logger.info("Report published to SNS topic %s", sns_topic_arn)

        return response(
            200,
            "Elastic IP scan completed successfully.",
            summary,
        )

    except ClientError as e:
        logger.exception("AWS ClientError while scanning Elastic IPs")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while scanning Elastic IPs")
        return response(500, f"Boto error: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error")
        return response(500, f"Unexpected error: {str(e)}")


def build_sns_message(summary):
    lines = [
        "AWS Unattached Elastic IP Report",
        "",
        f"Total Elastic IPs: {summary['total_elastic_ips']}",
        f"Unattached Elastic IPs: {summary['unattached_elastic_ips_count']}",
        "",
    ]

    if summary["unattached_elastic_ips"]:
        lines.append("Details:")
        for eip in summary["unattached_elastic_ips"]:
            lines.append(
                f"- Public IP: {eip['public_ip']}, Allocation ID: {eip['allocation_id']}, Domain: {eip['domain']}"
            )
    else:
        lines.append("No unattached Elastic IPs found.")

    return "\n".join(lines)


def response(status_code, message, data=None):
    body = {
        "message": message,
        "data": data or {}
    }
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }