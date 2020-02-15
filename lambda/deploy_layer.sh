#!/bin/bash

set -eu

OUTPUT_DIR=target

mkdir -p tmp

if [ ! -e "tmp/chromedriver.zip" ]; then
    curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > tmp/chromedriver.zip
fi

if [ ! -e "tmp/headless-chromium.zip" ]; then
    curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > tmp/headless-chromium.zip
fi

docker build -t lambda_headless_chrome .
docker run -v ${PWD}:/var/task lambda_headless_chrome

aws s3 cp ${OUTPUT_DIR}/deploy_layer.zip s3://aws-lambda-scrape
aws lambda publish-layer-version --layer-name scrape-lib-layer --content S3Bucket=aws-lambda-scrape,S3Key=deploy_layer.zip --compatible-runtimes python3.6
