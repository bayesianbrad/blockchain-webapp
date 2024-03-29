#!/usr/bin/env python3
import datetime
import json

import requests
from flask import render_template, redirect, request



from src.frontend import app

# Node in the blockchain network that our application will communicate with to fetch
# and add data. 
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8080"

posts = []

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the data, 
    and store it locally. 
    """
    get_chain_address = F"{CONNECTED_NODE_ADDRESS}/chain"
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)
        
        global posts  
        posts = sorted(content,
                        key=lambda k: k['timestamp'],
                        reverse=True)
@app.route('/')
def home():
    fetch_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application
    """

    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content
    }

    # Submit a tx
    new_tx_address = f"{CONNECTED_NODE_ADDRESS}/new_transaction"

    request.post(new_tx_address,
                 json=post_object, 
                 headers={'Content-type': 'application/json'})
    # return to homepage
    return redirect('/')



def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
    