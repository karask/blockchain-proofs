=================
blockchain-proofs
=================
Implementation for generating and validating blockchain proofs/receipts (for proof of existence). Currently it offers support only for Chainpoint v2 (<http://www.chainpoint.org/>) but it can be easily extended.

Note that it also validates that the merkleRoot is properly stored in the blockchain (testnet or mainnet).

In the future the library may incorporate other approaches like OpenTimestamps (<https://github.com/opentimestamps>).

Installation
------------
``$ pip install blockchain-proofs``

Example usage
-------------

``$ python``

>>> from blockchain_proofs import ChainPointV2
>>> leafs = ['a', 'b', 'c']
>>> cp = ChainPointV2()
>>> cp.add_leaf(leafs, True)
>>> cp.make_tree()
>>> cp.get_leaf_count()
3
>>> cp.get_merkle_root()
'7075152d03a5cd92104887b476862778ec0c87be5c2fa1c0a90f87c49fad6eff'
>>> cp.get_receipt(0, "e8b4177a30c8af5dd5f33adbc530e8970b593af1001b322c289e60b4ce395e13")
{'type': 'ChainpointSHA256v2', 'targetHash': 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb', 'anchors': [{'type': 'BTCOpReturn', 'sourceId': 'e8b4177a30c8af5dd5f33adbc530e8970b593af1001b322c289e60b4ce395e13'}], 'proof': [{'right': '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'}, {'right': '2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6'}], '@context': 'https://w3id.org/chainpoint/v2', 'merkleRoot': '7075152d03a5cd92104887b476862778ec0c87be5c2fa1c0a90f87c49fad6eff'}

