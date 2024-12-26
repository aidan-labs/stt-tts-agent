# tts.py

# Standard imports
import logging
import subprocess
# Local imports
from config.config_loader import load_config

# Set up logging to log errors
logging.basicConfig(filename='errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load voice from config.yaml
config = load_config()
voice = config['conversation']['voice']

# Run the "say" command to speak the message
def tts(message):
    try:
        subprocess.run(["say", "-v", voice, message])
        return message
    except Exception as e:
        return None
    except Exception as e:
        logging.error(f"Unexpected error in tts function: {e}")
        return None

# Function to estimate the TTS duration based on words per minute
def estimate_tts_duration(message):
    try:
        words_per_minute = 154
        words_per_second = words_per_minute / 60.0
        # Count the number of words in the message
        word_count = len(message.split())
        # Estimate the duration by dividing word count by words per second
        estimated_duration_seconds = word_count / words_per_second
        return estimated_duration_seconds
    except Exception as e:
        logging.error(f"Unexpected error in estimate_tts_duration function: {e}")
        return None
