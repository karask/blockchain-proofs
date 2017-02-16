import sys
import json
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from blockchain_proofs.chainpoint import ChainPointV2
import unittest


class BasicBlockChainProofsTest(unittest.TestCase):

    def setUp(self):
        hashes = ['a', 'b', 'c']
        self.cp = ChainPointV2()
        self.cp.add_leaf(hashes, True)
        self.cp.make_tree()

    def test_tree_leaf_count(self):
        self.assertEqual(self.cp.get_leaf_count(), 3)

    def test_tree_root(self):
        self.assertEqual(self.cp.get_merkle_root(),
                         '7075152d03a5cd92104887b476862778ec0c87be5c2fa1c0a90f87c49fad6eff')

    def test_proof_validity(self):
        self.assertTrue(
            self.cp.validate_proof(self.cp.get_proof(1),
                                   self.cp.get_leaf(1),
                                   self.cp.get_merkle_root())
        )

    def test_fetch_hash_from_blockchain(self):
        self.assertEqual('8ba8729bf6577e0540ac8efbf4ffafec3f666721a423ce9f42242669941fa4fd',
                         self.cp.fetch_op_return_file_hash('509f6b149d71661aa803ebf13c7f6f55a4fece961982fca2d72d5a084968b8b1',
                                                           '554e6963444320')
                        )

    def test_receipt(self):
        receipt = '''
{
  "@context": "https://w3id.org/chainpoint/v2",
  "type": "ChainpointSHA256v2", 
  "targetHash": "36e860b0fc71b44e08f6a8b32be7a6b3bbcf20da510fcd9b99acc222e0283468",
  "merkleRoot": "c7b8323a0288d7f37993715c2321d1be622efdad6f3360054d11b50c0d4bcaae",
  "proof": [
    {"left": "c1b381c9a1092d13139034dbbd5751a00f6faf25f47f797efcbdce64434916b3"}
  ],
  "anchors": [
    {
      "type": "BTCOpReturn", 
      "sourceId": "e8b4177a30c8af5dd5f33adbc530e8970b593af1001b322c289e60b4ce395e13"
    }
  ]
}'''
        receipt_json = json.loads(receipt)
        filehash = '36e860b0fc71b44e08f6a8b32be7a6b3bbcf20da510fcd9b99acc222e0283468'
        self.assertTrue(self.cp.validate_receipt(receipt_json, filehash, '554c616e6420', True))

if __name__ == '__main__' and __package__ is None:
    unittest.main()

