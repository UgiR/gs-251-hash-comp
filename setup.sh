#!/usr/bin/env bash

# Prepare autograder environment

# Install Python dependencies declared in requirements.txt
apt-get install -y python python3-pip
pip3 install -r /autograder/source/requirements.txt

cp /autograder/source/config.yml /autograder
