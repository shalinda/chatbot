import logging
from configparser import ConfigParser
from botocore.config import Config

# Parse the config.ini file
config_parser = ConfigParser()
config_parser.read('config.ini')

# AWS Bedrock settings
AWS_REGION = config_parser.get('app', 'aws_region')
GEN_MODEL_ID = config_parser.get('app', 'gen_model_id')
MODEL_ID = config_parser.get('app', 'model_id')
EMBED_MODEL_ID = config_parser.get('app', 'embed_model_id')
BEDROCK_READ_TIMEOUT = config_parser.getint('app', 'bedrock_read_timeout')
DB_LIMIT = config_parser.getint('app', 'db_limit')
MAX_TOKEN = config_parser.getint('app', 'max_token')

# Logging configuration
LOG_LEVEL = logging.getLevelName(config_parser.get('logging', 'log_level'))
LOG_FORMAT = config_parser.get('logging', 'log_format')

# Boto3 client configuration
BOTO3_CONFIG = Config(
    read_timeout=BEDROCK_READ_TIMEOUT,
    retries={"max_attempts": 0}
)


POSTGRES_HOST = config_parser.get('postgres', 'host')
POSTGRES_PORT = config_parser.get('postgres', 'port')
POSTGRES_USER = config_parser.get('postgres', 'user')
POSTGRES_PASSWORD = config_parser.get('postgres', 'password')
POSTGRES_DB = config_parser.get('postgres', 'database')

KB_FOLDER = config_parser.get('app', 'kb_folder')
