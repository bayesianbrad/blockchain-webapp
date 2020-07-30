#!/usr/bin/env python3

from backend.chain import Blockchain
from backend.block import Block
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
import requests
import time
import json

# intialize flask application

from src.backend import app
blockchain = Blockchain()

# create an endpont for app to post a new transaction
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction"
        
    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)

    return "Success", 201

# endpoint to get the node's copy of the chain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

# endpoint to request the node's to get the uncomfirmed transactions to mine. 
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length =  len(blockchain.chain)
        consensus()
        # updates a the blockchain object globally.
        if chain_length == len(blockchain.chain):
             # announce the recently mixed block to the network
             announce_new_block(blockchain.last_block)
             
        return f"Block #{blockchain.last_block.index} is mined"


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

# create the decentralized network
# we need the data to be distributed among several nodes, and need them all to be maintain the blockchain. 

# contains the addresses of other participating members of the network

peers = set()

# endpoint to post new peers to the network
@app.route('/register_node', methods=["POST"])
def register_new_peers():
    # the host address to the peer node
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    
    # add the note to the peer list
    peers.add(node_address)

    # Return the blockchain to the newly registered node so that it can sync 
    return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the 'register node' endpoint to 
    register current node with the remote node specified in the request,
    and sync the blockchain as well with the remote node.
    """
    node_address = request.get_json()['node_address']
    if not node_address:
        return "Invalid data", 400
    
    data = {'node_address': request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + '/register_node',
                            data=json.dumps(data), headers=headers)
    
    # if response accepted
    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data['index'], 
                      block_data['transactions'],
                      block_data['timestamp'],
                      block_data['previous_hash'])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception(" the chain dump is tampered!!")
        else:
            # the block is a genesis block, no verification needed. This would be dangerous in wild implementations. 
            blockchain.append(block)
    return blockchain

def consensus():
    """
    A simple consensus algorithm. If a longer valid chain is found, 
    the chain is replaced with it. 
    """

    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get(f'{node}/chain')
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            # Londer valid chain found
            current_len = length
            longest_chain = chain
        
        if longest_chain:
            blockchain = longest_chain
            return True
        
        return False

        
# endpoint to poss a block has been mined by someone else to
# the node's chain. The node first verifies the block
# and then adds it to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data['index'], 
                block_data['transactions'],
                block_data['timestamp'],
                block_data['previous_hash'])
    proof = block_data['hash']
    added = blockchain.add_block(block,proof)

    if not added:
        return "The block was discarded by the node", 400
    
    return "Block added to the chain", 201

def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined. 
    Other blocks can simply verify the proof of work and add it to their respective chains. 
    :param block: [description]
    :type block: [type]
    """

    for peer in peers:
        url = f"{peers}add_block"
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))