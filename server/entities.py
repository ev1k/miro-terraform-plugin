
RT_INSTANCE = "aws_instance"
RT_LB = "aws_lb"
RT_LB_TG = "aws_lb_target_group"
RT_LB_TG_ATTACHMENT = "aws_lb_target_group_attachment"
RT_LB_LISTENER = "aws_lb_listener"
RT_LB_LISTENER_RULE = "aws_lb_listener_rule"
RT_S3_BUCKET = "aws_s3_bucket"


class TfResource:
    def __init__(self, name):
        self.name = name
        self.connected_to = list()
        self.count = 1

    def connect(self, to: "TfResource"):
        self.connected_to.append(to)

    def as_dict(self):
        return {
            'name': self.name
        }


class AwsInstance(TfResource):
    def __init__(self, name, subnet_id, instance_type, count, availability_zone, ami):
        super().__init__(name)

        self.subnet_id = subnet_id
        self.instance_type = instance_type
        self.count = count
        self.availability_zone = availability_zone
        self.ami = ami

    def __repr__(self):
        return "AwsInstance[x" + str(self.count) + "] " + str(self.name) + " (" + str(self.instance_type) + ")"

    def as_dict(self):
        return {
            'name': self.name,
            'subnet_id': self.subnet_id,
            'instance_type': self.instance_type,
            'count': self.count,
            'availability_zone': self.availability_zone,
            'ami': self.ami
        }


class AwsLoadBalancer(TfResource):
    def __init__(self, name, display_name, lb_type):
        super().__init__(name)

        self.lb_type = lb_type
        self.display_name = display_name

    def __repr__(self):
        return "AwsLoadBalancer " + str(self.name) + " (" + str(self.lb_type) + ")"

    def as_dict(self):
        return {
            'name': self.name,
            'lb_type': self.lb_type,
            'display_name': self.display_name,
        }


class AwsLoadBalancerTargetGroup(TfResource):
    def __init__(self, name, vpc_id, port, protocol, target_type):
        super().__init__(name)

        self.vpc_id = vpc_id
        self.port = port
        self.protocol = protocol
        self.target_type = target_type

    def __repr__(self):
        return "AwsLoadBalancerTargetGroup " + str(self.name) + " (" + str(self.port) + ")"

    def as_dict(self):
        return {
            'name': self.name,
            'vpc_id': self.vpc_id,
            'port': self.port,
            'protocol': self.protocol,
            'target_type': self.target_type,
        }


class AwsLbListener(TfResource):
    def __init__(self, name, port, protocol, default_action_type):
        super().__init__(name)

        self.port = port
        self.protocol = protocol
        self.default_action_type = default_action_type

    def __repr__(self):
        return "AwsLbListener " + str(self.name) + " (" + str(self.port) + " " + str(self.protocol) + ")"

    def as_dict(self):
        return {
            'name': self.name,
            'port': self.port,
            'protocol': self.protocol,
            'default_action_type': self.default_action_type,
        }


class AwsS3Bucket(TfResource):
    def __init__(self, name, bucket):
        super().__init__(name)
        self.bucket = bucket

    def __repr__(self):
        return "AwsS3Bucket " + str(self.name) + " (" + str(self.bucket) + ")"

    def as_dict(self):
        return {
            'name': self.name,
            'bucket': self.bucket
        }
