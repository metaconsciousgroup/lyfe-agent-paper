import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

# Replace this with your package's version and expected tag
VERSION = '0.1.0'
EXPECTED_TAG = 'v' + VERSION  # Assuming tags are like v0.01, v0.02, etc.

here = os.path.abspath(os.path.dirname(__file__))

class VerifyVersionCommand(install):
    """
    Custom command to verify that the git tag is the expected one for the release.
    """

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("GITHUB_REF", "NO GITHUB TAG!").replace("refs/tags/", "")

        if tag != EXPECTED_TAG:
            info = "Git tag: {} does not match the expected tag of this app: {}".format(
                tag, EXPECTED_TAG
            )
            sys.exit(info)


setup(
    name='lyfe_bench',
    version=VERSION,
    description='Benchmarks for Lyfe Agents',
    author='MetaConscious Group',
    author_email='yanggr@mit.edu',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Your License Here',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),  # Exclude tests
    install_requires=[
        'networkx',
        'numpy',
    ],
    python_requires='>=3.7, <4',  # Update this according to your needs
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)