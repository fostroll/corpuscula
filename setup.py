from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="corpuscula",
    version="1.0.0",
    description="A toolkit that simplifies corpus processing",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sergei Ternovykh",
    author_email="fostroll@gmail.com",
    url="https://github.com/fostroll/corpuscula",
    packages=find_packages(exclude=["data", "scripts", "tests"]),
    license="BSD",
    install_requires=required,
    include_package_data=True,
    python_requires=">=3.6",
)
