#!/bin/bash

set -eu

OUTPUT_DIR=target

zip -9 ${OUTPUT_DIR}/deploy_package.zip lambda_function.py
aws s3 cp ${OUTPUT_DIR}/deploy_package.zip s3://aws-lambda-scrape
aws lambda delete-function --function-name topcoder-mm-standings-scrape && :
aws lambda create-function --region us-east-1 --function-name topcoder-mm-standings-scrape --runtime python3.6 --role arn:aws:iam::142710310450:role/aws-lamda-scrape-roll --code S3Bucket=aws-lambda-scrape,S3Key=deploy_package.zip --handler lambda_function.lambda_handler --memory-size 512 --timeout 600 --layers "arn:aws:lambda:us-east-1:142710310450:layer:scrape-lib-layer:3"
