from setuptools import setup, find_packages

setup(
    name="newsletter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4"],
)
