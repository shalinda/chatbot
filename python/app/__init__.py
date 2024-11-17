# Global Bedrock client
bedrock_client = None
connection_pool = None

def set_bedrock_client(client):
    global bedrock_client
    bedrock_client = client

def get_bedrock_client():
    global bedrock_client
    return bedrock_client

def set_connection_pool(client):
    global connection_pool
    connection_pool = client

def get_connection_pool():
    global connection_pool
    return connection_pool