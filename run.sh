#!/bin/bash

set -euo pipefail

echo "Generating dictionary files..."
python3 generate_dict.py

echo "Processing term bank..."
python3 term_bank.py

python3 utils/split_json.py term_bank_0.json dict/opr 25000

echo "Copying files..."
cp dict/*.json dict/opr/
cp dict/styles.css dict/opr/

mv dict/opr/opr-ru-en-index.json dict/opr/index.json

echo "Creating ZIP archive..."
(cd dict/opr && zip -q -r ../../opr-ru-en.zip ./*)

echo "Operation complete: opr-ru-en.zip created"