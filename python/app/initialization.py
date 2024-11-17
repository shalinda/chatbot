# initialization.py

import boto3
import logging
from app.config import AWS_REGION, BOTO3_CONFIG
from botocore.exceptions import BotoCoreError, ClientError
from botocore.config import Config

logger = logging.getLogger(__name__)

def initialize_bedrock():
    try:
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION,
            config=BOTO3_CONFIG
        )

        logger.info("Bedrock client initialized successfully.")
        return bedrock_client
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to initialize AWS Bedrock client: {e}")
        raise e
