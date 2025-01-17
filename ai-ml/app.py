import os
import json
from flask import Flask, request, jsonify
from inference.langchain_service import query_pipeline
# from inference.langchain_service import query_RAG_QA_Search_with_prompt
from langchain_huggingface import HuggingFaceEndpoint

# Flask App Setup
app = Flask(__name__)

# Load Embeddings and Model Paths
EMBEDDINGS_PATH = "models/combined_clean_embeddings.json"

# Predict Route: Returns insights based on category or query
# @app.route("/predict", methods=["POST"])
# def predict():
#     """Predict insights based on user query or category."""
#     data = request.json
#     category = data.get("category", "")
#     query = data.get("query", "")

#     if not category and not query:
#         return jsonify({"error": "Provide either a category or a query"}), 400

#     try:
#         # Load embeddings data
#         with open(EMBEDDINGS_PATH, "r") as f:
#             embeddings = json.load(f)

#         # Fetch insights for category or query
#         if category:
#             result = embeddings.get(category, "No data available for this category.")
#         else:
#             result = query_pipeline(query)

#         return jsonify({"response": result})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Query Route: Chatbot queries
@app.route("/query", methods=["POST"])
def query_endpoint():
    """Handle chatbot queries."""
    data = request.json
    question = data.get("query", "")
    if not question:
        return jsonify({"error": "Query is required"}), 400

    try:
        response = query_pipeline(question)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict_with_template', methods=['POST'])
def predict_with_template():
    data = request.json
    print("Received data:", data)
    question = data.get('question', '')
    print("Question:", question)
    prompt_template = data.get('prompt_template', '')

    if not question:
        return jsonify({"error": "Question is required."}), 400
    # if not prompt_template:
    #     return jsonify({"error": "Prompt template is required."}), 400

    # try:
    response = query_pipeline(question, prompt_template)
    print("Response:", response)
    if not response:
        return jsonify({"error": "No response found."}), 404
    return jsonify({"response": response})
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
