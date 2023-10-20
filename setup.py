# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gflow-personal', 'gflow-personal.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.7.1,<4.0.0',
 'mpl-interactions>=0.23.0,<0.24.0',
 'numpy>=1.24.3,<2.0.0',
 'pre-commit>=3.3.2,<4.0.0',
 'pyclipper>=1.3.0.post4,<2.0.0',
 'pytest-xdist>=3.3.1,<4.0.0',
 'pytest>=7.3.1,<8.0.0',
 'scipy>=1.10.1,<2.0.0',
 'shapely>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'gflow-personal',
    'version': '0.1.0',
    'description': '',
    'long_description': '# gflow\n\nFlow field guidance\n\nTo run with gui, run gui/gui_sim.py\nTo run simple example, run examples/simple_sim.py and select desired case within a json case file\n',
    'author': 'adriandelser',
    'author_email': 'adrian.delser@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)