#!/usr/bin/env python3
import time
import typing
from backend.block import Block

class Blockchain:
    def __init__(self, difficulty=2):
        """
        Constructor for the Blockchain class

        :param difficulty: The proof of work complexity 
        """
        super().__init__()

        self.chain = [] # this structure would have to be immutable as we do only want to add to the right of the chain once created. 
        self.create_genesis_block()
        self.difficulty = difficulty
        self.unconfirmed_transactions = [] # data yet to get into the blockchain


    
    def create_genesis_block(self):
        """
        A method to generate the genesis (first) block and append it to the chain.
        The block has index 0, previous_hash as 0, and a valid hash. 
        """
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        A quick pyhonic way to retrieve the most recent block in the chain.
        Note: The chian will always consist of at least one block (i.e., genesis block)
        """
        return self.chain[-1]


    def proof_of_work(self, block) -> str:
        """
        Function that tries different values of a nounce to get a hash that satisfies our difficulty criteria. 


        :param block: [description]
        :type block: [type]
        :return: correct hash
        :rtype: str
        """

        block.nounce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0'* self.difficulty):
            block.nounce += 1
            computed_hash = block.compute_hash()
        
        return computed_hash
    

    def add_block(self, block, proof) -> bool:
        """
        
        A function that adds the block to the chain after verification. 
        Verification includes:
            * Checking if the proof is valid
            * The previous_hash in the block and the hash of the latest block match 

        :param block:  
        :type block: [type]
        :param proof: [description]
        :type proof: [type]
        """

        previous_hash = self.last_block.hash
    
        if previous_hash != block.previous_hash:
            return False
        
        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof 
        self.chain.append(block)
        return True
    
    def is_valid_proof(self, block, block_hash) -> bool:
        """
        Check if block_hash is valid hash of block and satisfies the difficulty criteria. 
        
        :param block: [description]
        :type block: [type]
        :param block_hash: [description]
        :type block_hash: [type]
        :return: [description]
        :rtype: bool
        """

        return (block_hash.startswith('0'*self.difficulty) and block_hash == block.compute_hash())
    
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
    
    def mine(self):
        """
        This method serves as an interface to add the pending transactions
        to the blockchain by adding them to the block and figuring out 
        proof of work. 
        """

        if not self.unconfirmed_transactions:
            return False
        
        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                        transactions=self.unconfirmed_transactions,
                        timestamp=time.time(),
                        previous_hash=last_block.hash)
        
        proof = self.proof_of_work(new_block)

        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index
    
    @classmethod
    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.
        
        :param chain: [description]
        :type chain: [type]
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using 'compute_hash' method
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or previous_hash != block.previous_hash:
                result = False
                break
            
            block.hash, previous_hash = block_hash, block_hash
        
        return result
    
