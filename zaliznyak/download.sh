#!/bin/bash

# Base URL for the raw files
BASE_URL="https://raw.githubusercontent.com/gramdict/zalizniak-2010/refs/heads/master/dictionary"

# Create local directory structure
mkdir -p "dictionary/Нарицательные"
mkdir -p "dictionary/Глаголы"

echo "Downloading common nouns (Нарицательные)..."
# Full Russian uppercase alphabet
ALPHABET="А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я"

for L in $ALPHABET; do
    # Using URL-encoded path for 'Нарицательные'
    URL="${BASE_URL}/%D0%9D%D0%B0%D1%80%D0%B8%D1%86%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5/${L}.txt"
    # -f fails silently on 404, -s is silent mode, -L follows redirects
    curl -s -f -L -o "dictionary/Нарицательные/${L}.txt" "$URL"
    if [ $? -eq 0 ]; then
        echo "  Saved ${L}.txt"
    fi
done

echo "Downloading verbs (Глаголы)..."
VERB_LETTERS="И Й Т Ь Я"

for L in $VERB_LETTERS; do
    # Using URL-encoded path for 'Глаголы'
    URL="${BASE_URL}/%D0%93%D0%BB%D0%B0%D0%B3%D0%BE%D0%BB%D1%8B/${L}.txt"
    curl -s -f -L -o "dictionary/Глаголы/${L}.txt" "$URL"
    if [ $? -eq 0 ]; then
        echo "  Saved ${L}.txt"
    fi
done

echo "Downloading proper names (Собственные)..."
# Using URL-encoded path for 'Собственные.txt'
PROPER_URL="${BASE_URL}/%D0%A1%D0%BE%D0%B1%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5.txt"
curl -s -f -L -o "dictionary/Собственные.txt" "$PROPER_URL"
if [ $? -eq 0 ]; then
    echo "  Saved Собственные.txt"
fi

echo "Download process complete."