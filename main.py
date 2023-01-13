# This file collects data from the BTC chain and stores it in a .json file

import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

# link to the documentation for the API => https://www.blockchain.com/explorer/api/blockchain_api 
# Gets the block data from the API by block height
def get_block_data(block_height):
    url = f"https://blockchain.info/block-height/{block_height}?format=json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()["blocks"]

# Sorts blocks by height
def sort_blocks_by_height(file_path):
    with open(file_path) as f:
        data = json.load(f)
    # Sort the blocks by the 'height' key
    sorted_data = sorted(data, key=lambda block: block['height'])
    # write the sorted data to a new file
    with open(file_path, "w") as outfile:
        json.dump(sorted_data, outfile)
    print("blocks sorted by height")

# Begins parsing data from chain using a different number of threads. 
def btc_block_data(threads=8, file='all_blocks.json'):
    # Try to open existing all_blocks.json file
    try:
        sort_blocks_by_height(file)
        with open(file, 'r') as f:
            data = json.load(f)
            # Get the current height from the last block
            curr_height = data[-1]['height']
            f.close()
    except (FileNotFoundError, IndexError):
        # If the file doesn't exist or is empty
        # start fetching blocks from height 0
        curr_height = 0
        data = []

    while True:
        # Create a ThreadPoolExecutor with 8 worker threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit the get_block_data function as a task to the executor
            # passing in the current block height as an argument
            future_to_block = {executor.submit(get_block_data, block_height): block_height for block_height in range(curr_height, curr_height+threads)}
            # Use as_completed to get the results of the tasks as they complete
            for future in as_completed(future_to_block):
                block_height = future_to_block[future]
                try:
                    blocks = future.result()
                except Exception as exc:
                    print(f'{block_height} generated an exception: {exc}')
                else:
                    if blocks:
                        data += blocks
                        print(f'block height {block_height} fetched')

        curr_height += threads
        # Saving the blocks periodically
        with open(file, "w") as outfile:
            json.dump(data, outfile)
        print(f"Block height: {curr_height} JSON file updated with new block information.")

# checks if all of the blocks are in order sorting them previously
def check_all_blocks(file_path):
    x = 0
    y = 0
    prev_height = -1
    sort_blocks_by_height(file_path)
    with open(file_path, 'r') as f:
        data = json.load(f)
        for block in data:
            x += 1
            if prev_height > block['height']:
                print(f"heights not in order: {prev_height} and {block['height']}")
                raise Exception("heights not in order")
            prev_height = block['height']
            if block['n_tx'] > 1:
                y += 1
    print(f"num of blocks in file: {x}, num of blocks with more than 1 transaction: {y}, all blocks are in order: True")

def main():
    # you may change the directory here if you need
    main_dir = os.path.dirname(os.getcwd())
    path_to_file = os.path.join(main_dir, 'all_blocks.json')
    if len(sys.argv) > 1:
        if sys.argv[1] == 'check':
            check_all_blocks(path_to_file)
            return
    btc_block_data(threads=8, file=path_to_file)

if __name__ == "__main__":
    main()

