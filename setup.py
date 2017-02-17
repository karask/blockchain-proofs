import os
from setuptools import setup
from pip.req import parse_requirements
from blockchain_proofs import __version__

install_reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in install_reqs]

with open('README.rst') as readme:
    long_description = readme.read()

setup(name='blockchain-proofs',
      version=__version__,
      description='Implements chainpoint v2 proof of existence approach',
      long_description=long_description,
      author='Konstantinos Karasavvas',
      author_email='kkarasavvas@gmail.com',
      license='MIT',
      packages=['blockchain_proofs'],
      keywords='blockchain proof receipt chainpoint validation',
      install_requires=requirements,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3'
      ]
     )

