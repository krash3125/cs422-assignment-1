#!/bin/bash

set -e

if [ ! -d ".venv" ]; then
    echo "Making venv"
    python3.11 -m venv .venv
fi

# activate venv
source .venv/bin/activate

# install reqs
echo "Installing requirements.txt"
pip install -r requirements.txt > /dev/null


echo "----------------------------------------------"

scripts=("ping-test.py" "geo-loc.py" "traceroute.py" "matplotlib-gen.py")

for script in "${scripts[@]}"
do
    echo "Running $script"
    python "$script"
done
