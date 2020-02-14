import hcl2
import os
import json
from server.entities import *
from lark.exceptions import UnexpectedToken


class Parser:
    def __init__(self):
        self.resources = None
        self.all_objects = dict()
        self.top_objects = list()
        self.resource_types = list()
        self.walked_resources = dict()
        self.walked_resources_reverse_index = dict()
        self.variables = None

    def run_dirs(self, directories):
        for d in directories:
            self.load_dir(d)

        return self.run_walker()

    def get_graph(self, text):
        try:
            self.load_text(text)
            result = self.run_walker()
        except UnexpectedToken as e:
            result = {
                "error": e.args,
                "line": e.line,
                "colunmn": e.column
            }

        return result

    def run_walker(self):
        self.collect_vars()
        self.resources = self.safe_get(self.all_objects, 'resource')
        self.walk_resources()
        return self.create_graph()

    def create_graph(self):
        nodes = dict()
        edges = list()

        for resource_type, resource_dict in self.walked_resources.items():
            for resource_name, resource_obj in resource_dict.items():
                for si in range(0, resource_obj.count):
                    source_id = resource_type + "." + resource_name + "[" + str(si) + "]"

                    nodes[source_id] = {
                        "type": resource_type,
                        "label": resource_name,
                        "metadata": resource_obj.as_dict()
                    }

                    for target_obj in resource_obj.connected_to:
                        target_type, target_name = self.walked_resources_reverse_index[target_obj]

                        for ti in range(0, target_obj.count):
                            target_id = target_type + "." + target_name + "[" + str(ti) + "]"

                            edges.append(
                                {
                                    "source": source_id,
                                    "relation": "edge relationship",
                                    "target": target_id,
                                    "directed": True,
                                    "label": "",
                                    "metadata": {
                                        "user-defined": "values"
                                    }
                                }
                            )

        graph = {
            "graphs": [
                {
                    "directed": True,
                    "type": "graph type",
                    "label": "graph label",
                    "metadata": {
                        "user-defined": "values"
                    },
                    "nodes": nodes,
                    "edges": edges
                }
            ]
        }

        return graph

    def dumper(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

    def add_unique(self, array, key):
        if not key in array:
            array.append(key)

    def ingest_file(self, file):
        for obj_name in file:
            self.add_unique(self.top_objects, obj_name)

            if obj_name in ('locals', 'terraform', 'dependency', 'include'):  # ignore for now,
                continue

            if obj_name not in self.all_objects:
                self.all_objects[obj_name] = dict()

            for obj_def in file[obj_name]:
                for obj_type, obj_instances in obj_def.items():
                    if not obj_type in self.all_objects[obj_name]:
                        self.all_objects[obj_name][obj_type] = dict()

                    if isinstance(obj_instances, dict):
                        for instance_name, properties in obj_instances.items():
                            self.all_objects[obj_name][obj_type][instance_name] = properties
                    else:
                        for instance in obj_instances:
                            self.all_objects[obj_name][obj_type]['_default'] = instance

    def load_dir(self, root):
        for root, dirs, files in os.walk(root):
            # print("root - ", root)
            for file in files:
                if file.endswith(".tf") or file.endswith(".hcl"):
                    filepath = root + os.sep + file

                    with open(filepath, 'r') as fp:
                        try:
                            obj = hcl2.load(fp)

                        except Exception:
                            print("Error processing file " + filepath)
                            obj = None

                        self.ingest_file(obj)

    def load_text(self, text):
        obj = hcl2.loads(text)
        self.ingest_file(obj)

    def safe_get(self, dictionary, key):
        if dictionary is not None:
            if key in dictionary:
                return dictionary[key]
        return None

    def simplify_list(self, variable):
        if isinstance(variable, list) and len(variable) == 1:
            return variable[0]
        return variable

    def collect_vars(self):
        collected_variables = dict()

        variables = self.safe_get(self.all_objects, 'variable')
        if variables:
            for variable_name, variable_def in variables.items():
                default_value = self.simplify_list(self.safe_get(variable_def, 'default'))
                if default_value:
                    var_value = default_value
                else:
                    var_value = 'undefined'
                collected_variables[variable_name] = var_value

        modules = self.safe_get(self.all_objects, 'module')
        if modules:
            for module_name, module_props in modules.items():
                for prop_name, prop_value in module_props.items():
                    collected_variables[prop_name] = self.simplify_list(prop_value)

        # TODO inputs = safe_get(all_objects, 'inputs')  # from terragrunt.hcl

        self.variables = collected_variables

    def read_prop(self, props_object, key, default):
        if props_object is not None and key in props_object:
            value = self.simplify_list(props_object[key])
        else:
            value = default

        # if it is a ref:
        if isinstance(value, str) and value.startswith("${"):
            var_name = value[2:-1]
            var_name_parts = var_name.split(".")
            if len(var_name_parts) > 1 and var_name_parts[0] == 'var':
                var_value = self.safe_get(self.variables, var_name_parts[1])
                if var_value:
                    value = var_value

        return value

    def is_resource_walked(self, resource_type, resource_name):
        return resource_type in self.walked_resources and resource_name in self.walked_resources[resource_type]

    def get_resource(self, resource_type, resource_name):
        if not self.is_resource_walked(resource_type, resource_name):
            return None
        return self.walked_resources[resource_type][resource_name]

    def place_resource(self, resource_type, resource_name, obj):
        if self.is_resource_walked(resource_type, resource_name):
            raise Exception("Resource already exists")

        if resource_type not in self.walked_resources:
            self.walked_resources[resource_type] = dict()

        self.walked_resources[resource_type][resource_name] = obj
        self.walked_resources_reverse_index[obj] = (resource_type, resource_name)

    def search_resource(self, resource_full_name, resource_type=None):
        if isinstance(resource_full_name, str) and resource_full_name.startswith("${") and resource_full_name.endswith("}"):
            var_name = resource_full_name[2:-1]
            var_name_parts = var_name.split(".")

            if not resource_type:
                resource_type = var_name_parts[0]
            resource_name = var_name_parts[1].split("[")[0]

            self.walk_resource(resource_type, resource_name)
            resource = self.get_resource(resource_type, resource_name)
        else:
            resource = None

        if not resource:
            resource = TfResource(resource_full_name)

        return resource

    def walk_instance(self, name, props):
        print("Walking on instance " + name)

        instance_count = self.read_prop(props, 'count', 1)
        subnet_id = self.read_prop(props, 'subnet_id', None),
        instance_type = self.read_prop(props, 'instance_type', None)
        availability_zone = self.read_prop(props, 'availability_zone', None)
        ami = self.read_prop(props, 'ami', None)


        instance = AwsInstance(name, subnet_id, instance_type, instance_count, availability_zone, ami)

        self.place_resource(RT_INSTANCE, name, instance)

    def walk_lb(self, name, props):
        print("Walking on load balancer " + name)

        display_name = self.read_prop(props, 'name', None),
        load_balancer_type = self.read_prop(props, 'load_balancer_type', None)

        obj = AwsLoadBalancer(name, display_name, load_balancer_type)
        self.place_resource(RT_LB, name, obj)

    def walk_lb_tg(self, name, props):
        print("Walking on load balancer target group" + name)

        vpc_id = self.read_prop(props, 'vpc_id', None)
        port = self.read_prop(props, 'port', None)
        protocol = self.read_prop(props, 'protocol', None)
        target_type = self.read_prop(props, 'target_type', None)

        obj = AwsLoadBalancerTargetGroup(name, vpc_id, port, protocol, target_type)
        self.place_resource(RT_LB_TG, name, obj)

    def walk_lb_tg_attachment(self, name, props):
        print("Walking on load balancer target group attachment" + name)

        count = self.read_prop(props, 'count', None)
        target_group_arn = self.read_prop(props, 'target_group_arn', None)
        target_id = self.read_prop(props, 'target_id', None)
        port = self.read_prop(props, 'port', None)

        target = self.search_resource(target_id)
        target_group = self.search_resource(target_group_arn)

        target_group.connect(target)

    def walk_lb_listener(self, name, props):
        print("Walking on listener" + name)

        load_balancer_arn = self.read_prop(props, 'load_balancer_arn', None)
        port = self.read_prop(props, 'port', None)
        protocol = self.read_prop(props, 'protocol', None)

        default_action = self.read_prop(props, 'default_action', None)
        default_action_type = self.read_prop(default_action, 'type', None)
        target_group_arn = self.read_prop(default_action, 'target_group_arn', None)

        obj = AwsLbListener(name, port, protocol, default_action_type)
        self.place_resource(RT_LB_LISTENER, name, obj)

        target_group = self.search_resource(target_group_arn)
        load_balancer = self.search_resource(load_balancer_arn)

        load_balancer.connect(obj)
        obj.connect(target_group)

    def walk_lb_listener_rule(self, name, props):
        print("Walking on listener rule" + name)

        listener_arn = self.read_prop(props, 'listener_arn', None)
        # type = self.read_prop(props, 'type', None)
        target_group_arn = self.read_prop(props, 'target_group_arn', None)

        listener = self.search_resource(listener_arn)
        target_group = self.search_resource(target_group_arn)

        listener.connect(target_group)

    def walk_resource(self, resource_type, resource_name):
        if self.is_resource_walked(resource_type, resource_name):
            print("Already processed " + resource_type + " -> " + resource_name)
            return

        print("Processing " + resource_type + " -> " + resource_name)
        resource_props = self.resources[resource_type][resource_name]

        if resource_type == RT_INSTANCE:
            self.walk_instance(resource_name, resource_props)
        elif resource_type == RT_LB:
            self.walk_lb(resource_name, resource_props)
        elif resource_type == RT_LB_TG:
            self.walk_lb_tg(resource_name, resource_props)
        elif resource_type == RT_LB_TG_ATTACHMENT:
            self.walk_lb_tg_attachment(resource_name, resource_props)
        elif resource_type == RT_LB_LISTENER:
            self.walk_lb_listener(resource_name, resource_props)
        elif resource_type == RT_LB_LISTENER_RULE:
            self.walk_lb_listener_rule(resource_name, resource_props)

        else:
            print("Unknown resource type, skipping")

    def walk_resources(self):
        if self.resources:
            for resource_type, resource_dict in self.resources.items():
                for resource_name in resource_dict:
                    self.walk_resource(resource_type, resource_name)


#p = Parser()
#dirs = [
    # '/Users/edro/work/iac/terraform/live/env_prod/provider_aws/account_prod/region_eu-west-1/vpc_prod/hazelcast_prod',
    # '/Users/edro/work/iac/terraform/global/modules/hazelcast',
   # '/Users/edro/work/miro-terraform-plugin/server'
#]

#g = p.run(dirs)


# for instance_name, instance_props in all_objects["resource"]['aws_instance'].items():
#    print(instance_name, instance_props)

#print(json.dumps(g, default=Parser.dumper, indent=2))

# print(json.dumps(resource_types, default=dumper, indent=4))
# print(json.dumps(top_objects, default=dumper, indent=4))