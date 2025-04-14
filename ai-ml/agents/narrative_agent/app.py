from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/narrative')
def narrative():
    return jsonify([
        {
            "type": "card",
            "message": "You are on track to reach 87% compliance by 2026."
        }
    ])
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
