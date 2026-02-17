#!/bin/bash

set -euo pipefail

DIST_DIR="dict/opr"
INDEX_FILE="$DIST_DIR/index.json"
ZIP_NAME="opr-ru-en.zip"
TODAY=$(date +"%Y.%m.%d")

for cmd in python3 jq zip; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is not installed." >&2
        exit 1
    fi
done

if [ -z "$( ls -A 'openrussian_public' )" ]; then
   echo "Downloading csv files..."
   python3 get_csv.py
else
   echo "Skipping csv download."
fi

echo "Generating dictionary files..."
python3 generate_dict.py

echo "Processing term bank..."
python3 term_bank.py

mkdir -p "$DIST_DIR"
python3 utils/split_json.py term_bank_0.json "$DIST_DIR" 25000

echo "Copying assets..."
cp dict/*.json "$DIST_DIR/"
cp dict/styles.css "$DIST_DIR/"

rm -f "$DIST_DIR/zaliznyak-index.json"
mv "$DIST_DIR/opr-ru-en-index.json" "$INDEX_FILE"

echo "Updating revision date..."
jq --arg date "$TODAY" '.revision = $date' "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"

echo "Creating ZIP archive..."
pushd "$DIST_DIR" > /dev/null
zip -q -r "../../$ZIP_NAME" ./*
popd > /dev/null

rm -f oepnrussian_public/*.csv

echo "Operation complete: $ZIP_NAME created"