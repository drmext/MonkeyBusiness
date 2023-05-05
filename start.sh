#!/bin/bash

if ! command -v python3.11 &> /dev/null
then
    echo "python3.11 not found"
    exit
fi

if [ -e .venv/lib/python3.11/site-packages/ujson*.so ]
then
    source .venv/bin/activate
    python pyeamu.py
else
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -U -r requirements.txt
    python pyeamu.py
fi
