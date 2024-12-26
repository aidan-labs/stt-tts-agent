# stt.py

# Standard imports
import logging
import queue
# Third-Party imports
import numpy as np
import pyaudio
import whisper
# Local imports
from config.config_loader import load_config

# Set up logging to log errors
logging.basicConfig(filename='errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to record audio
def record_audio(audio_queue, control_event, stop_event):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    p = pyaudio.PyAudio()

    while not stop_event.is_set():
        if control_event.is_set():  # Start recording when the event is set
            try:
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
                frames = []
                while control_event.is_set():  # Record while the control event remains set
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                stream.stop_stream()
                stream.close()
                
                # Combine audio chunks into a NumPy array and add to the queue
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) * (1 / 32768.0)
                audio_queue.put(audio_data)
            except Exception as e:
                logging.error(f"Error in record_audio: {e}")
    p.terminate()

# Function to transcribe audio
def transcribe_audio(audio_data):
    try:
        # Load Ollama configuration from config.yaml
        config = load_config()
        whisper_model_path = config['whisperRecognition']['modelPath']
        language = config['whisperRecognition']['lang']

        # Load the Whisper model
        model = whisper.load_model(whisper_model_path)
        
        # Transcribe
        result = model.transcribe(audio_data, language=language)
        return result.get("text", "").strip()
    except Exception as e:
        logging.error(f"Error in transcribe_audio: {e}")
        return ""

# Function to handle transcription in a separate thread
def transcription_thread(audio_queue, result_queue, ollama_handler, control_event, stop_event):
    while not stop_event.is_set():
        if control_event.is_set():  # Check if recording is active
            try:
                # Get audio data from the queue
                audio_data = audio_queue.get(timeout=1)
                transcription = transcribe_audio(audio_data)
                
                # Send transcription to Ollama for a response
                ollama_response = ollama_handler.ask(transcription)
                
                # Put the response in the result queue
                result_queue.put(ollama_response)
            except queue.Empty:
                pass
            except Exception as e:
                logging.error(f"Error in transcription_thread: {e}")
