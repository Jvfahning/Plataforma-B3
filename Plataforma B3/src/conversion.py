import yaml
import json
import uuid

def json_to_yaml(json_data):

    return yaml.dump(json_data, default_flow_style=False)

def yaml_to_json(yaml_data):

    return yaml.safe_load(yaml_data)

def generate_workflow_id():

    return str(uuid.uuid4())