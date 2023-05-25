import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'rt') as f:
            d = json.load(f)
            for key, value in d.items():
                globals()[key] = value
    except:
        pass
