from setuptools import setup

setup(
    name="agentarchives",
    description="Clients to retrieve, add, and modify records from archival management systems",
    url='https://github.com/artefactual-labs/agentarchives',
    author="Artefactual Systems",
    author_email="info@artefactual.com",
    license="AGPL 3",
    version="0.4.0",
    packages=["agentarchives", "agentarchives.archivesspace", "agentarchives.archivists_toolkit", "agentarchives.atom"],
    install_requires=["requests>=2,<3", "mysqlclient>=1.3,<2"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
