import glob
import requests
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
CHAINPOINT_ANCHOR_TYPES = {'btc': 'BTCOpReturn'} #, 'eth': 'ETHData'}

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
        if self.get_tree_ready_state():
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
        else:
            return None


    '''
    Validates a chainpoint receipt. Currently only for BTC anchors
        receipt is the chainpoint_proof metadata from the pdf file.
        certificate_hash is the hash of the certificate after we removed the
            chainpoint_proof metadata
        metadata_prefix is the prefix chosen when issuing in the blockchain
        testnet specifies if testnet or mainnet was used
    '''
    def validate_receipt(self, receipt, certificate_hash, metadata_prefix='', testnet=False):
        # check context and hash type
        if(receipt['@context'].lower() != CHAINPOINT_CONTEXT):
            return False
        if(receipt['type'] not in CHAINPOINT_HASH_TYPES.values()):
            return False
        target_hash = receipt['targetHash']
        merkle_root = receipt['merkleRoot']
        proof = receipt['proof']

        # validate actual hash
        if target_hash.lower() != certificate_hash.lower():
            return False

        # validate merkle proof
        if(not self.validate_proof(proof, target_hash, merkle_root)):
           return False

        # get anchor
        # TODO currently gets only the first valid (BTC) anchor
        anchors = receipt['anchors']
        txid = ''
        for a in anchors:
            if a['type'] in CHAINPOINT_ANCHOR_TYPES.values():
                txid = a['sourceId']
                break

        # validate anchor
        hash_hex = self.fetch_op_return_file_hash(txid, metadata_prefix, testnet)
        if(not merkle_root.lower() == hash_hex.lower()):
            return False

        return True


    def fetch_op_return_file_hash(self, txid, metadata_prefix='', testnet=False):
        if testnet:
            blockr_url = "http://tbtc.blockr.io/api/v1/tx/info/" + txid
        else:
            blockr_url = "http://btc.blockr.io/api/v1/tx/info/" + txid

        response = requests.get(blockr_url).json()
        vouts = response['data']['vouts']
        hash_hex = ""
        for o in vouts:
            script = o['extras']['script']
            if script.startswith('6a'):
                asm = o['extras']['asm']
                if metadata_prefix:
                    split_asm = " " + metadata_prefix
                else:
                    split_asm = " "
                hash_hex = asm.split(split_asm, 1)[1]
                break
        return hash_hex


def main():
    print("Create tree for values 'a', 'b' and 'c' and display some details about the merkle tree")
    hashes = ['a', 'b', 'c']
    cp = ChainPointV2()
    cp.add_leaf(hashes, True)
    cp.make_tree()
    print("leaf_count: ", cp.get_leaf_count())
    print("root: ", cp.get_merkle_root())
    for x in range(0, len(hashes)):
        print("{}: {}".format(x, cp.get_proof(x)))
        print("\n")

if __name__ == "__main__":
    main()
