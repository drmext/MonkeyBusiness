#!/bin/bash

ver="3.11"
py="python$ver"

if ! command -v $py &> /dev/null
then
    echo "$py not found"
    exit
fi

if [ -d .venv/ ]
then
    source .venv/bin/activate
    $py pyeamu.py
else
    $py -m venv .venv
    source .venv/bin/activate
    $py -m pip install -U -r requirements.txt
    $py pyeamu.py
fi
