from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/get_summary', methods=['POST'])
def get_summary():
    data = request.get_json()
    input_text = data.get('text', '')
    # Simple summary: return the first 10 words
    summary = ' '.join(input_text.split()[:10])
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)