# agentarchives

Clients to retrieve, add, and modify records from archival management systems.

## Installation

Agentarchives is on [PyPI](https://pypi.python.org/pypi/agentarchives)!

`pip install agentarchives`

Or you can install it directly from git

`pip install git+https://github.com/artefactual-labs/agentarchives.git`

## Usage

This library can be used to interact with [Archivists Toolkit](http://archiviststoolkit.org/),
[ArchivesSpace](http://archivesspace.org/), and [Access To Memory (AtoM)](https://www.accesstomemory.org).

### ArchivesSpace

First, you need to import the module in your Python script:

```python
from agentarchives import archivesspace
```

Then, initiate a new client, passing in the URL, user name, password, port and repository for your AS instance:

```python
client = archivesspace.ArchivesSpaceClient('http://localhost', 'admin', 'admin', 8089, 2)
```

Using your client, call one of the included functions (documented in `client.py`). For example, the following:

    $ resource = client.get_record('/repositories/2/resources/1')
    $ print resource

will return:

```json
{
    "classifications": [],
    "create_time": "2015-11-17T00:23:19Z",
    "created_by": "admin",
    "dates": [
        {
            "create_time": "2015-11-17T00:23:19Z",
            "created_by": "admin",
            "date_type": "bulk",
            "expression": "maybe 1999",
            "jsonmodel_type": "date",
            "label": "creation",
            "last_modified_by": "admin",
            "lock_version": 0,
            "system_mtime": "2015-11-17T00:23:19Z",
            "user_mtime": "2015-11-17T00:23:19Z"
        }
    ],
    "deaccessions": [],
    "extents": [
        {
            "create_time": "2015-11-17T00:23:19Z",
            "created_by": "admin",
            "extent_type": "cassettes",
            "jsonmodel_type": "extent",
            "last_modified_by": "admin",
            "lock_version": 0,
            "number": "1",
            "portion": "whole",
            "system_mtime": "2015-11-17T00:23:19Z",
            "user_mtime": "2015-11-17T00:23:19Z"
        }
    ],
    "external_documents": [],
    "external_ids": [],
    "id_0": "blah",
    "instances": [],
    "jsonmodel_type": "resource",
    "language": "aar",
    "last_modified_by": "admin",
    "level": "collection",
    "linked_agents": [],
    "linked_events": [],
    "lock_version": 0,
    "notes": [],
    "publish": false,
    "related_accessions": [],
    "repository": {
        "ref": "/repositories/2"
    },
    "restrictions": false,
    "revision_statements": [],
    "rights_statements": [],
    "subjects": [],
    "suppressed": false,
    "system_mtime": "2015-11-17T00:23:19   Z",
    "title": "blah",
    "tree": {
        "ref": "/repositories/2/resources/1/tree"
    },
    "uri": "/repositories/2/resources/1",
    "user_mtime": "2015-11-17T00:23:19   Z"
}
```

### Access To Memory (AtoM)

First, you need to import the module in your Python script:

```python
from agentarchives import atom
```

Then, initiate a new client, passing in the URL, REST API access token, password, and port for your AtoM instance:

```python
client = atom.AtomClient('http://localhost', '68405800c6612599', 80)
```

Using your client, call one of the included functions (documented in `client.py`). For example, the following:

    $ resource = client.get_record('test-fonds')
    $ print resource

Will return:

```json
{
    "dates": [
        {
            "begin": "2014-01-01",
            "end": "2015-01-01",
            "type": "Creation"
        }
    ],
    "level_of_description": "Fonds",
    "notes": [
        {
            "content": "Note content",
            "type": "general"
        }
    ],
    "publication_status": "Draft",
    "reference_code": "F2",
    "title": "Test fonds"
}
```

Current AtoM client limitations (versus the ArchivesSpace client):
* Identifier wildcard search not supported
* Creation of multiple notes not supported
* Nested digital objects not supported
* The ability to add/list notes with no content isn't supported
