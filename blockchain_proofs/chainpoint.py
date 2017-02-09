import glob
import hashlib
from merkletools import MerkleTools

CHAINPOINT_CONTEXT = 'https://w3id.org/chainpoint/v2'
CHAINPOINT_HASH_TYPES = {'sha224': 'ChainpointSHA224v2',
                         'sha256': 'ChainpointSHA256v2',
                         'sha384': 'ChainpointSHA384v2',
                         'sha512': 'ChainpointSHA512v2',
                         'sha3_224': 'ChainpointSHA3-224v2',
                         'sha3_256': 'ChainpointSHA3-256v2',
                         'sha3_384': 'ChainpointSHA3-384v2',
                         'sha3_512': 'ChainpointSHA3-512v2' }
CHAINPOINT_ANCHOR_TYPES = {'btc': 'BTCOpReturn', 'eth': 'ETHData'}

'''
Implements chainpoint v2 proof of existence approach
'''
class ChainPointV2(object):
    def __init__(self, hash_type="sha256"):
        self.hash_type = hash_type.lower()
        self.mk = MerkleTools(hash_type)

    '''Wraps merkletools method'''
    def reset_tree(self):
        self.mk.reset_tree()

    '''Wraps merkletools method'''
    def add_leaf(self, values, do_hash=False):
        self.mk.add_leaf(values, do_hash)

    '''Wraps merkletools method'''
    def get_leaf(self, index):
        return self.mk.get_leaf(index)

    '''Wraps merkletools method'''
    def get_leaf_count(self):
        return self.mk.get_leaf_count()

    '''Wraps merkletools method'''
    def get_tree_ready_state(self):
        return self.mk.get_tree_ready_state()

    '''Wraps merkletools method'''
    def make_tree(self):
        self.mk.make_tree()

    '''Wraps merkletools method'''
    def get_merkle_root(self):
        return self.mk.get_merkle_root()

    '''Wraps merkletools method'''
    def get_proof(self, index):
        return self.mk.get_proof(index)

    '''Wraps merkletools method'''
    def validate_proof(self, proof, target_hash, merkle_root):
        return self.mk.validate_proof(proof, target_hash, merkle_root)

    def get_chainpoint_hash_type(self):
        return CHAINPOINT_HASH_TYPES[self.hash_type]

    '''
    Returns the chainpoint v2 blockchain receipt for specific leaf
    Currently only works for BTC anchors
    '''
    def get_receipt(self, index, btc_source_id):
        return {
            "@context": CHAINPOINT_CONTEXT,
            "type": self.get_chainpoint_hash_type(),
            "targetHash": self.get_leaf(index),
            "merkleRoot": self.get_merkle_root(),
            "proof": self.get_proof(index),
            "anchors": [
                {
                    "type": "BTCOpReturn",
                    "sourceId": btc_source_id
                }
            ]
        }


    '''Validates a chainpoint receipt. Currently only for BTC anchors'''
    def validate_receipt(self, receipt):
        # check context and hash type
        if(receipt['@context'] != CHAINPOINT_CONTEXT):
            return False
        if(receipt['type'] not in CHAINPOINT_HASH_TYPES.values()):
            return False
        target_hash = receipt['targetHash']
        merkle_root = receipt['merkleRoot']
        proof = receipt['proof']
        # validate merkle proof
        if(not self.validate_proof(proof, target_hash, merkle_root)):
           return False

        # validate anchor

        return True


def main():
    hashes = ['a', 'b', 'c']
    cp = ChainPointV2()
    cp.add_leaf(hashes, True)
    cp.make_tree()
    print("leaf_count: ", cp.get_leaf_count())
    print("root: ", cp.get_merkle_root())
    for x in range(0, len(hashes)):
        print("{}: {}".format(x, cp.get_proof(x)))
        print("\n")
    for x in range(0, len(hashes)):
            print(cp.validate_proof(cp.get_proof(x), cp.get_leaf(x), cp.get_merkle_root()))
    r = cp.get_receipt(0, 'aaaaaddddaaa4a4a')
    print(r)
    print ( cp.validate_receipt(r) )
    #ADD TESTS TO PROJECT !!!!!!!!!!!!!

if __name__ == "__main__":
    main()
