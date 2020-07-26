import json 

from typing import Dict, List, Any
from hashlib import sha256
class Block:
    def __init__(self, index: int, transaction: List, timestamp: float, previous_hash: str):
        """
        Constructor for the Block class

        :param index: Unique ID of the block
        :type index: [type]
        :param transaction: List of transactions
        :type transaction: [type]
        :param timestamp: Time of generation of the block
        :type timestamp: [type]
        :param previous_hash: The hash of the previous block in the chain
        :type previous_hash: [type]
        """

        self.index = index
        self.transaction = transaction
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self) -> str:
        """
        Returns the hash of the block instance by first converting it into a JSON string

        """

        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

