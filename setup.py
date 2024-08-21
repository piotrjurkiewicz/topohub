from setuptools import setup
import topohub

URL = 'https://github.com/piotrjurkiewicz/topohub'

with open('README.md') as f:
    README = f.read()

setup(
    name='topohub',
    version=topohub.__version__,
    packages=['topohub'],
    package_dir={'topohub': 'topohub'},
    package_data={'topohub': ['data/gabriel/*/*.json', 'data/sndlib/*.json', 'data/topozoo/*.json', 'data/backbone/*.json']},
    url=URL,
    license='MIT',
    author='Piotr Jurkiewicz',
    author_email='piotr.jerzy.jurkiewicz@gmail.com',
    description='A repository of reference Gabriel graph and real-world topologies for networking research',
    long_description=README,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: System :: Networking",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry"
    ]
)
