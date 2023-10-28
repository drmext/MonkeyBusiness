#!/bin/bash

ver="3.12"
py="python$ver"

if ! command -v $py &> /dev/null
then
    echo "$py not found"
    exit
fi

if [ ! -d .venv/ ]
then
    $py -m venv .venv
fi

source .venv/bin/activate
$py -m pip install -r requirements.txt
$py pyeamu.py
