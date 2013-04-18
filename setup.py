try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Django Weave API',
    'author': 'Angel Medrano',
    'url': '',
    'download_url': '',
    'author_email': 'amedrano@provplan.org',
    'version': '0.1',
    'install_requires': ["django>=1.3",
                         "ElementTree >= 1.2.7"
                        ],
    'packages': ['weave'],
    'scripts': [],
    'name': 'weave'
}

setup(**config)
