# app.py

from flask import Flask
from app.controllers.generation_controller import generation_blueprint
from app.controllers.faiss_controller import faiss_blueprint
from app.controllers.postgre_controller import pg_blueprint, initialize_connection_pool
from app import  set_bedrock_client, get_connection_pool;
from app.initialization import initialize_bedrock

    
bedrock_client = initialize_bedrock()
set_bedrock_client(bedrock_client)

initialize_connection_pool()

# Initialize Flask app
app = Flask(__name__)

# @app.teardown_appcontext
# def close_connection_pool(exception):
#     connection_pool = get_connection_pool()
#     if connection_pool:
#         connection_pool.closeall()
#         print("Connection pool closed")


# Register blueprints
app.register_blueprint(generation_blueprint)

app.register_blueprint(faiss_blueprint)
app.register_blueprint(pg_blueprint)
