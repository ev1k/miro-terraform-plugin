from flask import Flask, request, jsonify
import hcl2

app = Flask(__name__)

@app.route('/parse', methods=['POST']) 
def parse():
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
