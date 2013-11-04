from distutils.core import setup

setup(
    name='miongo',
    version='0.1.1',
    author='Anton Kasyanov',
    author_email='antony.kasyanov@gmail.com',
    packages=['miongo', 'miongo.tests'],
    url='http://pypi.python.org/pypi/miongo/',
    license='LICENSE.txt',
    description='Yet another MongoDB ORM for Python. Signals included!',
    long_description=open('README.txt').read(),
    install_requires=[
        "pymongo",
    ],
)