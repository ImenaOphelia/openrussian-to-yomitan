# forgot to add this to the main code
import json
import os
import sys

def split_large_json(input_file, output_folder, chunk_size):
    os.makedirs(output_folder, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)
        
        if not isinstance(data, list):
            raise ValueError("Input JSON must be an array of items.")
        
        total_items = len(data)
        num_chunks = (total_items + chunk_size - 1) // chunk_size

        print(f"Total items in JSON file: {total_items}")
        print(f"With a chunk size of {chunk_size}, this will create approximately {num_chunks} files.")
        proceed = input("Do you want to proceed? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation canceled.")
            return

        for i in range(0, total_items, chunk_size):
            chunk = data[i:i + chunk_size]
            chunk_file = os.path.join(output_folder, f"term_meta_bank_{i // chunk_size + 1}.json")
            
            with open(chunk_file, 'w', encoding='utf-8') as outfile:
                json.dump(chunk, outfile, indent=2, ensure_ascii=False)
            
            print(f"Saved {len(chunk)} items to {chunk_file}")

    print("Splitting complete.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python split_json.py <input_file> <output_folder> <chunk_size>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_folder = sys.argv[2]
    try:
        chunk_size = int(sys.argv[3])
        if chunk_size <= 0:
            raise ValueError
    except ValueError:
        print("Chunk size must be a positive integer.")
        sys.exit(1)
    
    split_large_json(input_file, output_folder, chunk_size)