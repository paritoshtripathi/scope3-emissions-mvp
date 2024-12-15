from flask import Flask, request, jsonify
import os
import requests
# from transformers import pipeline
from inference.langchain_service import query_pipeline


# Initialize Flask app
app = Flask(__name__)

# Model selection options
# USE_INFERENCE_API = os.getenv("USE_INFERENCE_API", "true").lower() == "true"
# LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "distilbert-base-uncased")

INFERENCE_API_URL = os.getenv("INFERENCE_API_URL", "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "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")

# # Initialize model (local or API-based)
# if USE_INFERENCE_API:
#     print("Using Hugging Face Inference API for predictions.")
# else:
#     print(f"Loading local model: {LOCAL_MODEL_NAME}")
#     model = pipeline("text-classification", model=LOCAL_MODEL_NAME)

@app.route("/")
def home():
    return jsonify({"message": "AI/ML Service is running!"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    # if USE_INFERENCE_API:
        # Use Hugging Face Inference API
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    response = requests.post(INFERENCE_API_URL, headers=headers, json={"inputs": data["text"]})
    if response.status_code != 200:
        return jsonify({"error": "Inference API failed", "details": response.json()}), 500
    predictions = response.json()
    # else:
    #     # Use locally loaded model
    #     predictions = model(data["text"])

    return jsonify(predictions)

@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = query_pipeline(question)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
