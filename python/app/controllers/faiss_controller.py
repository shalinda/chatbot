from flask import Blueprint, request, jsonify
from app.config import MODEL_ID, EMBED_MODEL_ID
import logging
from app import get_bedrock_client

from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

# Create a Blueprint for this controller
faiss_blueprint = Blueprint('faiss', __name__)
br_embeddings = None
vs = None

# Load documents to vector store
@faiss_blueprint.route('/load_documents', methods=['POST'])
def load_documents():
    global vs
    
    br_embeddings = BedrockEmbeddings(model_id=EMBED_MODEL_ID, client=get_bedrock_client())
    
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({"error": "file_path is required"}), 400

    loader = PyPDFLoader(file_path)
    documents = loader.load()
    docs = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400, separator="\n").split_documents(documents)

    vs = FAISS.from_documents(documents=docs, embedding=br_embeddings)
    return jsonify({"message": f"Documents loaded to vector store. Number of elements in the index: {vs.index.ntotal}"})

# Execute prompt and return output
@faiss_blueprint.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Ensure the vector store has been initialized
    if vs is None:
        return jsonify({"error": "Vector store is not initialized. Load documents first."}), 400

    # Perform similarity search
    search_results = vs.similarity_search(question, k=3)
    context_string = '\n\n'.join([f'Document {ind+1}: ' + i.page_content for ind, i in enumerate(search_results)])

    # Create prompt template
    SYSTEM_MESSAGE = """
    System: Here is some important context which can help inform the questions the Human asks.
    Make sure to not make anything up to answer the question if it is not provided in the context.
    """
    HUMAN_MESSAGE = "Context: {context}\n\nQuestion: {question}"

    messages = [
        ("system", SYSTEM_MESSAGE),
        ("human", HUMAN_MESSAGE)
    ]

    prompt_data = ChatPromptTemplate.from_messages(messages)

    # Initialize the language model
    modelId = MODEL_ID
    cl_llm = ChatBedrock(model_id=modelId, client=get_bedrock_client(), model_kwargs={"temperature": 0.1, 'max_tokens': 100})

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
