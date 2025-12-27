#!/bin/bash

# DOES NOT WORK FOR SOME REASON

set -euo pipefail

cd zaliznyak

echo "Checking for files..."
if [[ ! -f "zaliz_1.yml" ]]; then
    echo "zaliz_1.yml does not exist. Downloading..."
    curl -O "https://raw.githubusercontent.com/jurta/nlp-rus-zaliz/refs/heads/master/zaliz_1.yml"
else
    echo "zaliz_1.yml exists."
fi

if [[ ! -f "zaliz_2.yml" ]]; then
    echo "zaliz_2.yml does not exist. Downloading..."
    curl -O "https://raw.githubusercontent.com/jurta/nlp-rus-zaliz/refs/heads/master/zaliz_2.yml"
else
    echo "zaliz_2.yml exists."
fi

echo "Processing term bank..."
if [[ -d "../dict/zaliz" ]]; then
    echo "The directory exists."
else
    mkdir ../dict/zaliz
fi
source .venv/bin/activate
if [[ -f "term_meta_bank_0.json" ]]; then
    python3 split_json.py term_meta_bank_0.json ../dict/zaliz/ 1000
else
    python3 convert.py zaliz_1.yml zaliz_2.yml -o term_meta_bank_0.json && python3 split_json.py term_meta_bank_0.json ../dict/zaliz/ 1000
fi

echo "Copying files..."
cd ..
cp dict/zaliznyak-index.json dict/zaliz && mv dict/zaliz/zaliznyak-index.json dict/zaliz/index.json
today=$(date +"%Y.%m.%d")
jq --arg date "$today" '.revision = $date' dict/zaliz/index.json > dict/zaliz/temp.json && mv dict/zaliz/temp.json dict/zaliz/index.json

echo "Creating ZIP archive..."
(cd dict/zaliz && zip -q -r ../../zaliznyak.zip ./*)

echo "Operation complete: zaliznyak.zip created"
