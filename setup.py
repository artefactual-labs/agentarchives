from setuptools import setup

setup(
    name="agentarchives",
    description="Clients to retrieve, add, and modify records from archival management systems",
    author="Misty De Meo",
    author_email="mdemeo@artefactual.com",
    license="AGPL 3",
    version="0.1",
    packages=["agentarchives", "agentarchives.archivesspace", "agentarchives.archivists_toolkit"],
    install_requires=["requests>=2,<3", "MySQL-python>=1.2,<2"],
)
