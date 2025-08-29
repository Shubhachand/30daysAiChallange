#!/bin/bash

# Update system packages
apt-get update

# Install PortAudio headers so PyAudio can compile
apt-get install -y portaudio19-dev

# Upgrade pip
python3 -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
