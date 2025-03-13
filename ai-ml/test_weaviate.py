from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import weaviate
import weaviate.classes.config as wvcc
import weaviate.classes as wvc
from weaviate.classes.init import AdditionalConfig, Timeout



# Load environment variables
load_dotenv()

WEAVIATE_URL = "http://localhost:8080/v1"

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test_connection():
    try:
        print("Weaviate URL", WEAVIATE_URL)
        # Create the schema in Weaviate
        client = weaviate.connect_to_local(
            port=8080,
            grpc_port=50051,
            additional_config=AdditionalConfig(
                timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
            ),
            skip_init_checks=True
        )
        if not client.is_ready():
            raise ValueError("Weaviate is not live")
        collection = client.collections.create(
            name="Company",
            properties=[
                wvcc.Property(
                    name="name", 
                    data_type=wvcc.DataType.TEXT,
                    description="The name of the company"
                    ),
                wvcc.Property(
                    name="emissionFactor", 
                    data_type=wvcc.DataType.NUMBER, 
                    description="Emission factor for the company"
                    ),
            ]
        )
        client.close()
        print("Collection created")
        response = requests.get(f"{WEAVIATE_URL}/schema")
        print(response)
        response.raise_for_status()
        return jsonify({"status": "Weaviate is ready", "details": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Cannot connect to Weaviate", "details": str(e)}), 500
    except ValueError as e:
        return jsonify({"error": "Weaviate is not live", "details": str(e)}), 500

@app.route('/add-schema', methods=['POST'])
def add_schema():
    schema = request.json
    try:
        response = requests.post(f"{WEAVIATE_URL}/schema", json=schema)
        response.raise_for_status()
        return jsonify({"status": "Schema added successfully", "response": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to add schema", "details": str(e)}), 500

@app.route('/schema', methods=['GET'])
def get_schema():
    try:
        response = requests.get(f"{WEAVIATE_URL}/schema")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to retrieve schema", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
