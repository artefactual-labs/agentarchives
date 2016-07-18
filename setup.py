from setuptools import setup

setup(
    name="agentarchives",
    description="Clients to retrieve, add, and modify records from archival management systems",
    author="Artefactual Systems",
    author_email="info@artefactual.com",
    license="AGPL 3",
    version="0.2.1",
    packages=["agentarchives", "agentarchives.archivesspace", "agentarchives.archivists_toolkit", "agentarchives.atom"],
    install_requires=["requests>=2,<3", "mysqlclient>=1.3,<2"],
)
