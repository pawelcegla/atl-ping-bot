import json

from flask import Flask
from flask import request

app = Flask(__name__)


@app.post('/webhook')
def webhook():
    print(json.dumps(request.get_json(), indent=2))
    return 'ok'
