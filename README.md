# AWS Cloud Automation Scripts

![status](https://img.shields.io/badge/status-active-success)
![python](https://img.shields.io/badge/python-3.x-blue)
![aws](https://img.shields.io/badge/AWS-Lambda-orange)
![boto3](https://img.shields.io/badge/library-boto3-informational)
![license](https://img.shields.io/badge/license-MIT-yellow)

Production-style AWS automation scripts built in Python for common cloud operations across EC2, EBS, VPC, CloudWatch, and SNS.

**Quick Links:** [Overview](#overview) | [Features](#features) | [Project Structure](#project-structure) | [Scripts](#scripts) | [Configuration](#configuration) | [Getting Started](#getting-started) | [Security Notes](#security-notes)

## Overview

This repository contains AWS Lambda-friendly scripts based on real cloud engineering workflows:

- EC2 monitoring and start automation
- EBS creation/attachment and resize operations
- VPC creation tasks
- Unattached Elastic IP reporting for cost optimization

Most scripts are currently **environment-variable driven** and rely minimally on the Lambda `event` payload.

## Features

- Automates repeatable AWS operational tasks
- Uses native AWS services and `boto3`
- Includes example payload/config references for each script
- Clean, production-style layout for showcasing cloud automation work

## Tech Stack

- Python
- AWS Lambda
- Boto3 / Botocore
- Amazon EC2 / EBS / VPC / CloudWatch / SNS

## Project Structure

```text
aws-cloud-automation-python/
|-- README.md
|-- requirements.txt
|-- src/
|   |-- create_attach_disk.py
|   |-- create_vpc.py
|   |-- monitor_ec2_instance.py
|   |-- report_unattached_eips.py
|   |-- resize_ebs_volume.py
|   `-- stop_start_ec2.py
`-- examples/
    |-- create_attach_disk_event.json
    |-- create_vpc_event.json
    |-- monitor_ec2_event.json
    |-- report_unattached_eips_event.json
    |-- resize_ebs_volume_event.json
    `-- stop_start_ec2_event.json
```

## Scripts

| Script | Purpose | AWS Services |
|---|---|---|
| `src/monitor_ec2_instance.py` | Prints instance state and CloudWatch utilization metrics | EC2, CloudWatch |
| `src/stop_start_ec2.py` | Starts stopped EC2 instances with `Environment=Non Prod` and sends SNS report | EC2, SNS |
| `src/create_attach_disk.py` | Creates and attaches an EBS volume to an EC2 instance | EC2, EBS |
| `src/create_vpc.py` | Creates a VPC and route table | VPC (EC2 API) |
| `src/report_unattached_eips.py` | Reports unattached Elastic IPs and publishes via SNS | EC2, SNS |
| `src/resize_ebs_volume.py` | Resizes EBS volume and tracks modification state | EC2, EBS |

## Configuration

The current scripts rely primarily on Lambda environment variables.

| Script | Required Environment Variables |
|---|---|
| `monitor_ec2_instance.py` | `instance_id`, `AWS_Region`, `year`, `month1`, `day1`, `month2`, `day2`, `prd`, `stat` |
| `stop_start_ec2.py` | None required; SNS topic is currently hardcoded in source |
| `create_attach_disk.py` | `voltype`, `val_name`, `inst_id`, `device_name`, `size_of_disk` |
| `create_vpc.py` | `IPv4_CIDR`, `AWS_Region`, `az`, `VPC_Name`, `RT_Name` |
| `report_unattached_eips.py` | `AWS_Region`, `SNS_Topic` |
| `resize_ebs_volume.py` | `VOLUME_ID`, `Size` |

## Examples

The `examples/*_event.json` files are reference payloads documenting expected configuration per script.  
They are aligned with current source behavior.

## Getting Started

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd aws-cloud-automation-python
pip install -r requirements.txt
```

### 2. Deploy as Lambda Functions

1. Create a Lambda function per script in `src/`
2. Configure runtime to Python 3.x
3. Set script-specific environment variables from the table above
4. Attach IAM permissions for the relevant AWS services used by each script
5. Test using the matching file in `examples/`

## Security Notes

Before making the repository public:

1. Replace hardcoded identifiers with environment variables/placeholders.
2. Remove any real account IDs, ARNs, emails, tokens, or credentials.
3. Enable GitHub secret scanning and push protection.
4. Keep production values in AWS Secrets Manager / Parameter Store / Lambda environment variables (not in code).

## License

This project is licensed under the MIT License.
