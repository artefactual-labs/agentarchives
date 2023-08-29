import codecs
from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

with codecs.open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentarchives",
    description="Clients to retrieve, add, and modify records from archival management systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/artefactual-labs/agentarchives",
    author="Artefactual Systems",
    author_email="info@artefactual.com",
    license="AGPL 3",
    version="0.8.0",
    packages=[
        "agentarchives",
        "agentarchives.archivesspace",
        "agentarchives.archivists_toolkit",
        "agentarchives.atom",
    ],
    install_requires=["requests", "mysqlclient"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
