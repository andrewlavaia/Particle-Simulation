import yaml

def load_config(file_string):
    with open(file_string) as f:
        dataMap = yaml.safe_load(f)
    return dataMap

def set_config(data):
    with open('config.yml', 'w') as outfile:
        yaml.safe_dump(data, outfile, default_flow_style=False)