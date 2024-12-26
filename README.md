<video src="https://github.com/user-attachments/assets/3efe981e-ff59-469d-b071-228609499822" controls></video>
# Project Overview
<small>
This project is a locally hosted AI agent with a GUI that uses speech-to-text and text-to-speech. It takes advantage of Ollama and LLMs (llama3.2:1b) to run entirely offline.
</small>

---
# Installation and Running

1. **Install Dependencies and Setup**:
   - Install Ollama by visiting [Ollama's website](https://ollama.com).
   - Download the llama3.2:1b model using the command:
       ```bash
       ollama pull llama3.2:1b
       ```
   - Download an OpenAI Whisper Model (by default, the `config.yaml` is set to use `base.en.pt`) by referring to this [Whisper model discussion](https://github.com/openai/whisper/discussions/63#discussioncomment-3798552).
   - Clone this repository somewhere on your system.
   - Place the Whisper model in a `/whisper` directory in the repo root folder.
   - Create a virtual environment in the root directory (`stt-tts-agent/`) to isolate dependencies:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     source venv/bin/activate
     ```
   - For Apple Silicon support of the PyAudio library, you’ll need to install Homebrew and run:
     ```bash
     brew install portaudio
     ```
   - Install required dependencies by running:
     ```bash
     python3 requirements.py
     ```
   - Run the application with the following command:
     ```bash
     python3 main.py
     ```
---
# Execution Flow
![stt-tts-agent-flow-chart](https://github.com/user-attachments/assets/c00f008a-5781-46c3-9f43-5c91b9d6214c)
1. `main.py` - The Main Controller
   - Orchestrates the application’s flow by handling:
     - **Greeting Message**: It starts by using the `tts.py` script to speak the greeting message defined in `config.yaml`.
     - **Pulse Effect**: Uses OpenGL shaders to generate a visual pulse effect during the TTS process.
     - **Recording**: Manages audio recording and transcription through `stt.py`. Users record messages by **holding the spacebar** and release it to stop the recording.
     - **Ollama API Interaction**: Sends the transcribed text to Ollama and gets a response, which is then spoken using TTS.

      The `main.py` script heavily relies on **multithreading and multiprocessing** to handle multiple tasks simultaneously, such as recording, transcription, and rendering the pulse effect.

2. `stt.py` - Speech-to-Text
   -  This script relies on **multithreading** to separate the audio recording and transcription processes. The transcription thread runs independently, allowing the application to continue recording audio while simultaneously transcribing previous recordings.
      - **record_audio**: Records audio from the microphone and puts the data into a queue. The audio is recorded when the user **holds the spacebar** and stops when the spacebar is released.
      - **transcribe_audio**: Uses the Whisper model (loaded from `whisper/base.en.pt`) to transcribe the audio into text.
      - **transcription_thread**: Runs in a background thread, consuming audio data from the queue, transcribing it, and then sending the result to the Ollama API.

3. `tts.py` - Text-to-Speech
   - The Text-to-Speech system uses multithreading to manage synchronized interactions like playing the greeting message while the pulse effect is rendered.
      - **tts**: Uses the `say` command to convert text into speech using the voice specified in `config.yaml`.
      - **estimate_tts_duration**: Estimates the duration of the Text-to-Speech output based on the number of words in the message.

4. `ollama_handler.py` - Ollama Communication
   - The Ollama handler is responsible for interacting with the local Ollama HTTP server, ensuring that the transcribed text is processed asynchronously.
      - **OllamaHandler**: Checks if Ollama is running and sends prompts (e.g., transcribed speech) to Ollama, receiving a response to be spoken by the TTS system.

5. `shaders_handler.py` - Shader Management
   - The shaders run synchronously with the TTS process to render the visual pulse effect, but they also interact with the main script’s thread to ensure the effect is in sync with the application flow.
      - **setup_shaders**: Loads and compiles the GLSL shaders for OpenGL rendering. The shaders are used to create the pulse effect seen in the graphical interface.
---
# Acknowledgements

This project relied heavily on the following references:

- **[Ollama Voice](https://github.com/maudoin/ollama-voice)** by maudoin for inspiration and implementation details regarding Ollama integration.
- **[OpenGL Pulse Effect](https://codepen.io/Hyperplexed/full/wvbyoLJ)** by Hyperplexed, which was used for the GLSL shaders.
