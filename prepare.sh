#!/bin/bash

VENV_POINT="env"

sudo apt-get update

# Install python3
if ! command -v python3 &> /dev/null
then
    sudo apt-get install python3
fi

# Install pip
if ! command -v pip3 &> /dev/null
then
    sudo apt-get install python3-pip
fi

# Create virtual environment
if [ ! -d "$VENV_POINT" ]; then
    python3 -m venv $VENV_POINT
else
    echo "Virtual environment already exists"
fi


source $VENV_POINT/bin/activate
pip3 install -r requirements.txt


read -p "Do you want to run the Python script? (y/n) " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    python3 teneo_cli.py
else
    echo "For run the Python script, run the command: python3 teneo_cli.py"
fi
