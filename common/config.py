import os

import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

for key, value in os.environ.items():
    config[key] = value
