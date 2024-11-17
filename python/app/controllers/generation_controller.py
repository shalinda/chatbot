# controllers/generation_controller.py

from flask import Blueprint, request, jsonify
from app.config import MODEL_ID
import json
import logging
import traceback
from app import get_bedrock_client

# Create a Blueprint for this controller
generation_blueprint = Blueprint('generation', __name__)

# Logger setup
logger = logging.getLogger(__name__)
# config = Config(read_timeout=1000, retries={"max_attempts": 0})
# bedrock_client1 = boto3.client(service_name='bedrock-runtime', 
#                   region_name='us-west-2',
#                   config=config)

@generation_blueprint.before_request
def log_request():
    logger.info(f'{request.method} {request.path} - {request.remote_addr}')

@generation_blueprint.route('/generate', methods=['POST'])
def generate():
    """
    Endpoint to generate text using AWS Bedrock.
    """
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = generate_text(prompt)

    if result:
        return jsonify({"generated_text": result}), 200
    else:
        return jsonify({"error": "Failed to generate text"}), 500


def generate_text(prompt):
    """
    Logic for generating text using Bedrock.
    """
    logger.info(f'Prompt received: {prompt}')

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

        logger.info(f'Request body: {body}')

        # Invoke the model using the Bedrock client
        response = get_bedrock_client().invoke_model(
            body=body, modelId=MODEL_ID, accept=accept, contentType=contentType
        )
        logger.info(f'Response received: {response}')

        # Read and decode the response body
        response_body = response['body'].read().decode('utf-8')
        response_json = json.loads(response_body)

        results = response_json.get("content")[0].get("text")
        return results  # Return the generated text

    except Exception as e:
        logger.error(f"Error generating text: {e}")
        logger.error("Stack trace:", exc_info=True)
        traceback.print_exc()
        return None
