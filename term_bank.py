import json
import unicodedata
import re
import os
from collections import OrderedDict

def remove_diacritics(text):
    nfd_text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd_text if not unicodedata.combining(c))

def build_glosses(translations):
    glosses = []
    for trans in translations:
        main_text = trans[0]
        if trans[3]:
            main_text += f" ({trans[3]})"
        
        trans_div = {"tag": "div", "content": [main_text]}
        
        if trans[1] and trans[2]:
            ex_count = 1
            summary_text = f"{ex_count} example" + ("s" if ex_count > 1 else "")
            
            example_content = {
                "tag": "div",
                "data": {"content": "extra-info"},
                "content": {
                    "tag": "div",
                    "data": {"content": "example-sentence"},
                    "content": [
                        {"tag": "div", "data": {"content": "example-sentence-a"}, "content": trans[1]},
                        {"tag": "div", "data": {"content": "example-sentence-b"}, "content": trans[2]}
                    ]
                }
            }
            
            details = {
                "tag": "details",
                "data": {"content": "details-entry-examples"},
                "content": [
                    {"tag": "summary", "data": {"content": "summary-entry"}, "content": summary_text},
                    example_content
                ]
            }
            
            trans_div["content"].append(details)
        
        glosses.append({"tag": "li", "content": [trans_div]})
    
    return glosses

def generate_term_bank(input_file):
    with open('props/types.json', 'r', encoding='utf-8') as f:
        types = json.load(f)
    with open('props/aspects.json', 'r', encoding='utf-8') as f:
        aspects = json.load(f)
    with open('props/genders.json', 'r', encoding='utf-8') as f:
        genders = json.load(f)
    with open('props/forms.json', 'r', encoding='utf-8') as f:
        forms = json.load(f)
    with open('props/noun_properties.json', 'r', encoding='utf-8') as f:
        noun_props = json.load(f)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    
    term_bank = []
    
    lemma_forms = {}
    
    for lemma, entries in dictionary.items():
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            
            tags = []
            overview = entry.get('overview', {})
            extra = entry.get('extra', {})
            
            if 'type' in overview:
                type_tag = types.get(overview['type'], {}).get('meaning', '')
                if type_tag:
                    tags.append(type_tag)
            
            if 'aspect' in extra:
                aspect_tag = aspects.get(extra['aspect'], {}).get('meaning', '')
                if aspect_tag:
                    tags.append(aspect_tag)
            
            if 'gender' in extra:
                gender_tag = genders.get(extra['gender'], {}).get('meaning', '')
                if gender_tag:
                    tags.append(gender_tag)
            
            if overview.get('type') == 'noun':
                for prop in ['animate', 'indeclinable', 'sg_only', 'pl_only']:
                    if prop in extra and extra[prop] is True:
                        prop_tag = noun_props.get(prop, {}).get('meaning', '')
                        if prop_tag:
                            tags.append(prop_tag)
            
            lemma_accented = overview.get('accented', lemma)
            lemma_entry = [
                lemma,
                lemma_accented,
                " ".join(tags),
                "",
                0,
                [],
                0,
                ""
            ]
            
            content = []
            
            if 'usage' in entry and entry['usage']:
                usage_details = {
                    "tag": "details",
                    "data": {"content": "details-entry-Usage"},
                    "content": [
                        {"tag": "summary", "data": {"content": "summary-entry"}, "content": "Usage"},
                        {"tag": "div", "data": {"content": "Usage-content"}, "content": entry['usage']}
                    ]
                }
                content.append({
                    "tag": "div",
                    "content": [usage_details]
                })
            
            if 'translations' in entry and entry['translations']:
                glosses = build_glosses(entry['translations'])
                content.append({
                    "tag": "ol",
                    "data": {"content": "glosses"},
                    "content": glosses
                })
            
            backlink = {
                "tag": "div",
                "data": {"content": "backlink"},
                "content": [{
                    "tag": "a",
                    "href": f"https://en.openrussian.org/ru/{lemma}",
                    "content": "OpenRussian"
                }]
            }
            content.append(backlink)
            
            lemma_entry[5] = [{
                "type": "structured-content",
                "content": content
            }]
            
            term_bank.append(lemma_entry)
            
            lemma_forms[lemma] = []
            if 'forms' in entry:
                for form_key, form_value in entry['forms'].items():
                    if not form_value:
                        continue
                    
                    rule_desc = forms.get(form_key, {}).get('meaning', form_key)
                    
                    inflection_entry = [
                        remove_diacritics(form_value),
                        form_value,
                        "non-lemma",
                        "",
                        0,
                        [[lemma, [rule_desc]]],
                        0,
                        ""
                    ]
                    
                    term_bank.append(inflection_entry)
                    lemma_forms[lemma].append(form_value)
    
    with open('term_bank_0.json', 'w', encoding='utf-8') as f:
        json.dump(term_bank, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "output/dict.json"
    generate_term_bank(input_file)