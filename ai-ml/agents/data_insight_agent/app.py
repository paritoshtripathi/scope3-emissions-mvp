
from flask import Flask, jsonify, request
from llm_utils import generate_insights
from db_utils import fetch_latest_uploaded_data

app = Flask(__name__)

@app.route('/insights')
def insights():
    file_id = request.args.get('fileId', 'demo')
    raw_data = fetch_latest_uploaded_data(file_id)
    insights = generate_insights(raw_data)
    return jsonify(insights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
