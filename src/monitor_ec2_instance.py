import json
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch = boto3.client("cloudwatch")


def lambda_handler(event, context):
    try:
        instance_id = event.get("instance_id") or os.environ.get("INSTANCE_ID")
        sns_topic_arn = event.get("sns_topic_arn") or os.environ.get("SNS_TOPIC_ARN")
        cpu_threshold = float(event.get("cpu_threshold") or os.environ.get("CPU_THRESHOLD", 80))
        period = int(event.get("period") or os.environ.get("PERIOD", 300))
        evaluation_periods = int(
            event.get("evaluation_periods") or os.environ.get("EVALUATION_PERIODS", 2)
        )

        if not instance_id:
            return response(400, "Missing 'instance_id' in event or environment variable.")

        if not sns_topic_arn:
            return response(400, "Missing 'sns_topic_arn' in event or environment variable.")

        alarm_name = f"HighCPU-{instance_id}"

        cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f"Alarm when CPU exceeds {cpu_threshold}% for EC2 instance {instance_id}",
            ActionsEnabled=True,
            AlarmActions=[sns_topic_arn],
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Statistic="Average",
            Dimensions=[
                {"Name": "InstanceId", "Value": instance_id}
            ],
            Period=period,
            EvaluationPeriods=evaluation_periods,
            Threshold=cpu_threshold,
            ComparisonOperator="GreaterThanThreshold",
            Unit="Percent"
        )

        logger.info("CloudWatch alarm configured for instance %s", instance_id)

        return response(
            200,
            "EC2 monitoring configured successfully.",
            {
                "instance_id": instance_id,
                "alarm_name": alarm_name,
                "cpu_threshold": cpu_threshold,
                "period": period,
                "evaluation_periods": evaluation_periods,
            },
        )

    except ClientError as e:
        logger.exception("AWS ClientError while configuring CloudWatch alarm")
        return response(500, f"AWS error: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        logger.exception("BotoCoreError while configuring CloudWatch alarm")
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