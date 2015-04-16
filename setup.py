from setuptools import setup, find_packages
import codecs
from os import path

here = path.abspath(path.dirname(__file__))


def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        return f.read()

setup(
    name='docopt2ragel',
    version='0.1.2',

    description='Convert your docopt usage text into a Ragel FSM',
    long_description=long_description(),

    # The project's main homepage.
    url='https://github.com/willemt/docopt2ragel',
    author='willemt',
    author_email='himself@willemthiart.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='development logging',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['docopt'],
    package_data={},
    data_files=['template.rl'],
    entry_points={
        'console_scripts': [
            'docopt2ragel = docopt2ragel.__main__:main',
        ],
    },
)
