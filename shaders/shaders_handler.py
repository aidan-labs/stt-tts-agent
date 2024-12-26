# shaders_handler.py

# Standard
import logging
import os
# Third-Party
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Set up logging configuration
logging.basicConfig(filename='errors.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Dynamically get the current script's directory and define shader paths
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
VERTEX_SHADER_PATH = os.path.join(SCRIPT_DIR, "vertex_shader.glsl")
FRAGMENT_SHADER_PATH = os.path.join(SCRIPT_DIR, "fragment_shader.glsl")

def setup_shaders():
    try:
        # Load and compile shaders
        with open(VERTEX_SHADER_PATH, 'r') as f:
            vertex_shader_code = f.read()
        
        with open(FRAGMENT_SHADER_PATH, 'r') as f:
            fragment_shader_code = f.read()

        # Compile the shaders
        shader_program = compileProgram(
            compileShader(vertex_shader_code, GL_VERTEX_SHADER),
            compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
        )

        # Set up vertex buffer
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ], dtype=np.float32)
        
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        position = glGetAttribLocation(shader_program, "in_vert")
        glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(position)

        # Get uniform locations
        resolution_uniform = glGetUniformLocation(shader_program, "u_resolution")
        time_uniform = glGetUniformLocation(shader_program, "u_time")
        
        return {
            "shader_program": shader_program,
            "resolution_uniform": resolution_uniform,
            "time_uniform": time_uniform
        }

    except Exception as e:
        logging.error(f"Error setting up shaders: {e}")
        raise
