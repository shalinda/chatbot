from flask import Flask, request, jsonify, Response
import boto3
import json
import logging
import traceback

# Initialize the Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')  # Update the region as needed

# Initialize Flask app
app = Flask(__name__)

# Basic console logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Optional: Log all requests
@app.before_request
def log_request():
    logger.info(f'{request.method} {request.path} - {request.remote_addr}')

# Function to generate text using Bedrock
def generate_text(prompt):
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Model ID for Anthropic's Claude model
    logger.info(f'prompt: {prompt}')
    try:
        prompt_config = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }

        body = json.dumps(prompt_config)
        accept = "application/json"
        contentType = "application/json"
        
        logger.info(f'body: {body}')

        # Invoke the model using the Bedrock client
        response = bedrock_client.invoke_model(
            body=body, modelId=model_id, accept=accept, contentType=contentType
        )
        logger.info(f'response: {response}')

        # Properly read the streaming body and parse it as JSON
        response_body = response['body'].read().decode('utf-8')  # Read and decode the StreamingBody
        response_json = json.loads(response_body)  # Parse it as JSON

        results = response_json.get("content")[0].get("text")
        return results  # Return the actual text result

    except Exception as e:
        logger.error(f"Error generating text: {e}")
        logger.error("Stack trace:", exc_info=True)
        traceback.print_exc()
        return None

# Define a route to use the generate_text function
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = generate_text(prompt)
    
    if result:
        return jsonify({"generated_text": result}), 200
    else:
        return jsonify({"error": "Failed to generate text"}), 500

# Start the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001)
