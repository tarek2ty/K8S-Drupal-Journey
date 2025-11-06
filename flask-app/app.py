from flask import Flask, request

app = Flask(__name__)

@app.route('/<path:text>', methods=['GET'])
def get_text(text):
    return "Hi "+text, 200  # Returns whatever is after the host in the URL

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Allow requests from other hosts
