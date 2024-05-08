import yaml
import json
import os

abs_path = os.environ["abs_path"]

background_config_path = os.path.join(abs_path, 'config/background.yaml')
control_json_path = os.path.join(abs_path, 'data/control_rig/control_type.json')

background_config = {}
control_json = {}

with open(background_config_path, 'r', encoding='utf-8') as file:
    background_config = yaml.safe_load(file)
with open(control_json_path, 'r', encoding='utf-8') as file:
    control_json = json.load(file)