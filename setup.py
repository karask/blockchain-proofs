from setuptools import setup
from pip.req import parse_requirements
from blockchain_proofs import __version__

install_reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in install_reqs]

setup(name='blockchain-proofs',
      version=__version__,
      description='Create pdf certificate files and issue on the blockchain!',
      author='Konstantinos Karasavvas',
      author_email='kkarasavvas@gmail.com',
      license='MIT',
      packages=['blockchain_proofs'],
      install_requires=requirements,
     )

