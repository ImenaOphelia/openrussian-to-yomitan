import os
import re
import json

INPUT_DIR = 'dictionary'
OUTPUT_FILE_1 = 'zaliznyak_index_only.json'
OUTPUT_FILE_2 = 'zaliznyak_prefix_and_index.json'
ZERO_WIDTH_SPACE = '\u200B'

def clean_word(text):
    """Removes stress marks but keeps ё."""
    return text.replace('\u0301', '')

def parse_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    parts = line.split(maxsplit=1)
    if len(parts) < 2:
        return None
    
    raw_lemma = parts[0]
    rest = parts[1]

    if '/' in raw_lemma:
        raw_lemma = raw_lemma.split('/')[-1]

    reading = raw_lemma
    word = clean_word(reading)

    gram_part = re.split(r'\(|_', rest)[0].strip()

    match = re.search(r'(\d|<|⌧|◑|△|мс-п)', gram_part)
    
    if match:
        split_idx = match.start()
        prefix = gram_part[:split_idx].strip()
        index_raw = gram_part[split_idx:].strip()
        index = index_raw.replace(' ', '')
    else:
        prefix = ""
        index = gram_part.replace(' ', '')

    return {
        "word": word,
        "reading": reading,
        "prefix": prefix,
        "index": index
    }

def process_dictionary():
    output1_data = []
    output2_data = []

    for root, dirs, files in os.walk(INPUT_DIR):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parsed = parse_line(line)
                        if not parsed:
                            continue

                        output1_data.append([
                            parsed["word"],
                            "freq",
                            {
                                "reading": parsed["reading"],
                                "frequency": {
                                    "value": 0,
                                    "displayValue": f"{ZERO_WIDTH_SPACE}{parsed['index']}"
                                }
                            }
                        ])

                        combined_val = f"{parsed['prefix']} {parsed['index']}".strip()
                        output2_data.append([
                            parsed["word"],
                            "freq",
                            {
                                "reading": parsed["reading"],
                                "frequency": {
                                    "value": 0,
                                    "displayValue": f"{ZERO_WIDTH_SPACE}{combined_val}"
                                }
                            }
                        ])

    with open(OUTPUT_FILE_1, 'w', encoding='utf-8') as f:
        json.dump(output1_data, f, ensure_ascii=False, indent=2)

    with open(OUTPUT_FILE_2, 'w', encoding='utf-8') as f:
        json.dump(output2_data, f, ensure_ascii=False, indent=2)

    print(f"Done! Created {OUTPUT_FILE_1} and {OUTPUT_FILE_2}")

if __name__ == "__main__":
    process_dictionary()