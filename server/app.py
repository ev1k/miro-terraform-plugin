from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import copy
import json

from server.hcl_parser import Parser
from pprint import pprint

app = Flask(__name__)
CORS(app)
resource_data = ''


@app.route('/reload_resources', methods=['GET'])
def reload_resources():
    with open('resources.json') as f:
        global resource_data
        resource_data = json.load(f)


reload_resources()


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug(request)


@app.route('/get_props', methods=['GET'])
def get_props():
    instanceType = request.values.get('instanceType')
    region = request.values.get('region')
    res = find_instance_props(resource_data, instanceType, region)
    if (res == None):
        abort(404)

    response = app.response_class(
        response=json.dumps(res),
        mimetype='application/json'
    )
    return response


@app.route('/calc_total_price', methods=['POST'])
def calc_total_price():
    app.logger.debug(str(request.json))
    res = find_total_price(request.json)
    response = app.response_class(
        response=json.dumps(res),
        mimetype='application/json'
    )
    return response


def find_total_price(instances):
    total_price = 0
    for instance in instances:
        props = find_instance_props(resource_data, instance['instanceType'], instance['region'])
        if (props == None):
            continue
        total_price = total_price + props['price']
    ret = {"total_price": total_price}
    return ret


def find_instance_props(json_object, instanceType, region):
    ret = None
    for node in json_object:
        if (node['instanceType'] == instanceType and node['region'] == region):
            ret = node
    if (ret == None):
        return None
    copied = copy.deepcopy(ret)
    del copied['instanceType']
    del copied['region']
    return copied


@app.route('/parse', methods=['POST'])
def parse():
    content = request.json

    parser = Parser()
    result = parser.run_text(content["data"])
    return result


@app.route('/parse_test', methods=['POST'])
def parse_test():
    data = '''{"graphs": [
    {
      "directed": true,
      "type": "graph type",
      "label": "graph label",
      "metadata": {
        "user-defined": "values"
      },
      "nodes": {
        "aws_lb.this[0]": {
          "type": "aws_lb",
          "label": "this",
          "metadata": {
            "name": "this",
            "lb_type": "application",
            "display_name": [
              "web-app"
            ]
          }
        },
        "aws_lb_listener.this[0]": {
          "type": "aws_lb_listener",
          "label": "this",
          "metadata": {
            "name": "this",
            "port": "80",
            "protocol": "HTTP",
            "default_action_type": "forward"
          }
        },
        "aws_lb_target_group.this[0]": {
          "type": "aws_lb_target_group",
          "label": "this",
          "metadata": {
            "name": "this",
            "vpc_id": "vpc-123",
            "port": 443,
            "protocol": "HTTPS",
            "target_type": "instance"
          }
        },
        "aws_lb_target_group.custom[0]": {
          "type": "aws_lb_target_group",
          "label": "custom",
          "metadata": {
            "name": "custom",
            "vpc_id": "vpc-123",
            "port": 443,
            "protocol": "HTTPS",
            "target_type": "instance"
          }
        },
        "aws_instance.this[0]": {
          "type": "aws_instance",
          "label": "this",
          "metadata": {
            "name": "this",
            "subnet_id": [
              "subnet-123"
            ],
            "instance_type": "c5.large",
            "count": 3,
            "availability_zone": "us-east-1a",
            "ami": "ami-123"
          }
        },
        "aws_instance.this[1]": {
          "type": "aws_instance",
          "label": "this",
          "metadata": {
            "name": "this",
            "subnet_id": [
              "subnet-123"
            ],
            "instance_type": "c5.large",
            "count": 3,
            "availability_zone": "us-east-1a",
            "ami": "ami-123"
          }
        },
        "aws_instance.this[2]": {
          "type": "aws_instance",
          "label": "this",
          "metadata": {
            "name": "this",
            "subnet_id": [
              "subnet-123"
            ],
            "instance_type": "c5.large",
            "count": 3,
            "availability_zone": "us-east-1a",
            "ami": "ami-123"
          }
        },
        "aws_instance.custom[0]": {
          "type": "aws_instance",
          "label": "custom",
          "metadata": {
            "name": "custom",
            "subnet_id": [
              "subnet-456"
            ],
            "instance_type": "m5.large",
            "count": 1,
            "availability_zone": "us-east-1a",
            "ami": "ami-456"
          }
        }
      },
      "edges": [
        {
          "source": "aws_lb.this[0]",
          "relation": "edge relationship",
          "target": "aws_lb_listener.this[0]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_listener.this[0]",
          "relation": "edge relationship",
          "target": "aws_lb_target_group.this[0]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_listener.this[0]",
          "relation": "edge relationship",
          "target": "aws_lb_target_group.custom[0]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_target_group.this[0]",
          "relation": "edge relationship",
          "target": "aws_instance.this[0]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_target_group.this[0]",
          "relation": "edge relationship",
          "target": "aws_instance.this[1]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_target_group.this[0]",
          "relation": "edge relationship",
          "target": "aws_instance.this[2]",
          "directed": true,
          "label": "",
          "metadata": {
            "user-defined": "values"
          }
        },
        {
          "source": "aws_lb_target_group.custom[0]",
          "relation": "edge relationship",
          "target": "aws_instance.custom[0]",
          "directed": true,
          "label": "",
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
    app.run(debug=True, host='0.0.0.0')
