#!/bin/bash
export CARGO_HOME=/tmp/cargo
mkdir -p $CARGO_HOME
pip install -r requirements.txt
pip install uvicorn
