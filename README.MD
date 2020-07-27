
# Building a blockchain app

## Steps
1. Store transactions into blocks
2. Add digital fingerprints to the blocks
3. Chain the Blocks
    - The hash of that previous block would change.
    - This will lead to a mismatch with the previous_hash field in the next block.
    - Since the input data to compute the hash of any block also consists of the previous_hash field, the hash of the next block will also change.
4. Implement a proof of work algorithm
5. Add blocks to the chain
    - The data has not been tampered with (the proof of work provided is correct).
    - The order of transactions is preserved (the previous_hash field of the block to be added points to the hash of the latest block in our chain).
    - Mining 
6. Create interfaces - i.e. RESTful API
7. Establish consensus and decentralization
    - Asking the remote node to add a new peer to its list of known peers.
    - Initializing the blockchain of the new node with that of the remote node.
    - Resyncing the blockchain with the network if the node goes off-grid.
    - Implement a consensus algorithm to agree on the longest valid chain
8. Build the application
