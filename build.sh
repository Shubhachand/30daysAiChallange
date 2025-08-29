#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update && apt-get install -y portaudio19-dev libportaudio2

# Install python dependencies
pip install -r requirements.txt