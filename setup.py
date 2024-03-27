# -*- coding: utf-8 -*-
import os
print("Current Directory:", os.getcwd())

from setuptools import setup

packages = \
['PGFlow', 'PGFlow.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.7.1,<4.0.0',
 'mpl-interactions>=0.23.0,<0.24.0',
 'numpy>=1.24.3,<2.0.0',
 'pyclipper>=1.3.0.post4,<2.0.0',
 'scipy>=1.10.1,<2.0.0',
 'shapely>=2.0.1,<3.0.0']

extra_requires = \
['pre-commit>=3.3.2,<4.0.0',
 'pytest-xdist>=3.3.1,<4.0.0',
 'pytest>=7.3.1,<8.0.0']

setup_kwargs = {
    'name': 'PGFlow',
    'version': '0.1.0',
    'description': '',
    'long_description': '# PGFlow\n\nFlow field guidance\n\nTo run simple example, run examples/simple_sim.py and select desired case within a json case file\n',
    'author': 'Zeynep Bilgin, Adrian Del-Ser, Ilkay Yavrucuk, Murat Bronz',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extra_requires' : extra_requires,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
