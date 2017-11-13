import glob
import requests
import hashlib
import binascii
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
        issuer_identifier is a fixed 8 bytes issuer code that displays on the
            blockchain
        testnet specifies if testnet or mainnet was used
    '''
    def validate_receipt(self, receipt, certificate_hash, issuer_identifier='', testnet=False):
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

        txid = self.get_txid_from_receipt(receipt)

        # validate anchor
        op_return_hex = self.get_op_return_hex_from_blockchain(txid, testnet)

        # ignore issuer_identifier for now (it is string in CRED but used to be
        # hex so we need a smart way to get it) -- TODO: obsolete it !!!
        #issuer_id_hex = self.text_to_hex(issuer_identifier)

        # if op_return starts with CRED it is using the meta-protocol
        if op_return_hex.startswith(self.text_to_hex('CRED')):
            # Structure in bytes/hex: 4 + 2 + 2 + 8 bytes = 8 + 4 + 4 + 16 in string hex

            # TODO in the future could check version_hex and act depending on version
            version_hex = op_return_hex[8:12]
            command_hex = op_return_hex[12:16]
            issuer_hex = op_return_hex[16:32] # could check if it is equal to issuer_id_hex!
            hash_hex = self.hex_to_text(op_return_hex[32:])
            #print(version_hex)
            #print(command_hex)
            #print(issuer_hex)
            #print(hash_hex)
            #print(merkle_root.lower())
        # otherwise op_return should be fixed to 7 bytes or 14 hex chars (old prefix method)
        else:
            ignore_hex_chars = 14
            hash_hex = op_return_hex[ignore_hex_chars:]

        if(not merkle_root.lower() == hash_hex.lower()):
            return False

        return True




    def get_op_return_hex_from_blockchain(self, txid, testnet):
        # uses blockcypher API for now -- TODO: expand to consult multiple services
        if testnet:
            blockcypher_url = "https://api.blockcypher.com/v1/btc/test3/txs/" + txid
        else:
            blockcypher_url = "https://api.blockcypher.com/v1/btc/main/txs/" + txid

        response = requests.get(blockcypher_url).json()
        outputs = response['outputs']
        hash_hex = ""
        for o in outputs:
            script = o['script']
            if script.startswith('6a'):
                # when > 75 op_pushdata1 (4c) is used before length
                if script.startswith('6a4c'):
                    # 2 for 1 byte op_return + 2 for 1 byte op_pushdata1 + 2 for 1 byte data length
                    ignore_hex_chars = 6
                else:
                    # 2 for 1 byte op_return + 2 for 1 byte data length
                    ignore_hex_chars = 4

                hash_hex = script[ignore_hex_chars:]
                break
        return hash_hex


    def get_txid_from_receipt(self, receipt):
        # get anchor
        # TODO currently gets only the first valid (BTC) anchor
        anchors = receipt['anchors']
        txid = ''
        for a in anchors:
            if a['type'] in CHAINPOINT_ANCHOR_TYPES.values():
                txid = a['sourceId']
                break
        return txid

    '''
    Convert ASCII text to hex equivalent
    TODO: Move to another file with utility methods
    '''
    def text_to_hex(self, string):
        bstring = string.encode('utf-8')
        return binascii.hexlify(bstring).decode('utf-8')

    '''
    Convert hex to ASCII text equivalent
    '''
    def hex_to_text(self, hex):
        bstring = binascii.unhexlify(hex)
        return bstring.decode('utf-8')



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
