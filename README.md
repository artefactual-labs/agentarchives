# agentarchives
Clients to retrieve, add, and modify records from archival management systems

## Installation

`pip install git+https://github.com/artefactual-labs/agentarchives.git`

##Usage
This library can be used to interact with both [Archivists Toolkit](http://archiviststoolkit.org/) as well as [ArchivesSpace](http://archivesspace.org/)

### ArchivesSpace
First, you need to import the module in your Python script:

`from agentarchives import archivesspace`

Then, initiate a new client, passing in the URL, user name, password, port and repository for your AS instance:

`client = archivesspace.ArchivesSpaceClient('http://localhost', 'admin', 'admin', 8089, 2)`

Using your client, call one of the included functions (documented in `client.py`). For example, the following:

    $ resource = client.get_record('/repositories/2/resources/1’)
    $ print resource

will return:

      {
       'lock_version':0,
       'system_mtime':   '2015-11-17T00:23:19   Z',
       'extents':[
          {
             'lock_version':0,
             'system_mtime':'2015-11-17T00:23:19Z',
             'jsonmodel_type':'extent',
             'user_mtime':'2015-11-17T00:23:19Z',
             'number':'1',
             'last_modified_by':'admin',
             'portion':'whole',
             'create_time':'2015-11-17T00:23:19Z',
             'created_by':'admin',
             'extent_type':'cassettes'
          }
       ],
       'jsonmodel_type':'resource',
       'instances':[

       ],
       'create_time':'2015-11-17T00:23:19Z',
       'publish':False,
       'title':'blah',
       'related_accessions':[

       ],
       'created_by':'admin',
       'subjects':[

       ],
       'deaccessions':[

       ],
       'external_documents':[

       ],
       'linked_agents':[

       ],
       'repository':{
          'ref':'/repositories/2'
       },
       'user_mtime':   '2015-11-17T00:23:19   Z',
       'rights_statements':[

       ],
       'revision_statements':[

       ],
       'linked_events':[

       ],
       'external_ids':[

       ],
       'suppressed':False,
       'restrictions':False,
       'dates':[
          {
             'lock_version':0,
             'system_mtime':'2015-11-17T00:23:19Z',
             'jsonmodel_type':'date',
             'date_type':'bulk',
             'user_mtime':'2015-11-17T00:23:19Z',
             'last_modified_by':'admin',
             'label':'creation',
             'create_time':'2015-11-17T00:23:19Z',
             'created_by':'admin',
             'expression':'maybe 1999'
          }
       ],
       'classifications':[

       ],
       'language':'aar',
       'level':'collection',
       'notes':[

       ],
       'tree':{
          'ref':'/repositories/2/resources/1/tree'
       },
       'uri':'/repositories/2/resources/1',
       'last_modified_by':'admin',
       'id_0':'blah’
    }
