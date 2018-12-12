from setuptools import setup,find_packages
setup(
    name="MusicMentions",
    version="0.1",
    packages=find_packages(),
    install_requires=['en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz']
)