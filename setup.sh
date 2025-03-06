#!/bin/bash

# Update package lists
sudo apt-get update

# Install eSpeak for pyttsx3 (Text-to-Speech engine)
sudo apt-get install -y espeak

# Install other required packages
sudo apt-get install -y mpg321  # To play the audio output of gTTS

# Install Python dependencies
pip install -r requirements.txt
