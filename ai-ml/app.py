from flask import Flask, request, jsonify
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Load Hugging Face pipeline (modify as needed for your model)
model = pipeline("text-classification", model="distilbert-base-uncased")

@app.route("/")
def home():
    return jsonify({"message": "AI/ML Service is running!"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400
    predictions = model(data["text"])
    return jsonify(predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
