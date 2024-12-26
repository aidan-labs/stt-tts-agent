# ollama_handler.py

# Standard imports
import json
import logging
import subprocess
# Third-Party imports
import requests

# Set up logging to log errors
logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class OllamaHandler:
    def __init__(self, url, model):
        try:
            self.url = url
            self.model = model
            self.context = []
            self.check_ollama_status()
        except Exception as e:
            logging.error(f"Error during OllamaHandler initialization: {e}")

    # Check if Ollama is running
    def check_ollama_status(self):
        try:
            result = subprocess.run(['pgrep', 'Ollama'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                logging.info("Ollama is running")
            else:
                logging.warning("Ollama is not running, starting Ollama...")
                # Attempt to start Ollama
                subprocess.run(['open', '-a', 'Ollama'])
                logging.info("Ollama has been started.")

        except Exception as e:
            logging.error(f"Error checking or starting Ollama: {e}")

    def ask(self, prompt):
        logging.info(f"Sending prompt to Mistral:\n{prompt}")
        payload = {
            "model": self.model,
            "stream": True,
            "context": self.context,
            "prompt": prompt
        }
        try:
            response = requests.post(self.url, json=payload, headers={'Content-Type': 'application/json'}, stream=True)
            response.raise_for_status()
            full_response = ""

            for line in response.iter_lines():
                if line:
                    body = json.loads(line)
                    if 'response' in body:
                        full_response += body['response']
                    if 'context' in body:
                        self.context = body['context']

            return full_response.strip()
        except requests.RequestException as e:
            logging.error(f"Error communicating with Ollama: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in ask method: {e}")
