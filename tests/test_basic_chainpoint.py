import sys
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
        self.assertEqual(self.cp.get_merkle_root(), '7075152d03a5cd92104887b476862778ec0c87be5c2fa1c0a90f87c49fad6eff')

if __name__ == '__main__' and __package__ is None:
    unittest.main()

