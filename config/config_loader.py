# config_loader.py

# Standard
import logging
# Third-Party
import yaml

# Set up logging to log errors
logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError as e:
        logging.error(f"Configuration file 'config.yaml' not found: {e}")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file 'config.yaml': {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error loading config: {e}")
        return None
