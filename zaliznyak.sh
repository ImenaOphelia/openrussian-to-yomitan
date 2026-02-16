#!/bin/bash

set -euo pipefail

ROOT_DIR="$(pwd)"
SRC_DIR="zaliznyak"
DIST_DIR="$ROOT_DIR/dict/zaliz"
TODAY=$(date +"%Y.%m.%d")

for cmd in python3 jq zip; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is not installed." >&2
        exit 1
    fi
done

if [[ ! -d "$SRC_DIR" ]]; then
    echo "Error: Directory $SRC_DIR not found." >&2
    exit 1
fi

pushd "$SRC_DIR" > /dev/null

echo "Checking for dictionary source..."
if [[ ! -d "dictionary" ]]; then
    sh download.sh
fi

echo "Converting JSON..."
if [[ ! -f "zaliznyak_index_only.json" ]]; then
    python3 convert.py
fi

echo "Splitting JSON files..."
mkdir -p "$DIST_DIR/index" "$DIST_DIR/prefix"
python3 split_json.py zaliznyak_index_only.json "$DIST_DIR/index" 1000
python3 split_json.py zaliznyak_prefix_and_index.json "$DIST_DIR/prefix" 1000

popd > /dev/null

for type in "index" "prefix"; do
    TARGET_DIR="$DIST_DIR/$type"
    
    if [[ "$type" == "prefix" ]]; then
        SRC_INDEX_FILE="$ROOT_DIR/dict/zaliznyak-prefix-index.json"
        ZIP_NAME="zaliznyak-prefix.zip"
    else
        SRC_INDEX_FILE="$ROOT_DIR/dict/zaliznyak-index.json"
        ZIP_NAME="zaliznyak.zip"
    fi

    echo "Configuring $type folder using $(basename "$SRC_INDEX_FILE")..."

    if [[ ! -f "$SRC_INDEX_FILE" ]]; then
        echo "Warning: Source index $SRC_INDEX_FILE not found, skipping $type."
        continue
    fi

    jq --arg date "$TODAY" '.revision = $date' "$SRC_INDEX_FILE" > "$TARGET_DIR/index.json"

    echo "Creating $ZIP_NAME..."
    pushd "$TARGET_DIR" > /dev/null
    zip -q -r "$ROOT_DIR/$ZIP_NAME" ./*
    popd > /dev/null
done

echo "Operation complete: zaliznyak.zip and zaliznyak-prefix.zip are in $ROOT_DIR"