import json
import unicodedata
import re
import os
import urllib.parse


def remove_diacritics(text):
    if not text:
        return ""
    nfd_text = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd_text if not unicodedata.combining(c))


def highlight_terms(text, terms):
    if not text or not terms:
        return [text]

    search_terms = set()
    for t in terms:
        if t:
            search_terms.add(re.escape(t))
            search_terms.add(re.escape(remove_diacritics(t)))

    sorted_terms = sorted(list(search_terms), key=len, reverse=True)

    pattern = re.compile(rf"\b({'|'.join(sorted_terms)})\b", re.IGNORECASE)

    parts = pattern.split(text)

    content_list = []
    lookup_set = {remove_diacritics(t).lower() for t in terms}

    for part in parts:
        if not part:
            continue

        clean_part = remove_diacritics(part).lower()
        if clean_part in lookup_set:
            content_list.append(
                {
                    "tag": "span",
                    "data": {"content": "example-highlight"},
                    "content": part,
                }
            )
        else:
            content_list.append(part)

    return content_list


def build_glosses(translations, all_forms):
    glosses = []
    for trans in translations:
        main_text = trans[0]

        if len(trans) > 3 and trans[3]:
            extra_info = trans[3].lower().strip()
            extra_info = re.sub(r"[.\!?,\s]+$", "", extra_info)
            main_text += f" ({extra_info})"

        trans_div = {"tag": "div", "content": [main_text]}

        if trans[1] and trans[2]:
            ex_count = 1
            summary_text = f"{ex_count} example" + ("s" if ex_count > 1 else "")

            example_a = highlight_terms(trans[1], all_forms)

            example_content = {
                "tag": "div",
                "data": {"content": "extra-info"},
                "content": {
                    "tag": "div",
                    "data": {"content": "example-sentence"},
                    "content": [
                        {
                            "tag": "div",
                            "data": {"content": "example-sentence-a"},
                            "content": example_a,
                        },
                        {
                            "tag": "div",
                            "data": {"content": "example-sentence-b"},
                            "content": trans[2],
                        },
                    ],
                },
            }

            details = {
                "tag": "details",
                "data": {"content": "details-entry-examples"},
                "content": [
                    {
                        "tag": "summary",
                        "data": {"content": "summary-entry"},
                        "content": summary_text,
                    },
                    example_content,
                ],
            }

            trans_div["content"].append(details)

        glosses.append({"tag": "li", "content": [trans_div]})

    return glosses


def generate_term_bank(input_file):
    prop_files = {
        "types": "props/types.json",
        "aspects": "props/aspects.json",
        "genders": "props/genders.json",
        "forms": "props/forms.json",
        "noun_props": "props/noun_properties.json",
    }

    props = {}
    for key, path in prop_files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                props[key] = json.load(f)
        else:
            props[key] = {}

    with open(input_file, "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    term_bank = []

    for lemma, entries in dictionary.items():
        for entry in entries:
            if not isinstance(entry, dict):
                continue

            translations = entry.get("translations", [])
            if not translations:
                continue

            forms_dict = entry.get("forms", {})
            all_word_variants = [lemma] + [
                v for v in forms_dict.values() if isinstance(v, str) and v
            ]

            tags = []
            overview = entry.get("overview", {})
            extra = entry.get("extra", {})

            if "type" in overview:
                tag = props["types"].get(overview["type"], {}).get("meaning", "")
                if tag:
                    tags.append(tag)
            if "aspect" in extra:
                tag = props["aspects"].get(extra["aspect"], {}).get("meaning", "")
                if tag:
                    tags.append(tag)
            if "gender" in extra:
                tag = props["genders"].get(extra["gender"], {}).get("meaning", "")
                if tag:
                    tags.append(tag)
            if overview.get("type") == "noun":
                for p in ["animate", "indeclinable", "sg_only", "pl_only"]:
                    if extra.get(p) is True:
                        tag = props["noun_props"].get(p, {}).get("meaning", "")
                        if tag:
                            tags.append(tag)

            lemma_accented = overview.get("accented", lemma)
            content = []

            if entry.get("usage"):
                usage_details = {
                    "tag": "details",
                    "data": {"content": "details-entry-Usage"},
                    "content": [
                        {
                            "tag": "summary",
                            "data": {"content": "summary-entry"},
                            "content": "Usage",
                        },
                        {
                            "tag": "div",
                            "data": {"content": "Usage-content"},
                            "content": entry["usage"],
                        },
                    ],
                }
                content.append({"tag": "div", "content": [usage_details]})

            content.append(
                {
                    "tag": "ol",
                    "data": {"content": "glosses"},
                    "content": build_glosses(translations, all_word_variants),
                }
            )

            encoded_lemma = urllib.parse.quote(lemma)
            content.append(
                {
                    "tag": "div",
                    "data": {"content": "backlink"},
                    "content": [
                        {
                            "tag": "a",
                            "href": f"https://en.openrussian.org/ru/{encoded_lemma}",
                            "content": "OpenRussian",
                        }
                    ],
                }
            )

            term_bank.append(
                [
                    lemma,
                    lemma_accented,
                    " ".join(tags),
                    "",
                    0,
                    [{"type": "structured-content", "content": content}],
                    0,
                    "",
                ]
            )

            for form_key, form_value in forms_dict.items():
                if not form_value or not isinstance(form_value, str):
                    continue
                rule_desc = props["forms"].get(form_key, {}).get("meaning", form_key)
                term_bank.append(
                    [
                        remove_diacritics(form_value),
                        form_value,
                        "non-lemma",
                        "",
                        0,
                        [[lemma, [rule_desc]]],
                        0,
                        "",
                    ]
                )

    with open("term_bank_0.json", "w", encoding="utf-8") as f:
        json.dump(term_bank, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    input_file = "output/dict.json"
    if os.path.exists(input_file):
        generate_term_bank(input_file)
