from psycopg2.extras import execute_values
from botocore.exceptions import BotoCoreError, ClientError
import numpy as np
import os


from flask import Blueprint, request, jsonify
import logging
from app import get_bedrock_client
from app.config import EMBED_MODEL_ID, MODEL_ID, \
    POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT, KB_FOLDER, \
    DB_LIMIT, MAX_TOKEN
from app import set_connection_pool, get_connection_pool
import psycopg2.pool

from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter

from langchain_community.document_loaders import PyPDFDirectoryLoader

# Create a Blueprint for this controller
pg_blueprint = Blueprint('pg', __name__)
br_embeddings = None
vs = None

def initialize_connection_pool():

    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # Minimum and maximum connections in the pool
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB
        )
        if connection_pool:
            print("Connection pool created successfully")
            set_connection_pool(connection_pool)
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        raise e


# Load documents to PostgreSQL vector store
@pg_blueprint.route('/load_documents1', methods=['POST'])
def load_documents():

    delete = request.json.get('delete')
    br_embeddings = BedrockEmbeddings(model_id=EMBED_MODEL_ID, client=get_bedrock_client())

    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({"error": "file_path is required"}), 400

    folder_path = os.path.join(KB_FOLDER, file_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    loader = PyPDFDirectoryLoader(folder_path)
    documents = loader.load()
    docs = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400, separator="\n").split_documents(documents)

    doc_texts = [doc.page_content for doc in docs]
    embeddings = br_embeddings.embed_documents(doc_texts)

    try:
        conn = get_connection_pool().getconn()
        cursor = conn.cursor()

        # Delete existing documents for the given file_path
        if delete:
            cursor.execute("DELETE FROM DOCUMENT WHERE kb = %s", (file_path,))
            conn.commit()

        # Insert documents with embeddings
        records = [
            (embedding, file_path, 'pdf', folder_path, doc.page_content)
            for embedding, doc in zip(embeddings, docs)
        ]

        execute_values(
            cursor,
            "INSERT INTO DOCUMENT (embedding, kb, file_type, file_name, content) VALUES %s",
            records,
            template="(%s::vector, %s, %s, %s, %s)"
        )
        conn.commit()

        message = f"{len(records)} documents loaded to PostgreSQL vector store."
        print(message)

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

    finally:
        if conn:
            cursor.close()
            get_connection_pool().putconn(conn)

    return jsonify({"message": message})


# Execute prompt and return output
@pg_blueprint.route('/ask1', methods=['POST'])
def ask():
    data = request.json
    kb = data.get('kb')
    question = data.get('question')
    limit = int(data.get('limit', 3))  # Default to 3 if limit is not provided
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    if not kb:
        return jsonify({"error": "Knowledgebase 'kb' is required"}), 400

    br_embeddings = BedrockEmbeddings(model_id=EMBED_MODEL_ID, client=get_bedrock_client())
    # Generate the question embedding
    question_embedding = br_embeddings.embed_documents([question])[0]  # Wrap question in a list

    # Query PostgreSQL vector store for similar documents
    conn = None
    try:
        # Get a connection from the pool
        conn = get_connection_pool().getconn()
        cursor = conn.cursor()

        # Retrieve the top n most similar documents
        cursor.execute(
            """
            SELECT content
            FROM DOCUMENT
            WHERE KB = %s
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """,
            (kb, question_embedding, DB_LIMIT)
        )
        search_results = cursor.fetchall()
        context_string = '\n\n'.join([f"Document {i+1}: {content[0]}" for i, content in enumerate(search_results)])

        cursor.close()

    except Exception as e:
        if conn:
            get_connection_pool().putconn(conn, close=True)  # Remove faulty connection
        return jsonify({"error": "Database query failed", "details": str(e)}), 500

    finally:
        if conn:
           get_connection_pool().putconn(conn)  # Return connection to the pool

    # Define prompt template
    SYSTEM_MESSAGE = """
        System: Here is some important context which can help inform the questions the Human asks.
        Respond with a direct answer. Start your response with 'We' if referring to the service.
        Avoid using any prefatory or unnecessary phrases.
        """

    HUMAN_MESSAGE = "Context: {context}\n\nQuestion: {question}\n\nPlease provide a short and direct answer."

    messages = [
        ("system", SYSTEM_MESSAGE),
        ("human", HUMAN_MESSAGE)
    ]

    prompt_data = ChatPromptTemplate.from_messages(messages)

    # Set up the language model    
    cl_llm = ChatBedrock(model_id=MODEL_ID, client=get_bedrock_client(), model_kwargs={"temperature": 0.05, 'max_tokens': MAX_TOKEN})

    chain = prompt_data | cl_llm | StrOutputParser()
    chain_input = {
        "context": context_string,
        "question": question,
    }

    # Stream the response
    response = ""
    for chunk in chain.stream(chain_input):
        response += chunk

    return jsonify({"answer": response})
