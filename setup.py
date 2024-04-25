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
    name='lyfe_agent',
    version=VERSION,
    description='Lyfe Agent',
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
    package_data={
        # Wheel requires explicit inclusion of non-python files
        'lyfe_agent': ['configs/*',
                       'configs/**/*',
                       'configs/**/**/*',
                       'configs/**/**/**/*',
                       'skills/*',
                       'skills/**/*',
                       'skills/**/**/*',
                       'skills/**/**/**/*',
                       ],
    },
    install_requires=[
        'hydra-core', # Meta AI hydra job/configuration management
        'scikit-learn',
        'pytest-mock',
        'django-environ',
        'langchain', # alternative LLM: LangChain (compatible with GPT and Vicuna)
        # 'google-generativeai', # alternative LLM: Google PaLM
        # 'spacy',
        'python-dotenv', # For loading .env files
        'boto3', # For interaction with AWS
        'numpy',
        'pandas',
        'scipy',
        'tqdm',
        # 'openai==0.28.1', # specifically for openai.embeddings_utils import get_embedding
        # 'openai==1.10.0',
        'langchain-openai',
        # 'sentence_transformers',
        'nltk',
    ],
    python_requires='>=3.7, <4',  # Update this according to your needs
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
