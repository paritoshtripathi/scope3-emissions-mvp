import os
from flask import Flask, request, jsonify
from inference.langchain_service import query_pipeline, index_clean_embeddings
from inference.weaviate_client import WeaviateClientSingleton

# Flask App Setup
app = Flask(__name__)

EMBEDDING_FILE = "models/combined_clean_embeddings.json"

@app.route("/test", methods=["GET"])
def test_endpoint():
    """
    Test endpoint to check if the server is running.
    """
    return jsonify({"message": "Server is running!"})

# API Endpoint: Query using the LLM pipeline
@app.route("/query", methods=["POST"])
def query_endpoint():
    """
    Handle chatbot queries.
    Expects a JSON body with a 'query' field.
    """
    data = request.json
    question = data.get("query", "")

    if not question:
        return jsonify({"error": "Query is required."}), 400

    try:
        response = query_pipeline(question)
        return jsonify({"response": response})
    except Exception as e:
        app.logger.error(f"Error processing query: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# API Endpoint: Predict with Template
@app.route('/predict_with_template', methods=['POST'])
def predict_with_template():
    """
    Predict insights based on a custom prompt template and a question.
    Handles dual embedding logic (preloaded JSON or dynamic generation).
    """
    data = request.json
    question = data.get('question', '')
    prompt_template = data.get('prompt_template', '')

    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        # Dual Embedding Logic
        if os.path.exists(EMBEDDING_FILE):
            print("Embedding file found. Loading and indexing...")
            index_clean_embeddings(EMBEDDING_FILE)
        else:
            print("Embedding file not found. Generating embeddings dynamically...")
            WeaviateClientSingleton.generate_embeddings("Document")

        # Run the pipeline
        response = query_pipeline(question, prompt_template)
        if not response:
            return jsonify({"error": "No response found."}), 404
        return jsonify({"response": response})
    except Exception as e:
        app.logger.error(f"Error in predict_with_template: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
