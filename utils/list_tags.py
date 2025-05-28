import json
import sys
from collections import defaultdict

def extract_unique_properties(data):
    unique_types = defaultdict(dict)
    unique_aspects = defaultdict(dict)
    unique_genders = defaultdict(dict)
    unique_forms = defaultdict(dict)
    unique_noun_properties = defaultdict(dict)

    for word, entries in data.items():
        for entry in entries:
            if 'overview' in entry and 'type' in entry['overview']:
                t = entry['overview']['type']
                unique_types[t] = {"meaning": ""}
            
            if 'extra' in entry:
                extra = entry['extra']
                if 'aspect' in extra:
                    a = extra['aspect']
                    unique_aspects[a] = {"meaning": ""}
                if 'gender' in extra:
                    g = extra['gender']
                    unique_genders[g] = {"meaning": ""}
                
                if 'animate' in extra:
                    unique_noun_properties['animate'] = {"meaning": ""}
                if 'indeclinable' in extra:
                    unique_noun_properties['indeclinable'] = {"meaning": ""}
                if 'sg_only' in extra:
                    unique_noun_properties['sg_only'] = {"meaning": ""}
                if 'pl_only' in extra:
                    unique_noun_properties['pl_only'] = {"meaning": ""}
            
            if 'forms' in entry:
                for form_key in entry['forms'].keys():
                    unique_forms[form_key] = {"meaning": ""}
    
    return unique_types, unique_aspects, unique_genders, unique_forms, unique_noun_properties

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_unique.py input.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    types, aspects, genders, forms, noun_props = extract_unique_properties(data)
    
    with open('props/types.json', 'w', encoding='utf-8') as f:
        json.dump(types, f, ensure_ascii=False, indent=2)
    
    with open('props/aspects.json', 'w', encoding='utf-8') as f:
        json.dump(aspects, f, ensure_ascii=False, indent=2)
    
    with open('props/genders.json', 'w', encoding='utf-8') as f:
        json.dump(genders, f, ensure_ascii=False, indent=2)
    
    with open('props/forms.json', 'w', encoding='utf-8') as f:
        json.dump(forms, f, ensure_ascii=False, indent=2)
    
    with open('props/noun_properties.json', 'w', encoding='utf-8') as f:
        json.dump(noun_props, f, ensure_ascii=False, indent=2)
    
    print("Extraction complete.")

if __name__ == "__main__":
    main()