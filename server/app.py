from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/parse', methods=['POST']) 
def parse():
    content = request.json
    return content

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')
