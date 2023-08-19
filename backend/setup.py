from setuptools import setup, find_packages

with open("version", "r") as fp:
    version = fp.read().strip()

setup(
    name="sorcerer",
    version=version,
    url="https://github.com/mypackage.git",
    author="Author Name",
    author_email="author@gmail.com",
    description="Description of my package",
    packages=find_packages(),
    install_requires=[],
    entrypoints={
        "console_scripts": [
            "sorcerer-client = sorcerer.cli:main",
        ],
    },
)
