#!/bin/bash

set -euo pipefail

DIST_DIR="../../assets/opr"
INDEX_FILE="$DIST_DIR/index.json"
ZIP_NAME="opr-ru-en.zip"
TODAY=$(date +"%Y.%m.%d")

for cmd in python3 jq zip; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is not installed." >&2
        exit 1
    fi
done

if [ -z "$( ls -A '../../assets/openrussian_public' )" ]; then
   echo "Downloading csv files..."
   python3 ../get_csv.py
else
   echo "Skipping csv download."
fi

echo "Generating dictionary files..."
python3 ../generate_dict.py

echo "Processing term bank..."
python3 ../term_bank.py

mkdir -p "$DIST_DIR"
python3 ../utils/split_json.py ../../assets/term_bank_0.json "$DIST_DIR" 25000

echo "Copying assets..."
cp ../../assets/*.json "$DIST_DIR/"
cp ../../assets/styles.css "$DIST_DIR/"

rm -f "$DIST_DIR/zaliznyak-index.json"
rm -f "$DIST_DIR/zaliznyak-prefix-index.json"
rm -f "$DIST_DIR/dict.json"
rm -f "$DIST_DIR/term_bank_0.json"
mv "$DIST_DIR/opr-ru-en-index.json" "$INDEX_FILE"

echo "Updating revision date..."
jq --arg date "$TODAY" '.revision = $date' "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"

echo "Creating ZIP archive..."
pushd "$DIST_DIR" > /dev/null
zip -q -r "../../dist/$ZIP_NAME" ./*
cp "$INDEX_FILE" ../../dist/
mv ../../dist/index.json ../../dist/opr-ru-en-index.json
popd > /dev/null

rm -f ../../assets/openrussian_public/*.csv

echo "Operation complete: $ZIP_NAME created"