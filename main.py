# main.py

# Standard imports
import logging
import multiprocessing
import queue
import threading
# Third-Party imports
import numpy as np
import pygame
from OpenGL.GL import *
# Local imports
from agent.ollama_handler import OllamaHandler
from agent.stt import record_audio, transcription_thread
from agent.tts import tts, estimate_tts_duration
from shaders.shaders_handler import setup_shaders
from config.config_loader import load_config

# Set up logging to log errors
logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to handle the pulse effect
def handle_pulse(pulse_time, pulse_durations=None, pulse_intervals=None):
    pulse_count = 0  # Number of pulses
    pulse_factor = 0.0
    pulse_durations = pulse_durations or [400, 600, 400, 1000, 400]  # Alternating speeds
    pulse_intervals = pulse_intervals or [800, 800, 800, 800]  # Time between pulses

    pulse_time_elapsed = pygame.time.get_ticks() - pulse_time
    pulse_duration = pulse_durations[pulse_count % len(pulse_durations)]  # Get next pulse duration
    pulse_factor = 0.5 * (1 + np.sin(2 * np.pi * pulse_time_elapsed / pulse_duration))  # Pulse effect

    # If the interval between pulses has passed, go to the next pulse
    if pulse_time_elapsed > pulse_intervals[pulse_count % len(pulse_intervals)]:
        pulse_time = pygame.time.get_ticks()  # Reset pulse time for next pulse
        pulse_count += 1  # Increment pulse count
    
    # Smooth fade-out of the pulse effect
    if pulse_factor > 0.0:
        fade_time_elapsed = pygame.time.get_ticks() - pulse_time
        if fade_time_elapsed < 1500:  # Fade-out time
            pulse_factor *= (1 - fade_time_elapsed / 1500)
        else:
            pulse_factor = 0.0
    
    return pulse_factor, pulse_time

def main():
    try:
        # Load the configuration from config.yaml
        config = load_config()
        if config is None:
            logging.error("Configuration failed to load.")
            return

        greeting_message = config['conversation']['greeting']
        
        # Initialize pulse related variables
        pulse_active = False
        pulse_time = 0
        pulse_end_time = 0

        if greeting_message:
            # Trigger TTS and pulse when greeting message is set
            pulse_active = True
            pulse_time = pygame.time.get_ticks()  # Reset pulse time when greeting is received

            # Estimate TTS duration based on the number of words in the response
            tts_duration = estimate_tts_duration(greeting_message)
            pulse_end_time = pygame.time.get_ticks() + int(tts_duration * 1000)  # Set pulse stop time

            # Start the TTS in a new thread
            threading.Thread(target=tts, args=(greeting_message,)).start()

    except Exception as e:
        logging.error(f"Error during greeting message setup: {e}")
        return

    try:
        # Initialize ollama_handler and pygame setup
        ollama_model = config['ollama']['model']
        ollama_url = config['ollama']['url']
        ollama_handler = OllamaHandler(url=ollama_url, model=ollama_model)

        # Pygame window config
        pygame.init()
        logo_path = "agent/logo.png"
        logo = pygame.image.load(logo_path)
        pygame.display.set_icon(logo)
        pygame.display.set_mode((300, 300), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Agent")

        # Load shaders
        shader_data = setup_shaders()

        glUseProgram(shader_data["shader_program"])
        resolution = shader_data["resolution_uniform"]
        time_uniform = shader_data["time_uniform"]

        # Get the uniform location for the pulse factor
        pulse_factor_uniform = glGetUniformLocation(shader_data["shader_program"], "u_pulse_factor")

        audio_queue = multiprocessing.Queue()
        control_event = multiprocessing.Event()
        stop_event = multiprocessing.Event()
        result_queue = queue.Queue()

        # Start audio recording process
        recording_process = multiprocessing.Process(target=record_audio, args=(audio_queue, control_event, stop_event))
        recording_process.start()

        # Start transcription and Ollama query in a background thread
        transcription_process = threading.Thread(target=transcription_thread, args=(audio_queue, result_queue, ollama_handler, control_event, stop_event))
        transcription_process.start()

        start_time = pygame.time.get_ticks()
        running = True

        # Main loop where the transcription is sent to Ollama and response is spoken
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    control_event.set()  # Start recording when spacebar is pressed
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    control_event.clear()  # Stop recording when spacebar is released

            # Get the current time in seconds
            current_time = (pygame.time.get_ticks() - start_time) / 1000.0

            # Handle pulse effect if active
            if pulse_active:
                pulse_factor, pulse_time = handle_pulse(pulse_time)

                # Stop pulse after TTS duration for the greeting message
                if pygame.time.get_ticks() > pulse_end_time:
                    pulse_active = False

                # Pass the pulse factor to the shader
                glUniform1f(pulse_factor_uniform, pulse_factor)

            # Handle Ollama response in the result queue
            try:
                if not result_queue.empty():
                    ollama_response = result_queue.get_nowait()

                    # Trigger TTS and pulse when Ollama response is received
                    pulse_active = True
                    pulse_time = pygame.time.get_ticks()  # Reset pulse time when triggered

                    # Estimate TTS duration based on the number of words in the response
                    tts_duration = estimate_tts_duration(ollama_response)
                    pulse_end_time = pygame.time.get_ticks() + int(tts_duration * 1000)  # Set pulse stop time

                    # Start the TTS in a new thread
                    tts_thread = threading.Thread(target=tts, args=(ollama_response,))
                    tts_thread.start()

            except queue.Empty:
                pass

            width, height = pygame.display.get_surface().get_size()
            glViewport(0, 0, width, height)
            glClear(GL_COLOR_BUFFER_BIT)
            glUniform2f(resolution, width, height)
            glUniform1f(time_uniform, current_time)
            glDrawArrays(GL_TRIANGLES, 0, 6)
            pygame.display.flip()

        stop_event.set()
        recording_process.terminate()
        transcription_process.join()  # Ensure transcription thread finishes
        recording_process.join()
        pygame.quit()

    except Exception as e:
        logging.error(f"Error during main execution: {e}")

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn")
        main()
    except Exception as e:
        logging.error(f"Error during main execution: {e}")
