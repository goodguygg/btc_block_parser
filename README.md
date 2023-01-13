# btc_block_parser
This is a simple python script which parses btc blockchain and creates a .json file which contains onchain data starting from the genesis block. 

Usage is also pretty simple:

$ python main.py 

Begins parsing data, it updates and saves the .json file each consecutive multithreaded call and if you need to stop it just precc Ctrl-C.

To check if all the blocks are in order and to get them in order use

$ python main.py check

If you need to change the number of threads go to line 95 and change it there, consider running this on a powerful machine with a lot of threads, otherwise it may take a while.
