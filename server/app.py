from flask import Flask, request, jsonify
from flask_cors import CORS

import json
from pprint import pprint


app = Flask(__name__)
CORS(app)
resource_data = None
reload_resources()

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug(request)

@app.route('/get_price', methods=['GET']) 
def get_price():
    instanceType = request.values.get('instanceType')
    region = request.values.get('region')
    res = find_price(data, instanceType, region)
    
    response = app.response_class(
        response= json.dumps(res)
        mimetype='application/json'
    )
    return response

@app.route('/reload_resources', methods=['GET']) 
def reload_resources():
    with open('resources.json') as f:
    data = json.load(f)

def find_price(json_object, instanceType, region):
    ret = None
    for node in json_object:
        if (node['instanceType'] == instanceType and node['region'] == region):
            ret = node
    return ret      

@app.route('/parse', methods=['POST']) 
def parse():
    print(request)
    content = request.json
    return content

@app.route('/parse_test', methods=['POST']) 
def parse_test():
    data = '''{
  "graphs": [
    {
      "directed": true,
      "type": "graph type",
      "label": "graph label",
      "metadata": {
        "user-defined": "values"
      },
      "nodes": {
        "0": {
          "type": "node type",
          "label": "node label(0)",
          "metadata": {
            "user-defined": "values"
          }
        },
        "1": {
          "type": "node type",
          "label": "node label(1)",
          "metadata": {
            "user-defined": "values"
          }
        }
      },
      "edges": [
        {
          "source": "0",
          "relation": "edge relationship",
          "target": "1",
          "directed": true,
          "label": "edge label",
          "metadata": {
            "user-defined": "values"
          }
        }
      ]
    },
    {
      "directed": true,
      "type": "graph type",
      "label": "graph label",
      "metadata": {
        "user-defined": "values"
      },
      "nodes": {
        "0": {
          "type": "node type",
          "label": "node label(0)",
          "metadata": {
            "user-defined": "values"
          }
        },
        "1": {
          "type": "node type",
          "label": "node label(1)",
          "metadata": {
            "user-defined": "values"
          }
        }
      },
      "edges": [
        {
          "source": "1",
          "relation": "edge relationship",
          "target": "0",
          "directed": true,
          "label": "edge label",
          "metadata": {
            "user-defined": "values"
          }
        }
      ]
    }
  ]
}'''
    response = app.response_class(
        response=data,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0')
