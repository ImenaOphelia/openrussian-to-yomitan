import yaml
import json
import argparse
import logging

logger = logging.getLogger(__name__)

CIRCLED_NUMBERS = {
    1: "①",  # U+2460
    2: "②",  # U+2461
    3: "③",  # U+2462
    4: "④",  # U+2463
    5: "⑤",  # U+2464
}

INDICATORS = [
    {
        'name': 'base',
        'condition': lambda s_dict: True,
        'action': lambda s_dict, base: (
            f"{s_dict['и']}{s_dict['у1']}/{s_dict['у2']}" 
            if 'у2' in s_dict and s_dict['у2'] 
            else f"{s_dict['и']}{s_dict['у1']}"
        )
    },
    {
        'name': 'ч:t',
        'condition': lambda s_dict: 'ч' in s_dict and s_dict['ч'] == 't',
        'action': lambda s_dict, base: (
            f"{s_dict['и']}*{s_dict['у1']}/{s_dict['у2']}" 
            if 'у2' in s_dict and s_dict['у2'] 
            else f"{s_dict['и']}*{s_dict['у1']}"
        )
    },
    {
        'name': 'ч2:t',
        'condition': lambda s_dict: 'ч2' in s_dict and s_dict['ч2'] == 't',
        'action': lambda s_dict, base: (
            f"{s_dict['и']}°{s_dict['у1']}/{s_dict['у2']}" 
            if 'у2' in s_dict and s_dict['у2'] 
            else f"{s_dict['и']}°{s_dict['у1']}"
        )
    },
    {
        "name": "ос",
        "condition": lambda s_dict: "ос" in s_dict,
        "action": lambda s_dict, base: base + CIRCLED_NUMBERS.get(s_dict["ос"], ""),
    },
    {
        "name": "фз:^к",
        "condition": lambda s_dict: "фз" in s_dict and s_dict["фз"] == "^к",
        "action": lambda s_dict, base: base + "✕",
    },
    {
        "name": "фн:^к.ем",
        "condition": lambda s, _=None: "фн" in s
            and any(tag == "^к.ем" for tag in s["фн"].split("|")),
        "action": lambda s, base: base + "⌧",
    },
    {
        "name": "фн:^с",
        "condition": lambda s, _=None: "фн" in s
            and any(tag == "^с" for tag in s["фн"].split("|")),
        "action": lambda s, base: base + "~",
    },
    {
        "name": "фп:.м",
        "condition": lambda s_dict: "фп" in s_dict and s_dict["фп"] == ".м",
        "action": lambda s_dict, base: base + "—",
    },
    {
        "name": "до",
        "condition": lambda s_dict: "до" in s_dict and s_dict["до"] is not None,
        "action": lambda s_dict, base: base + f"§{s_dict['до']}",
    },
]

RUSSIAN_VOWELS = "аеёиоуыэюя"

def remove_grave_accents(s):
    return s.replace("\u0300", "")

def remove_all_accents(s):
    return s.replace("\u0300", "").replace("\u0301", "")

def count_vowels(s):
    return sum(1 for char in s if char.lower() in RUSSIAN_VOWELS)

def process_accents(reading):
    reading = remove_grave_accents(reading)
    
    vowel_count = count_vowels(reading)
    
    if vowel_count == 1:
        return remove_all_accents(reading)
    
    return reading

def get_non_potential_form(group_str):
    alternatives = [alt.strip() for alt in group_str.split(",")]

    for alt in alternatives:
        if alt and not alt.endswith("-"):
            return alt

    if alternatives and alternatives[0].endswith("-"):
        return alternatives[0][:-1]

    return group_str


def get_lemma_ending(entry_dict):
    endings = entry_dict["п"].split(";")

    if entry_dict.get("мн") == "t" and len(endings) >= 7:
        result = get_non_potential_form(endings[6].strip())
        logger.debug("Pluralia tantum lemma ending: %s", result)
        return result

    if endings:
        result = get_non_potential_form(endings[0].strip())
        logger.debug("Regular lemma ending: %s", result)
        return result

    return ""


def extract_stem_number_and_suffix(ending):
    if not ending:
        return None, ending

    num_part = ""
    i = 0
    while i < len(ending) and ending[i].isdigit():
        num_part += ending[i]
        i += 1

    suffix = ending[i:]
    logger.debug("Extracted stem_num=%s, suffix=%s", num_part or None, suffix)
    return (int(num_part) if num_part else None, suffix)


def build_display_value(s_dict):
    display_value = None

    for indicator in INDICATORS:
        if indicator["condition"](s_dict):
            if indicator["name"] in ["base", "ч:t", "ч2:t"]:
                display_value = indicator["action"](s_dict, display_value)
            elif display_value is not None:
                display_value = indicator["action"](s_dict, display_value)
            logger.debug(
                "Applied indicator '%s', new display_value='%s'",
                indicator["name"], display_value
            )

    final = display_value or f"{s_dict['и']}{s_dict['у1']}"
    logger.debug("Final display value: %s", final)
    return final


def process_entry(lemma_key, entry_dict):
    if "п" not in entry_dict or "с" not in entry_dict:
        logger.warning("Skipping '%s' - missing 'п' or 'с' key", lemma_key)
        return None

    s_dict = entry_dict["с"]
    if "и" not in s_dict or "у1" not in s_dict:
        logger.warning("Skipping '%s' - missing 'и' or 'у1' in 'с'", lemma_key)
        return None

    ending = get_lemma_ending(entry_dict)
    stem_num, actual_suffix = extract_stem_number_and_suffix(ending)

    if stem_num is not None:
        stem_key = f"о{stem_num}"
        stem = entry_dict.get(stem_key, entry_dict.get("о", ""))
        reading = stem + actual_suffix
    else:
        reading = entry_dict.get("о", "") + ending

    reading = process_accents(reading)
    
    display_value = build_display_value(s_dict)

    result = [
        lemma_key,
        "freq",
        {
            "reading": reading,
            "frequency": {"value": 0, "displayValue": f"​{display_value}"} #zero-width space + built display value
        },
    ]
    logger.debug(
        "Processed entry '%s' → reading='%s', displayValue='%s'",
        lemma_key, reading, display_value
    )
    return result


def extract_entries(lemma, data):
    entries = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, list):
                entries.extend(extract_entries(lemma, item))
            elif isinstance(item, dict):
                entries.append(item)
    elif isinstance(data, dict):
        entries.append(data)
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_files", nargs="+", help="Input YAML files")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    all_entries = []
    for filename in args.input_files:
        logger.info("Loading file: %s", filename)
        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for lemma, entries in data.items():
            logger.debug("Extracting entries for lemma '%s'", lemma)
            extracted = extract_entries(lemma, entries)
            for entry_dict in extracted:
                entry = process_entry(lemma, entry_dict)
                if entry:
                    all_entries.append(entry)

    with open(args.output, "w", encoding="utf-8") as f_out:
        json.dump(all_entries, f_out, ensure_ascii=False, indent=2)

    logger.info(
        "Successfully converted %d entries to %s",
        len(all_entries), args.output
    )


if __name__ == "__main__":
    main()
