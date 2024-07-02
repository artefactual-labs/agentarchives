import collections
import os
from unittest import mock

import pytest
import requests

from agentarchives.archivesspace.client import ArchivesSpaceClient
from agentarchives.archivesspace.client import ArchivesSpaceError
from agentarchives.archivesspace.client import CommunicationError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH = {"host": "http://localhost:8089", "user": "admin", "passwd": "admin"}


@pytest.mark.parametrize(
    "params,raises,base_url",
    [
        # These are pairs that we don't like and we raise.
        ({"host": "", "port": ""}, True, None),
        ({"host": None, "port": None}, True, None),
        ({"host": "", "port": "string"}, True, None),
        ({"host": "string", "port": "string"}, True, None),
        # When `host` is not a URL.
        ({"host": "localhost"}, False, "http://localhost:8089"),
        ({"host": "localhost:8000"}, False, "http://localhost:8000"),
        ({"host": "localhost", "port": 12345}, False, "http://localhost:12345"),
        ({"host": "localhost", "port": "12345"}, False, "http://localhost:12345"),
        ({"host": "localhost", "port": None}, False, "http://localhost"),
        ({"host": "localhost", "port": ""}, False, "http://localhost"),
        ({"host": "foobar.tld", "port": ""}, False, "http://foobar.tld"),
        ({"host": "foobar.tld", "port": None}, False, "http://foobar.tld"),
        ({"host": "foobar.tld", "port": "12345"}, False, "http://foobar.tld:12345"),
        # When `host` is a URL!
        ({"host": "http://apiserver"}, False, "http://apiserver"),
        (
            {"host": "http://apiserver:12345/path/"},
            False,
            "http://apiserver:12345/path",
        ),
        ({"host": "https://apiserver:12345"}, False, "https://apiserver:12345"),
        (
            {"host": "https://apiserver:12345", "port": 999},
            False,
            "https://apiserver:12345",
        ),
    ],
)
def test_base_url_config(mocker, params, raises, base_url):
    kwargs = {"user": "foo", "passwd": "bar"}
    kwargs.update(params)
    if raises:
        with pytest.raises((AttributeError, requests.exceptions.InvalidURL)):
            ArchivesSpaceClient(**kwargs)
        return
    mocker.patch("agentarchives.archivesspace.ArchivesSpaceClient._login")
    client = ArchivesSpaceClient(**kwargs)
    assert client.base_url == base_url, f"Failed with params: {params}"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "beb7f2a62252458338b751e91b1a7b2ba663b87029b499fe53f035f3764bb0d0",
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200, **{"json.return_value": {"status": "session_logged_out"}}
        ),
    ],
)
def test_logout(session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    client.logout()
    assert client.session is None


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "beb7f2a62252458338b751e91b1a7b2ba663b87029b499fe53f035f3764bb0d0"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_listing_collections(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["title"] == "Test fonds"
    assert collections[0]["type"] == "resource"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "958640d703ed8dd063b518f825cc4f4206ec86f049837099257471065e936f02"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":4,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/3","_resolved":{"lock_version":4,"digital_object_id":"f808032e-c6ec-4242-b7aa-5395988b9f7e","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:38Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:38Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"4e5eec95fcb62440f20a4f5b89c6d16b","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/3","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/3/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/4","_resolved":{"lock_version":3,"digital_object_id":"5517ddb1-36dd-4a02-a363-f1571982670f","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:53Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:53Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"bdfe911944a3d26a9fd43455aa968c52","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/4","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/4/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/5","_resolved":{"lock_version":2,"digital_object_id":"8ea81c4d-6df3-4775-a314-4bef4f44dd3c","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:04:57Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:04:57Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"68242ba5c0cbff4b674c6a2fa2335ad0","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/5","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/5/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/6","_resolved":{"lock_version":1,"digital_object_id":"a1672927-9a56-41c4-b423-5d76e4a1c660","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"3453d8096aabc607723b4359ab8fdd3c","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/6","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/6/tree"}}}}],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":11,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-12-03T00:03:41Z","user_mtime":"2015-12-03T00:03:41Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[{"content":["Singlepart note"],"type":"physdesc","jsonmodel_type":"note_singlepart","persistent_id":"cdc013c483de98b8a1762302faf8fd32","publish":true}],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-03T00:03:41Z",
                            "system_mtime": "2015-12-03T00:03:41Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test edited subseries, November, 2014 to November, 2015",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child",
                            "id": 13,
                            "record_uri": "/repositories/2/archival_objects/13",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 2",
                            "id": 14,
                            "record_uri": "/repositories/2/archival_objects/14",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "item",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 3",
                            "id": 16,
                            "record_uri": "/repositories/2/archival_objects/16",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child with note",
                            "id": 17,
                            "record_uri": "/repositories/2/archival_objects/17",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child final",
                            "id": 18,
                            "record_uri": "/repositories/2/archival_objects/18",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_rendering_record_containing_a_singlepart_note(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[1]["notes"][0]["content"] == "Singlepart note"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "34a45d1d93fd8d14fe0b93b5e49011612e6b19a395afd03a3f6d311073f18606"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":11,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-12-03T00:03:41Z","user_mtime":"2015-12-03T00:03:41Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[{"content":["Singlepart note"],"type":"physdesc","jsonmodel_type":"note_singlepart","persistent_id":"cdc013c483de98b8a1762302faf8fd32","publish":true}],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-03T00:03:41Z",
                            "system_mtime": "2015-12-03T00:03:41Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series, 1950 - 1972",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test edited subseries w/ empty note, November, 2014 to November, 2015",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new edited child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child",
                            "id": 13,
                            "record_uri": "/repositories/2/archival_objects/13",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 2",
                            "id": 14,
                            "record_uri": "/repositories/2/archival_objects/14",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "item",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 3",
                            "id": 16,
                            "record_uri": "/repositories/2/archival_objects/16",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child with note",
                            "id": 17,
                            "record_uri": "/repositories/2/archival_objects/17",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child final",
                            "id": 18,
                            "record_uri": "/repositories/2/archival_objects/18",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 19,
                            "record_uri": "/repositories/2/archival_objects/19",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 20,
                            "record_uri": "/repositories/2/archival_objects/20",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test child",
                            "id": 26,
                            "record_uri": "/repositories/2/archival_objects/26",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test child",
                            "id": 27,
                            "record_uri": "/repositories/2/archival_objects/27",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test child",
                            "id": 28,
                            "record_uri": "/repositories/2/archival_objects/28",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test child",
                            "id": 29,
                            "record_uri": "/repositories/2/archival_objects/29",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Record with two notes",
                            "id": 32,
                            "record_uri": "/repositories/2/archival_objects/32",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Second child with two notes",
                            "id": 33,
                            "record_uri": "/repositories/2/archival_objects/33",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Third record with two notes",
                            "id": 34,
                            "record_uri": "/repositories/2/archival_objects/34",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test child",
                            "id": 35,
                            "record_uri": "/repositories/2/archival_objects/35",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "recordgrp",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 0,
                    "total_hits": 0,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
    ],
)
def test_listing_collections_search(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections(search_pattern="Test fonds")
    assert len(collections) == 1
    assert collections[0]["title"] == "Test fonds"
    assert collections[0]["type"] == "resource"

    no_results = client.find_collections(search_pattern="No such fonds")
    assert len(no_results) == 0


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "7dca265a6dc0619007212824e18b22141ff9eb9e7533bf5d6b0501bc4256d0df",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/6",
                            "title": "Resource with spaces in the identifier",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Resource with spaces in the identifier","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2016-02-13T00:41:44Z","system_mtime":"2016-02-13T00:42:41Z","user_mtime":"2016-02-13T00:42:41Z","suppressed":false,"id_0":"2015044 Aa Ac","level":"collection","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"50","created_by":"admin","last_modified_by":"admin","create_time":"2016-02-13T00:42:41Z","system_mtime":"2016-02-13T00:42:41Z","user_mtime":"2016-02-13T00:42:41Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"expression":"sdfsdf","created_by":"admin","last_modified_by":"admin","create_time":"2016-02-13T00:42:41Z","system_mtime":"2016-02-13T00:42:41Z","user_mtime":"2016-02-13T00:42:41Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/6","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/6/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2016-02-13T00:42:41Z",
                            "system_mtime": "2016-02-13T00:42:41Z",
                            "create_time": "2016-02-13T00:41:44Z",
                            "level": "collection",
                            "identifier": "2015044 Aa Ac",
                            "restrictions": "false",
                            "four_part_id": "2015044 Aa Ac",
                            "uri": "/repositories/2/resources/6",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Resource with spaces in the identifier",
                    "id": 6,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [],
                    "record_uri": "/repositories/2/resources/6",
                    "level": "collection",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_listing_collections_search_spaces(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections(identifier="2015044 Aa Ac")
    assert len(collections) == 1
    assert collections[0]["title"] == "Resource with spaces in the identifier"
    assert collections[0]["levelOfDescription"] == "collection"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "b2e5017a17414086304abced192a02b53c9d98df2b8ae9f415a32f97bda8e31b",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_listing_collections_sort(get, post):
    client = ArchivesSpaceClient(**AUTH)
    asc = client.find_collections(sort_by="asc")
    assert len(asc) == 2
    assert asc[0]["title"] == "Some other fonds"
    assert asc[0]["type"] == "resource"

    desc = client.find_collections(sort_by="desc")
    assert len(desc) == 2
    assert desc[0]["title"] == "Test fonds"
    assert desc[0]["type"] == "resource"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "1a00ae68128363e119356d43832dc6918f681c2a8fd910cf110302af22831160",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test subseries",
                    "display_string": "Test subseries",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-06-11T17:45:27Z",
                    "user_mtime": "2015-06-11T17:45:27Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        )
    ],
)
def test_find_resource_id(get, post):
    client = ArchivesSpaceClient(**AUTH)
    assert (
        client.find_resource_id_for_component("/repositories/2/archival_objects/3")
        == "/repositories/2/resources/1"
    )


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "c3c62cbd26ffe5bd1fa3457fac5f22cf1edfe7028f08aba9dec53d3ba277b14f",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test subseries",
                    "display_string": "Test subseries",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-06-11T17:45:27Z",
                    "user_mtime": "2015-06-11T17:45:27Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "72aa597a3d4078c3f61f6000ac068f38",
                    "component_id": "F1-1",
                    "title": "Test series",
                    "display_string": "Test series",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:14:48Z",
                    "system_mtime": "2015-06-11T17:45:18Z",
                    "user_mtime": "2015-06-11T17:45:18Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_find_component_parent(get, post):
    client = ArchivesSpaceClient(**AUTH)
    type, id = client.find_parent_id_for_component("/repositories/2/archival_objects/3")

    assert type == ArchivesSpaceClient.RESOURCE_COMPONENT
    assert id == "/repositories/2/archival_objects/1"

    type, id = client.find_parent_id_for_component("/repositories/2/archival_objects/1")
    assert type == ArchivesSpaceClient.RESOURCE
    assert id == "/repositories/2/resources/1"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "d48859aa93b3c881d4d688d6feb0841f852831e7140079fb55bf6726718cfa57",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                }
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-06-11T17:08:42Z",
                    "user_mtime": "2015-06-11T17:08:42Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "72aa597a3d4078c3f61f6000ac068f38",
                    "component_id": "F1-1",
                    "title": "Test series",
                    "display_string": "Test series",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:14:48Z",
                    "system_mtime": "2015-06-11T17:45:18Z",
                    "user_mtime": "2015-06-11T17:45:18Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test subseries",
                    "display_string": "Test subseries",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-06-11T17:45:27Z",
                    "user_mtime": "2015-06-11T17:45:27Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "8429037b0f599a1efcca06b9b813700a",
                    "component_id": "F1-1-1-1",
                    "title": "Test file",
                    "display_string": "Test file",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:30Z",
                    "system_mtime": "2015-06-11T17:45:40Z",
                    "user_mtime": "2015-06-11T17:45:40Z",
                    "suppressed": False,
                    "level": "file",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/4",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/3"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 1,
                    "publish": False,
                    "ref_id": "2d6194e7945563b58be69b5a70887239",
                    "component_id": "F1-2",
                    "title": "Test series 2",
                    "display_string": "Test series 2",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:15:03Z",
                    "system_mtime": "2015-06-11T17:46:12Z",
                    "user_mtime": "2015-06-11T17:46:12Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/2",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_find_resource_children(get, post):
    client = ArchivesSpaceClient(**AUTH)
    data = client.get_resource_component_and_children("/repositories/2/resources/1")

    assert isinstance(data, dict)
    assert len(data["children"]) == 2
    assert data["has_children"] is True
    assert data["title"] == "Test fonds"
    assert data["type"] == "resource"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "2f380c9b7b2d173d8409063c2ccd16f75990706a4844345fddbc7b9aa6de83f0",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                }
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-06-11T17:08:42Z",
                    "user_mtime": "2015-06-11T17:08:42Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                }
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-06-11T17:08:42Z",
                    "user_mtime": "2015-06-11T17:08:42Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "72aa597a3d4078c3f61f6000ac068f38",
                    "component_id": "F1-1",
                    "title": "Test series",
                    "display_string": "Test series",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:14:48Z",
                    "system_mtime": "2015-06-11T17:45:18Z",
                    "user_mtime": "2015-06-11T17:45:18Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 1,
                    "publish": False,
                    "ref_id": "2d6194e7945563b58be69b5a70887239",
                    "component_id": "F1-2",
                    "title": "Test series 2",
                    "display_string": "Test series 2",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:15:03Z",
                    "system_mtime": "2015-06-11T17:46:12Z",
                    "user_mtime": "2015-06-11T17:46:12Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/2",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_find_resource_children_recursion_level(get, post):
    client = ArchivesSpaceClient(**AUTH)
    data = client.get_resource_component_and_children(
        "/repositories/2/resources/1", recurse_max_level=1
    )
    assert data["children"] == []
    assert data["has_children"] is True

    data = client.get_resource_component_and_children(
        "/repositories/2/resources/1", recurse_max_level=2
    )
    assert len(data["children"]) == 2
    assert data["has_children"] is True


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "bf92956d5135eca4ad3d6b6418d96146a1182054c466bf81eeca0a8daef37931",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series, 1950 - 1972",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test edited subseries, November, 2014 to November, 2015",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child",
                            "id": 13,
                            "record_uri": "/repositories/2/archival_objects/13",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 2",
                            "id": 14,
                            "record_uri": "/repositories/2/archival_objects/14",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "item",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 3",
                            "id": 16,
                            "record_uri": "/repositories/2/archival_objects/16",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child with note",
                            "id": 17,
                            "record_uri": "/repositories/2/archival_objects/17",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child final",
                            "id": 18,
                            "record_uri": "/repositories/2/archival_objects/18",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 19,
                            "record_uri": "/repositories/2/archival_objects/19",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 20,
                            "record_uri": "/repositories/2/archival_objects/20",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 11,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-12-03T00:03:41Z",
                    "user_mtime": "2015-12-03T00:03:41Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [{"ref": "/repositories/2/accessions/1"}],
                    "notes": [
                        {
                            "content": ["Singlepart note"],
                            "type": "physdesc",
                            "jsonmodel_type": "note_singlepart",
                            "persistent_id": "cdc013c483de98b8a1762302faf8fd32",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
    ],
)
def test_find_resource_children_at_max_recursion_level(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children(
        "/repositories/2/resources/1", recurse_max_level=1
    )
    assert record["children"] == []
    assert record["has_children"] is True


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "7ed82cd6151564b78f0e2a9474c513d5a5deb813ea938e7487048cd5cb0756f6",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 3,
                    "position": 0,
                    "publish": False,
                    "ref_id": "72aa597a3d4078c3f61f6000ac068f38",
                    "component_id": "F1-1",
                    "title": "Test series",
                    "display_string": "Test series, 1950 - 1972",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:14:48Z",
                    "system_mtime": "2015-12-04T00:59:35Z",
                    "user_mtime": "2015-12-04T00:59:35Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "1950 - 1972",
                            "begin": "1950-12-03",
                            "end": "1972-12-03",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-04T00:59:35Z",
                            "system_mtime": "2015-12-04T00:59:35Z",
                            "user_mtime": "2015-12-04T00:59:35Z",
                            "date_type": "range",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-04T00:59:35Z",
                            "system_mtime": "2015-12-04T00:59:35Z",
                            "user_mtime": "2015-12-04T00:59:35Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/2"
                            },
                        }
                    ],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {
                        "lock_version": 10,
                        "position": 0,
                        "publish": False,
                        "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                        "component_id": "F1-1-1",
                        "title": "Test edited subseries",
                        "display_string": "Test edited subseries, November, 2014 to November, 2015",
                        "restrictions_apply": False,
                        "created_by": "admin",
                        "last_modified_by": "admin",
                        "create_time": "2015-06-11T17:20:19Z",
                        "system_mtime": "2015-12-04T00:59:36Z",
                        "user_mtime": "2015-12-03T01:24:00Z",
                        "suppressed": False,
                        "level": "subseries",
                        "jsonmodel_type": "archival_object",
                        "external_ids": [],
                        "subjects": [],
                        "linked_events": [],
                        "extents": [],
                        "dates": [
                            {
                                "lock_version": 0,
                                "expression": "November, 2014 to November, 2015",
                                "begin": "2014-11-01",
                                "end": "2015-11-01",
                                "created_by": "admin",
                                "last_modified_by": "admin",
                                "create_time": "2015-12-03T01:24:00Z",
                                "system_mtime": "2015-12-03T01:24:00Z",
                                "user_mtime": "2015-12-03T01:24:00Z",
                                "date_type": "inclusive",
                                "label": "creation",
                                "jsonmodel_type": "date",
                            }
                        ],
                        "external_documents": [],
                        "rights_statements": [],
                        "linked_agents": [],
                        "instances": [
                            {
                                "lock_version": 0,
                                "created_by": "admin",
                                "last_modified_by": "admin",
                                "create_time": "2015-12-03T01:24:00Z",
                                "system_mtime": "2015-12-03T01:24:00Z",
                                "user_mtime": "2015-12-03T01:24:00Z",
                                "instance_type": "digital_object",
                                "jsonmodel_type": "instance",
                                "digital_object": {
                                    "ref": "/repositories/2/digital_objects/7"
                                },
                            },
                            {
                                "lock_version": 0,
                                "created_by": "admin",
                                "last_modified_by": "admin",
                                "create_time": "2015-12-03T01:24:00Z",
                                "system_mtime": "2015-12-03T01:24:00Z",
                                "user_mtime": "2015-12-03T01:24:00Z",
                                "instance_type": "digital_object",
                                "jsonmodel_type": "instance",
                                "digital_object": {
                                    "ref": "/repositories/2/digital_objects/8"
                                },
                            },
                        ],
                        "notes": [
                            {
                                "jsonmodel_type": "note_multipart",
                                "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                                "subnotes": [
                                    {
                                        "content": "This is a test note",
                                        "publish": True,
                                        "jsonmodel_type": "note_text",
                                    }
                                ],
                                "type": "odd",
                                "publish": True,
                            }
                        ],
                        "uri": "/repositories/2/archival_objects/3",
                        "repository": {"ref": "/repositories/2"},
                        "resource": {"ref": "/repositories/2/resources/1"},
                        "parent": {"ref": "/repositories/2/archival_objects/1"},
                        "has_unpublished_ancestor": True,
                    },
                    {
                        "lock_version": 0,
                        "position": 1,
                        "ref_id": "7a273392ede0464c8509f70f053d94bf",
                        "title": "New new new child",
                        "display_string": "New new new child",
                        "restrictions_apply": False,
                        "created_by": "admin",
                        "last_modified_by": "admin",
                        "create_time": "2015-09-10T21:00:56Z",
                        "system_mtime": "2015-12-04T00:59:36Z",
                        "user_mtime": "2015-09-10T21:00:56Z",
                        "suppressed": False,
                        "level": "series",
                        "jsonmodel_type": "archival_object",
                        "external_ids": [],
                        "subjects": [],
                        "linked_events": [],
                        "extents": [],
                        "dates": [],
                        "external_documents": [],
                        "rights_statements": [],
                        "linked_agents": [],
                        "instances": [],
                        "notes": [],
                        "uri": "/repositories/2/archival_objects/10",
                        "repository": {"ref": "/repositories/2"},
                        "resource": {"ref": "/repositories/2/resources/1"},
                        "parent": {"ref": "/repositories/2/archival_objects/1"},
                        "has_unpublished_ancestor": True,
                    },
                ]
            },
        ),
    ],
)
def test_find_resource_component_children_at_max_recursion_level(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children(
        "/repositories/2/archival_objects/1", recurse_max_level=1
    )
    assert record["children"] == []
    assert record["has_children"] is True


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "5934dcb043611dda104542b5c8194a3d4ca35cf86d0c288d5cd1acf301633c14",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 2,
                    "offset_first": 11,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
    ],
)
def test_find_collection_ids(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids()
    assert ids == ["/repositories/2/resources/1", "/repositories/2/resources/2"]


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "7c5cd6a2c5b79c789f5125e09e58c287fddb81106f3bfbb5e33cda8b92d2d86e",
                    "user": {
                        "lock_version": 21,
                        "username": "admin",
                        "name": "Administrator",
                        "is_system_user": True,
                        "create_time": "2015-06-11T17:04:21Z",
                        "system_mtime": "2015-06-30T23:37:21Z",
                        "user_mtime": "2015-06-30T23:37:21Z",
                        "jsonmodel_type": "user",
                        "groups": [],
                        "is_admin": True,
                        "uri": "/users/1",
                        "agent_record": {"ref": "/agents/people/1"},
                        "permissions": {
                            "/repositories/1": [
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                            ],
                            "_archivesspace": [
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                            ],
                        },
                    },
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        )
    ],
)
def test_find_collection_ids_search(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids(search_pattern="Some")
    assert ids == ["/repositories/2/resources/2"]


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "28e0056b648ecddd66b7635758b6229fe2ccdf5143aaf56dacc621b0fd69fc56",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-06-11T17:08:42Z","user_mtime":"2015-06-11T17:08:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        )
    ],
)
def test_count_collection_ids(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections()
    assert ids == 2


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "4873d40652ca79f0ead3f7c35a4441825b585a870850bdb50d55c17557076680",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        )
    ],
)
def test_count_collection_ids_search(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections(search_pattern="Some")
    assert ids == 1


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "a7044300d27191551e5940423d1c0e9fb7a49354cab8d986eddcb1e940b9e6b4",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "archival_objects": [
                        {
                            "ref": "/repositories/2/archival_objects/752250",
                            "_resolved": {
                                "lock_version": 0,
                                "position": 0,
                                "publish": True,
                                "ref_id": "a118514fab1b2ee6a7e9ad259e1de355",
                                "component_id": "test111",
                                "title": "Test AO",
                                "display_string": "Test AO",
                                "restrictions_apply": False,
                                "created_by": "admin",
                                "last_modified_by": "admin",
                                "create_time": "2015-09-22T18:35:41Z",
                                "system_mtime": "2015-09-22T18:35:41Z",
                                "user_mtime": "2015-09-22T18:35:41Z",
                                "suppressed": False,
                                "level": "file",
                                "jsonmodel_type": "archival_object",
                                "external_ids": [],
                                "subjects": [],
                                "linked_events": [],
                                "extents": [],
                                "dates": [],
                                "external_documents": [],
                                "rights_statements": [],
                                "linked_agents": [],
                                "instances": [],
                                "notes": [],
                                "uri": "/repositories/2/archival_objects/752250",
                                "repository": {"ref": "/repositories/2"},
                                "resource": {"ref": "/repositories/2/resources/11319"},
                                "has_unpublished_ancestor": False,
                            },
                        }
                    ]
                }
            },
        )
    ],
)
def test_find_by_id_refid(get, post):
    client = ArchivesSpaceClient(**AUTH)
    data = client.find_by_id(
        "archival_objects", "ref_id", "a118514fab1b2ee6a7e9ad259e1de355"
    )
    assert len(data) == 1
    item = data[0]
    assert item["identifier"] == "a118514fab1b2ee6a7e9ad259e1de355"
    assert item["id"] == "/repositories/2/archival_objects/752250"
    assert item["type"] == "resource_component"
    assert item["title"] == "Test AO"
    assert item["levelOfDescription"] == "file"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "3cc051a4be61263e9e409b232be66f3af240e3940f1a53c0e83f25a0349f7c5c",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                }
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-06-11T17:08:42Z",
                    "user_mtime": "2015-06-11T17:08:42Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-11T17:08:42Z",
                            "system_mtime": "2015-06-11T17:08:42Z",
                            "user_mtime": "2015-06-11T17:08:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "72aa597a3d4078c3f61f6000ac068f38",
                    "component_id": "F1-1",
                    "title": "Test series",
                    "display_string": "Test series",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:14:48Z",
                    "system_mtime": "2015-06-11T17:45:18Z",
                    "user_mtime": "2015-06-11T17:45:18Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 1,
                    "publish": False,
                    "ref_id": "2d6194e7945563b58be69b5a70887239",
                    "component_id": "F1-2",
                    "title": "Test series 2",
                    "display_string": "Test series 2",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:15:03Z",
                    "system_mtime": "2015-06-11T17:46:12Z",
                    "user_mtime": "2015-06-11T17:46:12Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/2",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Some other fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-30T23:17:57Z",
                    "system_mtime": "2015-06-30T23:17:57Z",
                    "user_mtime": "2015-06-30T23:17:57Z",
                    "suppressed": False,
                    "id_0": "F2",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-06-29",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "date_type": "bulk",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/2",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/2/tree"},
                }
            },
        ),
    ],
)
def test_augment_ids(get, post):
    client = ArchivesSpaceClient(**AUTH)
    data = client.augment_resource_ids(
        ["/repositories/2/resources/1", "/repositories/2/resources/2"]
    )
    assert len(data) == 2
    assert data[0]["title"] == "Test fonds"
    assert data[0]["type"] == "resource"
    assert data[1]["title"] == "Some other fonds"
    assert data[1]["type"] == "resource"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "aee48628790858481963be28725c8023a0d4c8c01e3911ce5ca5ae74ad9f7501",
                }
            },
        )
    ],
)
def test_get_resource_type(post):
    client = ArchivesSpaceClient(**AUTH)
    assert client.resource_type("/repositories/2/resources/2") == "resource"
    assert (
        client.resource_type("/repositories/2/archival_objects/3")
        == "resource_component"
    )


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "aee48628790858481963be28725c8023a0d4c8c01e3911ce5ca5ae74ad9f7501",
                }
            },
        )
    ],
)
def test_get_resource_type_raises_on_invalid_input(post):
    client = ArchivesSpaceClient(**AUTH)
    with pytest.raises(ArchivesSpaceError):
        client.resource_type("invalid")


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "5bcf9db74ea8c5d9238ee4266d9895495e929c218bf49b509f62ac0e3f22abba",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "total_hits": 1,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        }
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_identifier_search_exact_match(get, post):
    client = ArchivesSpaceClient(**AUTH)
    assert client.find_collection_ids(identifier="F1") == [
        "/repositories/2/resources/1"
    ]
    assert client.count_collections(identifier="F1") == 1
    assert len(client.find_collections(identifier="F1")) == 1


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "b75502af2ca0fb38605e8dff31ffe026f078db9bacb6a4bedfa1339d2ef15389",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 0,
                    "total_hits": 0,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 0,
                    "total_hits": 0,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 0,
                    "total_hits": 0,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 2,
                    "offset_first": 11,
                    "offset_last": 3,
                    "total_hits": 3,
                    "results": [],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-08-12T20:24:17Z","user_mtime":"2015-08-12T20:24:17Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-08-12T20:24:18Z","system_mtime":"2015-08-12T20:24:18Z","user_mtime":"2015-08-12T20:24:18Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-08-12T20:24:17Z",
                            "system_mtime": "2015-08-12T20:24:17Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":0,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-06-30T23:17:57Z","user_mtime":"2015-06-30T23:17:57Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-06-30T23:17:57Z",
                            "system_mtime": "2015-06-30T23:17:57Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test subseries",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_identifier_search_wildcard(get, post):
    client = ArchivesSpaceClient(**AUTH)
    # Searching for an identifier prefix with no wildcard returns nothing
    assert client.find_collection_ids(identifier="F") == []
    assert client.count_collections(identifier="F") == 0
    assert len(client.find_collections(identifier="F")) == 0

    assert client.find_collection_ids(identifier="F*") == [
        "/repositories/2/resources/1",
        "/repositories/2/resources/2",
    ]
    assert client.count_collections(identifier="F*") == 2
    assert len(client.find_collections(identifier="F*")) == 2


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "3b25bdce7d637c3e1aa036cb9bc2676e00e4581aa870133fd8c44b3416ad30bd",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 3,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/3",
                    "warnings": [],
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-10-08T21:38:10Z",
                    "system_mtime": "2015-10-08T21:38:30Z",
                    "user_mtime": "2015-10-08T21:38:30Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "collection",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-08T21:38:31Z",
                            "system_mtime": "2015-10-08T21:38:31Z",
                            "user_mtime": "2015-10-08T21:38:31Z",
                            "portion": "whole",
                            "extent_type": "files",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "2015-01-01",
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-08T21:38:31Z",
                            "system_mtime": "2015-10-08T21:38:31Z",
                            "user_mtime": "2015-10-08T21:38:31Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/2",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/2/tree"},
                }
            },
        )
    ],
)
def test_add_child_resource(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child(
        "/repositories/2/resources/2", title="Test child", level="item"
    )
    assert uri == "/repositories/2/archival_objects/3"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "6b40dd8a10ba935c976eb1789790ec116a992f32b09b1bd5a3e54a720d1f9907",
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 5,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/5",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "83762cfcdc683e815d02aa562158e962",
                    "title": "Test series",
                    "display_string": "Test series",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-10-08T21:40:59Z",
                    "system_mtime": "2015-10-08T21:47:38Z",
                    "user_mtime": "2015-10-08T21:47:38Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/2"},
                    "has_unpublished_ancestor": True,
                }
            },
        )
    ],
)
def test_add_child_resource_component(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child(
        "/repositories/2/archival_objects/1", title="Test child", level="item"
    )
    assert uri == "/repositories/2/archival_objects/5"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "60accd40600bbde50c5d8c237d6e34b0826bdd7385147bdf38a99f519ea26cc4",
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 24,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/24",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Sarah's New Testing Collection",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2016-01-08T18:48:56Z",
                    "system_mtime": "2016-01-08T18:48:56Z",
                    "user_mtime": "2016-01-08T18:48:56Z",
                    "suppressed": False,
                    "id_0": "7890",
                    "level": "collection",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2016-01-08T18:48:56Z",
                            "system_mtime": "2016-01-08T18:48:56Z",
                            "user_mtime": "2016-01-08T18:48:56Z",
                            "portion": "whole",
                            "extent_type": "terabytes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "2010-2015",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2016-01-08T18:48:56Z",
                            "system_mtime": "2016-01-08T18:48:56Z",
                            "user_mtime": "2016-01-08T18:48:56Z",
                            "date_type": "bulk",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/5",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/5/tree"},
                }
            },
        )
    ],
)
def test_adding_child_with_note(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child(
        "/repositories/2/resources/5",
        title="Test child",
        level="item",
        notes=[{"type": "odd", "content": "This is a test note"}],
    )
    assert uri == "/repositories/2/archival_objects/24"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "a76c444cf976f1910c78069d7419792904c754f609960bb098a09a8367c78de2",
                    "user": {
                        "lock_version": 876,
                        "username": "admin",
                        "name": "Administrator",
                        "is_system_user": True,
                        "create_time": "2015-06-11T17:04:21Z",
                        "system_mtime": "2016-02-01T19:57:27Z",
                        "user_mtime": "2016-02-01T19:57:27Z",
                        "jsonmodel_type": "user",
                        "groups": [],
                        "is_admin": True,
                        "uri": "/users/1",
                        "agent_record": {"ref": "/agents/people/1"},
                        "permissions": {
                            "/repositories/1": [
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                            ],
                            "_archivesspace": [
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                            ],
                        },
                    },
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 29,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/29",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 11,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-12-03T00:03:41Z",
                    "user_mtime": "2015-12-03T00:03:41Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [{"ref": "/repositories/2/accessions/1"}],
                    "notes": [
                        {
                            "content": ["Singlepart note"],
                            "type": "physdesc",
                            "jsonmodel_type": "note_singlepart",
                            "persistent_id": "cdc013c483de98b8a1762302faf8fd32",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 12,
                    "ref_id": "f25dbd797433c55e35869f7341b65b34",
                    "title": "Test child",
                    "display_string": "Test child",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2016-02-01T19:57:28Z",
                    "system_mtime": "2016-02-01T19:57:28Z",
                    "user_mtime": "2016-02-01T19:57:28Z",
                    "suppressed": False,
                    "level": "recordgrp",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/29",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_posting_contentless_note(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child(
        "/repositories/2/resources/1",
        title="Test child",
        level="recordgrp",
        notes=[{"type": "odd", "content": ""}],
    )
    assert client.get_record(uri)["notes"] == []


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "4adb3e9ec9d6136fd9cd238ea90df00d455a3b3b07b278265eb0ba8a8ef7cf81",
                    "user": {
                        "lock_version": 1033,
                        "username": "admin",
                        "name": "Administrator",
                        "is_system_user": True,
                        "create_time": "2015-06-11T17:04:21Z",
                        "system_mtime": "2016-02-11T00:05:10Z",
                        "user_mtime": "2016-02-11T00:05:10Z",
                        "jsonmodel_type": "user",
                        "groups": [],
                        "is_admin": True,
                        "uri": "/users/1",
                        "agent_record": {"ref": "/agents/people/1"},
                        "permissions": {
                            "/repositories/1": [
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                            ],
                            "_archivesspace": [
                                "administer_system",
                                "become_user",
                                "cancel_importer_job",
                                "create_repository",
                                "delete_archival_record",
                                "delete_classification_record",
                                "delete_event_record",
                                "delete_repository",
                                "import_records",
                                "index_system",
                                "manage_agent_record",
                                "manage_repository",
                                "manage_subject_record",
                                "manage_users",
                                "manage_vocabulary_record",
                                "mediate_edits",
                                "merge_agents_and_subjects",
                                "merge_archival_record",
                                "suppress_archival_record",
                                "system_config",
                                "transfer_archival_record",
                                "transfer_repository",
                                "update_accession_record",
                                "update_classification_record",
                                "update_digital_object_record",
                                "update_event_record",
                                "update_resource_record",
                                "view_all_records",
                                "view_repository",
                                "view_suppressed",
                                "update_location_record",
                                "delete_vocabulary_record",
                                "update_subject_record",
                                "delete_subject_record",
                                "update_agent_record",
                                "delete_agent_record",
                                "update_vocabulary_record",
                                "merge_subject_record",
                                "merge_agent_record",
                            ],
                        },
                    },
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 35,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/35",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 11,
                    "title": "Test fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:08:42Z",
                    "system_mtime": "2015-12-03T00:03:41Z",
                    "user_mtime": "2015-12-03T00:03:41Z",
                    "suppressed": False,
                    "id_0": "F1",
                    "language": "eng",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T00:03:42Z",
                            "system_mtime": "2015-12-03T00:03:42Z",
                            "user_mtime": "2015-12-03T00:03:42Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [{"ref": "/repositories/2/accessions/1"}],
                    "notes": [
                        {
                            "content": ["Singlepart note"],
                            "type": "physdesc",
                            "jsonmodel_type": "note_singlepart",
                            "persistent_id": "cdc013c483de98b8a1762302faf8fd32",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/resources/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 16,
                    "ref_id": "4d6631016cc84c7cc58b46119585df5d",
                    "title": "Test child",
                    "display_string": "Test child",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2016-02-11T00:05:10Z",
                    "system_mtime": "2016-02-11T00:05:10Z",
                    "user_mtime": "2016-02-11T00:05:10Z",
                    "suppressed": False,
                    "level": "recordgrp",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [
                        {
                            "subnotes": [
                                {
                                    "content": "General",
                                    "jsonmodel_type": "note_text",
                                    "publish": True,
                                }
                            ],
                            "jsonmodel_type": "note_multipart",
                            "type": "odd",
                            "persistent_id": "d3587a0e5a752b31858fca9a5d6d499c",
                            "publish": True,
                        },
                        {
                            "subnotes": [
                                {
                                    "content": "Access",
                                    "jsonmodel_type": "note_text",
                                    "publish": True,
                                }
                            ],
                            "jsonmodel_type": "note_multipart",
                            "type": "accessrestrict",
                            "persistent_id": "81b79e0152596bd5e4b6e89ab30e8ccb",
                            "publish": True,
                        },
                    ],
                    "uri": "/repositories/2/archival_objects/35",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_posting_multiple_notes(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child(
        "/repositories/2/resources/1",
        title="Test child",
        level="recordgrp",
        notes=[
            {"type": "odd", "content": "General"},
            {"type": "accessrestrict", "content": "Access"},
        ],
    )
    record = client.get_record(uri)
    assert record["notes"][0]["type"] == "odd"
    assert record["notes"][0]["subnotes"][0]["content"] == "General"
    assert record["notes"][1]["type"] == "accessrestrict"
    assert record["notes"][1]["subnotes"][0]["content"] == "Access"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "2a263c91da801af6dc7548014d02af8b81b2f0916cc7000e05bd5b87a8e96ac7",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "title": "Some other fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-10-08T21:39:44Z",
                    "system_mtime": "2015-10-08T21:39:44Z",
                    "user_mtime": "2015-10-08T21:39:44Z",
                    "suppressed": False,
                    "id_0": "F2",
                    "language": "eng",
                    "level": "collection",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-08T21:39:44Z",
                            "system_mtime": "2015-10-08T21:39:44Z",
                            "user_mtime": "2015-10-08T21:39:44Z",
                            "portion": "whole",
                            "extent_type": "files",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-08T21:39:44Z",
                            "system_mtime": "2015-10-08T21:39:44Z",
                            "user_mtime": "2015-10-08T21:39:44Z",
                            "date_type": "single",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/3",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/3/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=404, **{"json.return_value": {"error": "Resource not found"}}
        ),
    ],
)
@mock.patch(
    "requests.Session.delete",
    side_effect=[
        mock.Mock(
            status_code=200, **{"json.return_value": {"status": "Deleted", "id": 3}}
        )
    ],
)
def test_delete_record_resource(delete, get, post):
    client = ArchivesSpaceClient(**AUTH)
    record_id = "/repositories/2/resources/3"
    assert client.get_record(record_id)
    r = client.delete_record(record_id)
    assert r["status"] == "Deleted"
    with pytest.raises(CommunicationError):
        client.get_record(record_id)


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "b6aa6f982c4fbdd9b470bf4d2f35e1be2bc1c482706eff62ce6e675ece381e1d",
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 0,
                    "ref_id": "245e87ee574547df6c55891ce41187d3",
                    "title": "Test child",
                    "display_string": "Test child",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-10-08T21:48:28Z",
                    "system_mtime": "2015-10-08T21:48:28Z",
                    "user_mtime": "2015-10-08T21:48:28Z",
                    "suppressed": False,
                    "level": "item",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/4",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/2"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=404,
            **{"json.return_value": {"error": "ArchivalObject not found"}},
        ),
    ],
)
@mock.patch(
    "requests.Session.delete",
    side_effect=[
        mock.Mock(
            status_code=200, **{"json.return_value": {"status": "Deleted", "id": 4}}
        )
    ],
)
def test_delete_record_archival_object(delete, get, post):
    client = ArchivesSpaceClient(**AUTH)
    record_id = "/repositories/2/archival_objects/4"
    assert client.get_record(record_id)
    r = client.delete_record(record_id)
    assert r["status"] == "Deleted"
    with pytest.raises(CommunicationError):
        client.get_record(record_id)


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "fd47f17b9643680d69818993e40ed986f771b70a41360b1df3b7dc26d5fd7983"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 3,
                    "lock_version": 8,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/3",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 7,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test subseries",
                    "display_string": "Test subseries, 2014-01-01 - 2015-01-01",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-10-29T23:50:50Z",
                    "user_mtime": "2015-10-29T23:50:50Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2014-01-01",
                            "end": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-29T23:50:50Z",
                            "system_mtime": "2015-10-29T23:50:50Z",
                            "user_mtime": "2015-10-29T23:50:50Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 7,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test subseries",
                    "display_string": "Test subseries, 2014-01-01 - 2015-01-01",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-10-29T23:50:50Z",
                    "user_mtime": "2015-10-29T23:50:50Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2014-01-01",
                            "end": "2015-01-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-10-29T23:50:50Z",
                            "system_mtime": "2015-10-29T23:50:50Z",
                            "user_mtime": "2015-10-29T23:50:50Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 8,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-11-02T22:53:07Z",
                    "user_mtime": "2015-11-02T22:53:07Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-11-02T22:53:07Z",
                            "system_mtime": "2015-11-02T22:53:07Z",
                            "user_mtime": "2015-11-02T22:53:07Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [
                        {
                            "type": "odd",
                            "jsonmodel_type": "note_multipart",
                            "subnotes": [
                                {
                                    "content": "This is a test note",
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                }
                            ],
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_edit_archival_object(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    original = client.get_record("/repositories/2/archival_objects/3")
    assert original["title"] == "Test subseries"
    assert original["dates"][0]["end"] == "2015-01-01"
    assert not original["notes"]
    new_record = {
        "id": "/repositories/2/archival_objects/3",
        "title": "Test edited subseries",
        "start_date": "2014-11-01",
        "end_date": "2015-11-01",
        "date_expression": "November, 2014 to November, 2015",
        "notes": [{"type": "odd", "content": "This is a test note"}],
    }
    client.edit_record(new_record)
    updated = client.get_record("/repositories/2/archival_objects/3")
    assert updated["title"] == new_record["title"]
    assert updated["dates"][0]["begin"] == new_record["start_date"]
    assert updated["dates"][0]["end"] == new_record["end_date"]
    assert updated["dates"][0]["expression"] == new_record["date_expression"]
    assert updated["notes"][0]["type"] == new_record["notes"][0]["type"]
    assert (
        updated["notes"][0]["subnotes"][0]["content"]
        == new_record["notes"][0]["content"]
    )


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "d84ec1437008dcfd2fce24b3d63a3d396a2e04d9c958b275b265605362f27c9c"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 3,
                    "lock_version": 11,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/3",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 10,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-12-04T00:59:36Z",
                    "user_mtime": "2015-12-03T01:24:00Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/7"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/8"
                            },
                        },
                    ],
                    "notes": [
                        {
                            "jsonmodel_type": "note_multipart",
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "subnotes": [
                                {
                                    "content": "This is a test note",
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                }
                            ],
                            "type": "odd",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 10,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-12-04T00:59:36Z",
                    "user_mtime": "2015-12-03T01:24:00Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/7"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/8"
                            },
                        },
                    ],
                    "notes": [
                        {
                            "jsonmodel_type": "note_multipart",
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "subnotes": [
                                {
                                    "content": "This is a test note",
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                }
                            ],
                            "type": "odd",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 11,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries w/ empty note",
                    "display_string": "Test edited subseries w/ empty note, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2016-02-02T01:23:32Z",
                    "user_mtime": "2016-02-02T01:23:32Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2016-02-02T01:23:33Z",
                            "system_mtime": "2016-02-02T01:23:33Z",
                            "user_mtime": "2016-02-02T01:23:33Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2016-02-02T01:23:33Z",
                            "system_mtime": "2016-02-02T01:23:33Z",
                            "user_mtime": "2016-02-02T01:23:33Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/7"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2016-02-02T01:23:33Z",
                            "system_mtime": "2016-02-02T01:23:33Z",
                            "user_mtime": "2016-02-02T01:23:33Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/8"
                            },
                        },
                    ],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_edit_record_empty_note(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    original = client.get_record("/repositories/2/archival_objects/3")
    assert original["notes"]
    new_record = {
        "id": "/repositories/2/archival_objects/3",
        "title": "Test edited subseries w/ empty note",
        "start_date": "2014-11-01",
        "end_date": "2015-11-01",
        "date_expression": "November, 2014 to November, 2015",
        "notes": [{"type": "odd", "content": ""}],
    }
    client.edit_record(new_record)
    updated = client.get_record("/repositories/2/archival_objects/3")
    assert not updated["notes"]


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "ad772ecb08b2d161a484c540690f5e93a61814cef5f0b362ac9ab1d833a139ec"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 9253,
                    "lock_version": 1,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/9253",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 0,
                    "ref_id": "deba72c5e3a1926de775574d7d2ca269",
                    "title": "holly-test",
                    "display_string": "holly-test",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2017-02-03T23:15:10Z",
                    "system_mtime": "2017-02-09T22:13:51Z",
                    "user_mtime": "2017-02-03T23:15:10Z",
                    "suppressed": False,
                    "level": "file",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/9253",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/4"},
                    "parent": {"ref": "/repositories/2/archival_objects/8887"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 0,
                    "publish": False,
                    "ref_id": "deba72c5e3a1926de775574d7d2ca269",
                    "title": "holly-test",
                    "display_string": "holly-test",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2017-02-03T23:15:10Z",
                    "system_mtime": "2017-02-09T22:14:36Z",
                    "user_mtime": "2017-02-09T22:14:36Z",
                    "suppressed": False,
                    "level": "file",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [
                        {
                            "subnotes": [
                                {
                                    "content": "General note content",
                                    "jsonmodel_type": "note_text",
                                    "publish": True,
                                }
                            ],
                            "jsonmodel_type": "note_multipart",
                            "type": "odd",
                            "persistent_id": "5c593d5dc0281cbdeeebe07126375487",
                            "publish": True,
                        },
                        {
                            "subnotes": [
                                {
                                    "content": "Access restriction note",
                                    "jsonmodel_type": "note_text",
                                    "publish": True,
                                }
                            ],
                            "jsonmodel_type": "note_multipart",
                            "type": "accessrestrict",
                            "persistent_id": "f2c649e8a7c1cba86647f26cad464804",
                            "publish": True,
                        },
                    ],
                    "uri": "/repositories/2/archival_objects/9253",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/4"},
                    "parent": {"ref": "/repositories/2/archival_objects/8887"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_edit_record_multiple_notes(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    new_record = {
        "id": "/repositories/2/archival_objects/9253",
        "notes": [
            {"type": "odd", "content": "General note content"},
            {"type": "accessrestrict", "content": "Access restriction note"},
        ],
    }
    client.edit_record(new_record)
    updated = client.get_record("/repositories/2/archival_objects/9253")
    assert updated["notes"][0]["type"] == new_record["notes"][0]["type"]
    assert (
        updated["notes"][0]["subnotes"][0]["content"]
        == new_record["notes"][0]["content"]
    )

    assert updated["notes"][1]["type"] == new_record["notes"][1]["type"]
    assert (
        updated["notes"][1]["subnotes"][0]["content"]
        == new_record["notes"][1]["content"]
    )


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "2e06c62e8123488f45750959e77129fd7bf532fec10ffd0301568ffedee188de"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 8,
                    "lock_version": 0,
                    "stale": None,
                    "uri": "/repositories/2/digital_objects/8",
                    "warnings": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 3,
                    "lock_version": 10,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/3",
                    "warnings": [],
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 9,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-12-03T01:23:47Z",
                    "user_mtime": "2015-12-03T01:23:47Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:23:47Z",
                            "system_mtime": "2015-12-03T01:23:47Z",
                            "user_mtime": "2015-12-03T01:23:47Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:23:47Z",
                            "system_mtime": "2015-12-03T01:23:47Z",
                            "user_mtime": "2015-12-03T01:23:47Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/7"
                            },
                        }
                    ],
                    "notes": [
                        {
                            "subnotes": [
                                {
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                    "content": "This is a test note",
                                }
                            ],
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "type": "odd",
                            "jsonmodel_type": "note_multipart",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        )
    ],
)
def test_add_digital_object(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object(
        "/repositories/2/archival_objects/3",
        identifier="38c99e89-20a1-4831-ba57-813fb6420e59",
        title="Test digital object",
    )
    assert do["id"] == "/repositories/2/digital_objects/8"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "d6226a61876a4e58aff36f9a4d549330abe76909660b1f3de4f50f11db6750c0"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 7,
                    "lock_version": 0,
                    "stale": None,
                    "uri": "/repositories/2/digital_objects/7",
                    "warnings": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 3,
                    "lock_version": 9,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/3",
                    "warnings": [],
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 8,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-12-03T00:03:42Z",
                    "user_mtime": "2015-11-02T22:53:07Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-11-02T22:53:07Z",
                            "system_mtime": "2015-11-02T22:53:07Z",
                            "user_mtime": "2015-11-02T22:53:07Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [
                        {
                            "type": "odd",
                            "jsonmodel_type": "note_multipart",
                            "subnotes": [
                                {
                                    "content": "This is a test note",
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                }
                            ],
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "digital_object_id": "925bfc8a-d6f8-4479-9b6a-d811a4e7f6bf",
                    "title": "Test digital object with note",
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-12-03T01:23:47Z",
                    "system_mtime": "2015-12-03T01:23:47Z",
                    "user_mtime": "2015-12-03T01:23:47Z",
                    "suppressed": False,
                    "digital_object_type": "text",
                    "jsonmodel_type": "digital_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "file_versions": [],
                    "notes": [
                        {
                            "type": "originalsloc",
                            "jsonmodel_type": "note_digital_object",
                            "content": ["The ether"],
                            "persistent_id": "1b5d0feafe3c9d07fa515eb1e532c84c",
                            "publish": True,
                        },
                        {
                            "type": "note",
                            "jsonmodel_type": "note_digital_object",
                            "content": ["This is a test note"],
                            "persistent_id": "27c98cdc882d66ee0177579bc89821ea",
                            "publish": True,
                        },
                    ],
                    "linked_instances": [{"ref": "/repositories/2/archival_objects/3"}],
                    "uri": "/repositories/2/digital_objects/7",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/digital_objects/7/tree"},
                }
            },
        ),
    ],
)
def test_digital_object_with_location_of_originals_note(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object(
        "/repositories/2/archival_objects/3",
        identifier="925bfc8a-d6f8-4479-9b6a-d811a4e7f6bf",
        title="Test digital object with note",
        location_of_originals="The ether",
    )
    note = client.get_record(do["id"])["notes"][0]
    assert note["content"][0] == "The ether"
    assert note["type"] == "originalsloc"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "1ea928f79eb921a2857d5ef2f4ffa1a0d3c9a8daf667c69e7b64fd6e333dd7a3"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 9,
                    "lock_version": 0,
                    "stale": None,
                    "uri": "/repositories/2/digital_objects/9",
                    "warnings": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Updated",
                    "id": 21,
                    "lock_version": 1,
                    "stale": True,
                    "uri": "/repositories/2/archival_objects/21",
                    "warnings": [],
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 1,
                    "publish": False,
                    "ref_id": "4e160068664159ca2107de634a3183f9",
                    "title": "Child with singlepart note",
                    "display_string": "Child with singlepart note",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2016-01-07T18:40:06Z",
                    "system_mtime": "2016-01-07T18:40:06Z",
                    "user_mtime": "2016-01-07T18:40:06Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [
                        {
                            "jsonmodel_type": "note_singlepart",
                            "type": "abstract",
                            "content": ["This is an abstract"],
                            "persistent_id": "a8704fed6c62a8fa51dbc17affc8df5f",
                            "publish": False,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/21",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/2"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "digital_object_id": "5f464db2-9365-492f-b7c7-7958baeb0388",
                    "title": "Test digital object whose parent has a singlepart note",
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2016-01-07T18:46:35Z",
                    "system_mtime": "2016-01-07T18:46:35Z",
                    "user_mtime": "2016-01-07T18:46:35Z",
                    "suppressed": False,
                    "digital_object_type": "text",
                    "jsonmodel_type": "digital_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "file_versions": [],
                    "notes": [
                        {
                            "type": "note",
                            "jsonmodel_type": "note_digital_object",
                            "content": ["This is an abstract"],
                            "persistent_id": "8c569b3744607ce9dbb17b1f2ca4dff0",
                            "publish": False,
                        }
                    ],
                    "linked_instances": [
                        {"ref": "/repositories/2/archival_objects/21"}
                    ],
                    "uri": "/repositories/2/digital_objects/9",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/digital_objects/9/tree"},
                }
            },
        ),
    ],
)
def test_adding_a_digital_object_to_a_record_with_a_singlepart_note(
    get, session_post, post
):
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object(
        "/repositories/2/archival_objects/21",
        identifier="5f464db2-9365-492f-b7c7-7958baeb0388",
        title="Test digital object whose parent has a singlepart note",
    )
    note = client.get_record(do["id"])["notes"][0]
    assert len(note["content"]) == 1


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "8f0bce11c556e20e7ba67b6501ace4275f3d9f6bc570fd9ebe6cab5aaeaa9d88"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 3,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/digital_object_components/3",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "digital_object_id": "1",
                    "title": "Test digi object",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-11-18T21:29:33Z",
                    "system_mtime": "2015-11-18T21:29:33Z",
                    "user_mtime": "2015-11-18T21:29:33Z",
                    "suppressed": False,
                    "jsonmodel_type": "digital_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "file_versions": [],
                    "notes": [],
                    "linked_instances": [],
                    "uri": "/repositories/2/digital_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/digital_objects/1/tree"},
                }
            },
        )
    ],
)
def test_add_digital_object_component(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    doc = client.add_digital_object_component(
        "/repositories/2/digital_objects/1",
        label="Test DOC",
        title="This is a test DOC",
    )
    assert doc["id"] == "/repositories/2/digital_object_components/3"
    assert doc["label"] == "Test DOC"
    assert doc["title"] == "This is a test DOC"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "d188da574cacd0d7f8f9a12a08b0441b415fed76b83e0019ebcad0af54a2c1f8"
                }
            },
        ),
    ],
)
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "status": "Created",
                    "id": 5,
                    "lock_version": 0,
                    "stale": True,
                    "uri": "/repositories/2/digital_object_components/5",
                    "warnings": [],
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "digital_object_id": "1",
                    "title": "Test digi object",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-11-18T21:29:33Z",
                    "system_mtime": "2015-11-18T21:29:33Z",
                    "user_mtime": "2015-11-18T21:29:33Z",
                    "suppressed": False,
                    "jsonmodel_type": "digital_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "file_versions": [],
                    "notes": [],
                    "linked_instances": [],
                    "uri": "/repositories/2/digital_objects/1",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/digital_objects/1/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 0,
                    "position": 1,
                    "title": "This is a child DOC",
                    "display_string": "This is a child DOC",
                    "label": "Child DOC",
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-12-03T01:07:54Z",
                    "system_mtime": "2015-12-03T01:07:54Z",
                    "user_mtime": "2015-12-03T01:07:54Z",
                    "suppressed": False,
                    "jsonmodel_type": "digital_object_component",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "file_versions": [],
                    "notes": [],
                    "uri": "/repositories/2/digital_object_components/5",
                    "repository": {"ref": "/repositories/2"},
                    "digital_object": {"ref": "/repositories/2/digital_objects/1"},
                    "parent": {"ref": "/repositories/2/digital_object_components/3"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
    ],
)
def test_add_nested_digital_object_component(get, session_post, post):
    client = ArchivesSpaceClient(**AUTH)
    parent = "/repositories/2/digital_object_components/3"
    doc = client.add_digital_object_component(
        "/repositories/2/digital_objects/1",
        parent_digital_object_component=parent,
        label="Child DOC",
        title="This is a child DOC",
    )
    assert client.get_record(doc["id"])["parent"]["ref"] == parent


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "d81a358cd432e897d69df8d17afe43dc0b70f1bc6db988f1dc291becbc510663"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 10,
                    "position": 0,
                    "publish": False,
                    "ref_id": "e61c441cd04eb5731ce64de35a4339ff",
                    "component_id": "F1-1-1",
                    "title": "Test edited subseries",
                    "display_string": "Test edited subseries, November, 2014 to November, 2015",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:20:19Z",
                    "system_mtime": "2015-12-04T00:59:36Z",
                    "user_mtime": "2015-12-03T01:24:00Z",
                    "suppressed": False,
                    "level": "subseries",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [
                        {
                            "lock_version": 0,
                            "expression": "November, 2014 to November, 2015",
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "date_type": "inclusive",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/7"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-03T01:24:00Z",
                            "system_mtime": "2015-12-03T01:24:00Z",
                            "user_mtime": "2015-12-03T01:24:00Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/8"
                            },
                        },
                    ],
                    "notes": [
                        {
                            "jsonmodel_type": "note_multipart",
                            "persistent_id": "063373886a2f23d03fe1a51f7c96ca8b",
                            "subnotes": [
                                {
                                    "content": "This is a test note",
                                    "publish": True,
                                    "jsonmodel_type": "note_text",
                                }
                            ],
                            "type": "odd",
                            "publish": True,
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "parent": {"ref": "/repositories/2/archival_objects/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {
                        "lock_version": 1,
                        "position": 0,
                        "publish": False,
                        "ref_id": "8429037b0f599a1efcca06b9b813700a",
                        "component_id": "F1-1-1-1",
                        "title": "Test file",
                        "display_string": "Test file",
                        "restrictions_apply": False,
                        "created_by": "admin",
                        "last_modified_by": "admin",
                        "create_time": "2015-06-11T17:20:30Z",
                        "system_mtime": "2015-12-04T00:59:36Z",
                        "user_mtime": "2015-06-11T17:45:40Z",
                        "suppressed": False,
                        "level": "file",
                        "jsonmodel_type": "archival_object",
                        "external_ids": [],
                        "subjects": [],
                        "linked_events": [],
                        "extents": [],
                        "dates": [],
                        "external_documents": [],
                        "rights_statements": [],
                        "linked_agents": [],
                        "instances": [],
                        "notes": [],
                        "uri": "/repositories/2/archival_objects/4",
                        "repository": {"ref": "/repositories/2"},
                        "resource": {"ref": "/repositories/2/resources/1"},
                        "parent": {"ref": "/repositories/2/archival_objects/3"},
                        "has_unpublished_ancestor": True,
                    }
                ]
            },
        ),
    ],
)
def test_date_expression(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children(
        "/repositories/2/archival_objects/3", recurse_max_level=1
    )
    assert record["date_expression"] == "November, 2014 to November, 2015"


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "2661a9a15d0a2667572979a5d5d88678fc79554aa9cca99b48111c2da65508a5"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 1,
                    "position": 1,
                    "publish": False,
                    "ref_id": "2d6194e7945563b58be69b5a70887239",
                    "component_id": "F1-2",
                    "title": "Test series 2",
                    "display_string": "Test series 2",
                    "restrictions_apply": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-11T17:15:03Z",
                    "system_mtime": "2015-12-03T00:03:42Z",
                    "user_mtime": "2015-06-11T17:46:12Z",
                    "suppressed": False,
                    "level": "series",
                    "jsonmodel_type": "archival_object",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [],
                    "dates": [],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/2",
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "has_unpublished_ancestor": True,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {
                        "lock_version": 0,
                        "position": 0,
                        "ref_id": "f9db798809e30de21950f0414f09fb76",
                        "title": "Test bad resource",
                        "display_string": "Test bad resource",
                        "restrictions_apply": False,
                        "created_by": "admin",
                        "last_modified_by": "admin",
                        "create_time": "2015-09-10T18:21:17Z",
                        "system_mtime": "2015-12-02T01:05:22Z",
                        "user_mtime": "2015-09-10T18:21:17Z",
                        "suppressed": False,
                        "level": "series",
                        "jsonmodel_type": "archival_object",
                        "external_ids": [],
                        "subjects": [],
                        "linked_events": [],
                        "extents": [],
                        "dates": [],
                        "external_documents": [],
                        "rights_statements": [],
                        "linked_agents": [],
                        "instances": [],
                        "notes": [],
                        "uri": "/repositories/2/archival_objects/7",
                        "repository": {"ref": "/repositories/2"},
                        "resource": {"ref": "/repositories/2/resources/2"},
                        "parent": {"ref": "/repositories/2/archival_objects/2"},
                        "has_unpublished_ancestor": True,
                    }
                ]
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": []}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "lock_version": 4,
                    "title": "Some other fonds",
                    "publish": False,
                    "restrictions": False,
                    "created_by": "admin",
                    "last_modified_by": "admin",
                    "create_time": "2015-06-30T23:17:57Z",
                    "system_mtime": "2015-12-02T01:05:21Z",
                    "user_mtime": "2015-12-02T01:05:21Z",
                    "suppressed": False,
                    "id_0": "F2",
                    "level": "fonds",
                    "jsonmodel_type": "resource",
                    "external_ids": [],
                    "subjects": [],
                    "linked_events": [],
                    "extents": [
                        {
                            "lock_version": 0,
                            "number": "1",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "portion": "whole",
                            "extent_type": "cassettes",
                            "jsonmodel_type": "extent",
                        }
                    ],
                    "dates": [
                        {
                            "lock_version": 0,
                            "begin": "2015-06-29",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "date_type": "bulk",
                            "label": "creation",
                            "jsonmodel_type": "date",
                        }
                    ],
                    "external_documents": [],
                    "rights_statements": [],
                    "linked_agents": [],
                    "instances": [
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/3"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:22Z",
                            "system_mtime": "2015-12-02T01:05:22Z",
                            "user_mtime": "2015-12-02T01:05:22Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/4"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:22Z",
                            "system_mtime": "2015-12-02T01:05:22Z",
                            "user_mtime": "2015-12-02T01:05:22Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/5"
                            },
                        },
                        {
                            "lock_version": 0,
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "create_time": "2015-12-02T01:05:22Z",
                            "system_mtime": "2015-12-02T01:05:22Z",
                            "user_mtime": "2015-12-02T01:05:22Z",
                            "instance_type": "digital_object",
                            "jsonmodel_type": "instance",
                            "digital_object": {
                                "ref": "/repositories/2/digital_objects/6"
                            },
                        },
                    ],
                    "deaccessions": [],
                    "related_accessions": [],
                    "notes": [],
                    "uri": "/repositories/2/resources/2",
                    "repository": {"ref": "/repositories/2"},
                    "tree": {"ref": "/repositories/2/resources/2/tree"},
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "total_hits": 2,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":11,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-12-03T00:03:41Z","user_mtime":"2015-12-03T00:03:41Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[{"content":["Singlepart note"],"type":"physdesc","jsonmodel_type":"note_singlepart","persistent_id":"cdc013c483de98b8a1762302faf8fd32","publish":true}],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-03T00:03:41Z",
                            "system_mtime": "2015-12-03T00:03:41Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":4,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/3","_resolved":{"lock_version":4,"digital_object_id":"f808032e-c6ec-4242-b7aa-5395988b9f7e","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:38Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:38Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"4e5eec95fcb62440f20a4f5b89c6d16b","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/3","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/3/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/4","_resolved":{"lock_version":3,"digital_object_id":"5517ddb1-36dd-4a02-a363-f1571982670f","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:53Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:53Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"bdfe911944a3d26a9fd43455aa968c52","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/4","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/4/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/5","_resolved":{"lock_version":2,"digital_object_id":"8ea81c4d-6df3-4775-a314-4bef4f44dd3c","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:04:57Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:04:57Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"68242ba5c0cbff4b674c6a2fa2335ad0","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/5","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/5/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/6","_resolved":{"lock_version":1,"digital_object_id":"a1672927-9a56-41c4-b423-5d76e4a1c660","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"3453d8096aabc607723b4359ab8fdd3c","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/6","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/6/tree"}}}}],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series, 1950 - 1972",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test edited subseries, November, 2014 to November, 2015",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child",
                            "id": 13,
                            "record_uri": "/repositories/2/archival_objects/13",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 2",
                            "id": 14,
                            "record_uri": "/repositories/2/archival_objects/14",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "item",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 3",
                            "id": 16,
                            "record_uri": "/repositories/2/archival_objects/16",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child with note",
                            "id": 17,
                            "record_uri": "/repositories/2/archival_objects/17",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child final",
                            "id": 18,
                            "record_uri": "/repositories/2/archival_objects/18",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 19,
                            "record_uri": "/repositories/2/archival_objects/19",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 20,
                            "record_uri": "/repositories/2/archival_objects/20",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        }
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_empty_dates(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_children(
        "/repositories/2/archival_objects/2"
    )
    assert record["dates"] == ""
    assert record["date_expression"] == ""
    record = client.get_resource_component_and_children(
        "/repositories/2/resources/2", recurse_max_level=1
    )
    # dates are mandatory for resources, so this record does have a date but no expression
    assert record["date_expression"] == ""
    collections = client.find_collections()
    assert collections[0]["date_expression"] == ""


@mock.patch(
    "requests.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "session": "3436096c34006577491aae6c6dc485ce5a987afd90f79366c18ec63389ddb456"
                }
            },
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "this_page": 1,
                    "offset_first": 1,
                    "offset_last": 3,
                    "total_hits": 3,
                    "results": [
                        {
                            "id": "/repositories/2/resources/1",
                            "title": "Test fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":11,"title":"Test fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-11T17:08:42Z","system_mtime":"2015-12-03T00:03:41Z","user_mtime":"2015-12-03T00:03:41Z","suppressed":false,"id_0":"F1","language":"eng","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-01-01","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-03T00:03:42Z","system_mtime":"2015-12-03T00:03:42Z","user_mtime":"2015-12-03T00:03:42Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[{"ref":"/repositories/2/accessions/1"}],"notes":[{"content":["Singlepart note"],"type":"physdesc","jsonmodel_type":"note_singlepart","persistent_id":"cdc013c483de98b8a1762302faf8fd32","publish":true}],"uri":"/repositories/2/resources/1","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/1/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-03T00:03:41Z",
                            "system_mtime": "2015-12-03T00:03:41Z",
                            "create_time": "2015-06-11T17:08:42Z",
                            "level": "fonds",
                            "identifier": "F1",
                            "language": "eng",
                            "restrictions": "false",
                            "four_part_id": "F1",
                            "uri": "/repositories/2/resources/1",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/2",
                            "title": "Some other fonds",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":4,"title":"Some other fonds","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-06-30T23:17:57Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"id_0":"F2","level":"fonds","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"1","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2015-06-29","created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","date_type":"bulk","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:21Z","user_mtime":"2015-12-02T01:05:21Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/3","_resolved":{"lock_version":4,"digital_object_id":"f808032e-c6ec-4242-b7aa-5395988b9f7e","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:38Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:38Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"4e5eec95fcb62440f20a4f5b89c6d16b","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/3","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/3/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/4","_resolved":{"lock_version":3,"digital_object_id":"5517ddb1-36dd-4a02-a363-f1571982670f","title":"test","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T00:55:53Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T00:55:53Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"bdfe911944a3d26a9fd43455aa968c52","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/4","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/4/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/5","_resolved":{"lock_version":2,"digital_object_id":"8ea81c4d-6df3-4775-a314-4bef4f44dd3c","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:04:57Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:04:57Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"68242ba5c0cbff4b674c6a2fa2335ad0","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/5","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/5/tree"}}}},{"lock_version":0,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:22Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:22Z","instance_type":"digital_object","jsonmodel_type":"instance","digital_object":{"ref":"/repositories/2/digital_objects/6","_resolved":{"lock_version":1,"digital_object_id":"a1672927-9a56-41c4-b423-5d76e4a1c660","title":"Some other fonds","restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2015-12-02T01:05:21Z","system_mtime":"2015-12-02T01:05:22Z","user_mtime":"2015-12-02T01:05:21Z","suppressed":false,"digital_object_type":"text","jsonmodel_type":"digital_object","external_ids":[],"subjects":[],"linked_events":[],"extents":[],"dates":[],"external_documents":[],"rights_statements":[],"linked_agents":[],"file_versions":[],"notes":[{"content":["test"],"type":"originalsloc","jsonmodel_type":"note_digital_object","persistent_id":"3453d8096aabc607723b4359ab8fdd3c","publish":true}],"linked_instances":[{"ref":"/repositories/2/resources/2"}],"uri":"/repositories/2/digital_objects/6","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/digital_objects/6/tree"}}}}],"deaccessions":[],"related_accessions":[],"notes":[],"uri":"/repositories/2/resources/2","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/2/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2015-12-02T01:05:21Z",
                            "system_mtime": "2015-12-02T01:05:21Z",
                            "create_time": "2015-06-30T23:17:57Z",
                            "level": "fonds",
                            "identifier": "F2",
                            "restrictions": "false",
                            "four_part_id": "F2",
                            "uri": "/repositories/2/resources/2",
                            "jsonmodel_type": "resource",
                        },
                        {
                            "id": "/repositories/2/resources/4",
                            "title": "Resource with a multipart contentless note",
                            "primary_type": "resource",
                            "types": ["resource"],
                            "json": '{"lock_version":1,"title":"Resource with a multipart contentless note","publish":false,"restrictions":false,"created_by":"admin","last_modified_by":"admin","create_time":"2016-01-07T20:51:13Z","system_mtime":"2016-01-07T20:53:13Z","user_mtime":"2016-01-07T20:53:13Z","suppressed":false,"id_0":"A","id_1":"6","language":"ain","level":"collection","jsonmodel_type":"resource","external_ids":[],"subjects":[],"linked_events":[],"extents":[{"lock_version":0,"number":"5","created_by":"admin","last_modified_by":"admin","create_time":"2016-01-07T20:53:14Z","system_mtime":"2016-01-07T20:53:14Z","user_mtime":"2016-01-07T20:53:14Z","portion":"whole","extent_type":"cassettes","jsonmodel_type":"extent"}],"dates":[{"lock_version":0,"begin":"2016-01-06","created_by":"admin","last_modified_by":"admin","create_time":"2016-01-07T20:53:14Z","system_mtime":"2016-01-07T20:53:14Z","user_mtime":"2016-01-07T20:53:14Z","date_type":"single","label":"creation","jsonmodel_type":"date"}],"external_documents":[],"rights_statements":[],"linked_agents":[],"instances":[],"deaccessions":[],"related_accessions":[],"notes":[{"jsonmodel_type":"note_multipart","persistent_id":"042fd712c1eae93e51fde8b4da1c455d","type":"bioghist","subnotes":[{"jsonmodel_type":"note_orderedlist","title":"First","items":["Second"],"publish":false}],"publish":false}],"uri":"/repositories/2/resources/4","repository":{"ref":"/repositories/2"},"tree":{"ref":"/repositories/2/resources/4/tree"}}',
                            "suppressed": False,
                            "publish": False,
                            "system_generated": False,
                            "repository": "/repositories/2",
                            "created_by": "admin",
                            "last_modified_by": "admin",
                            "user_mtime": "2016-01-07T20:53:13Z",
                            "system_mtime": "2016-01-07T20:53:13Z",
                            "create_time": "2016-01-07T20:51:13Z",
                            "level": "collection",
                            "identifier": "A-6",
                            "language": "ain",
                            "restrictions": "false",
                            "four_part_id": "A 6",
                            "uri": "/repositories/2/resources/4",
                            "jsonmodel_type": "resource",
                        },
                    ],
                    "facets": {
                        "facet_queries": {},
                        "facet_fields": {},
                        "facet_dates": {},
                        "facet_ranges": {},
                    },
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "id": 1,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "Test series, 1950 - 1972",
                            "id": 1,
                            "record_uri": "/repositories/2/archival_objects/1",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": True,
                            "children": [
                                {
                                    "title": "Test edited subseries, November, 2014 to November, 2015",
                                    "id": 3,
                                    "record_uri": "/repositories/2/archival_objects/3",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "subseries",
                                    "has_children": True,
                                    "children": [
                                        {
                                            "title": "Test file",
                                            "id": 4,
                                            "record_uri": "/repositories/2/archival_objects/4",
                                            "publish": False,
                                            "suppressed": False,
                                            "node_type": "archival_object",
                                            "level": "file",
                                            "has_children": False,
                                            "children": [],
                                            "instance_types": [],
                                            "containers": [],
                                        }
                                    ],
                                    "instance_types": [],
                                    "containers": [],
                                },
                                {
                                    "title": "New new new child",
                                    "id": 10,
                                    "record_uri": "/repositories/2/archival_objects/10",
                                    "publish": False,
                                    "suppressed": False,
                                    "node_type": "archival_object",
                                    "level": "series",
                                    "has_children": False,
                                    "children": [],
                                    "instance_types": [],
                                    "containers": [],
                                },
                            ],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test series 2",
                            "id": 2,
                            "record_uri": "/repositories/2/archival_objects/2",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child",
                            "id": 13,
                            "record_uri": "/repositories/2/archival_objects/13",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 2",
                            "id": 14,
                            "record_uri": "/repositories/2/archival_objects/14",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "item",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Test new child 3",
                            "id": 16,
                            "record_uri": "/repositories/2/archival_objects/16",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child with note",
                            "id": 17,
                            "record_uri": "/repositories/2/archival_objects/17",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "class",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "New child final",
                            "id": 18,
                            "record_uri": "/repositories/2/archival_objects/18",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": None,
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 19,
                            "record_uri": "/repositories/2/archival_objects/19",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with no note",
                            "id": 20,
                            "record_uri": "/repositories/2/archival_objects/20",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "fonds",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/1",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Some other fonds",
                    "id": 2,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [
                        {
                            "title": "New resource child",
                            "id": 12,
                            "record_uri": "/repositories/2/archival_objects/12",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with singlepart note",
                            "id": 21,
                            "record_uri": "/repositories/2/archival_objects/21",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "series",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                        {
                            "title": "Child with contentless note",
                            "id": 22,
                            "record_uri": "/repositories/2/archival_objects/22",
                            "publish": False,
                            "suppressed": False,
                            "node_type": "archival_object",
                            "level": "Other",
                            "has_children": False,
                            "children": [],
                            "instance_types": [],
                            "containers": [],
                        },
                    ],
                    "record_uri": "/repositories/2/resources/2",
                    "level": "fonds",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Resource with a multipart contentless note",
                    "id": 4,
                    "node_type": "resource",
                    "publish": False,
                    "suppressed": False,
                    "children": [],
                    "record_uri": "/repositories/2/resources/4",
                    "level": "collection",
                    "jsonmodel_type": "resource_tree",
                    "instance_types": [],
                    "containers": [],
                }
            },
        ),
    ],
)
def test_contentless_notes(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert collections[-1]["notes"][0]["type"] == "bioghist"
    assert collections[-1]["notes"][0]["content"] == ""


def test_escaping_solr_queries():
    def escape(s, **kwargs):
        return ArchivesSpaceClient._escape_solr_query(s, **kwargs)

    query = '"quotes"'
    # Test escaping single characters
    assert escape(query, field="identifier") == r"\"quotes\""
    assert escape(query, field="title") == r'\\"quotes\\"'
    # And double characters, which require only one set of escape tokens
    assert escape("&&test", field="identifier") == r"\&&test"
    assert escape("test") == "test"


def test_process_notes(monkeypatch):
    empty_note = {"type": "odd"}
    TestCase = collections.namedtuple("TestCase", "new_record ret notes")
    tests = (
        # No notes submitted.
        # Behaviour: return False, do nothing.
        TestCase(new_record={}, ret=False, notes=None),
        # Empty list.
        # Behaviour: return False, do nothing.
        TestCase(new_record={"notes": []}, ret=False, notes=None),
        # Single empty note.
        # Behaviour: return True, delete notes (empty list).
        TestCase(new_record={"notes": [empty_note]}, ret=True, notes=[]),
        # Multiple notes, all are empty.
        # Behaviour: return True, delete notes (empty list).
        TestCase(new_record={"notes": [empty_note, empty_note]}, ret=True, notes=[]),
        # Multiple notes, first is empty.
        # Behaviour: return True, replace with only non-empty nodes.
        TestCase(
            new_record={"notes": [empty_note, {"type": "odd", "content": "foobar"}]},
            ret=True,
            notes=[
                {
                    "jsonmodel_type": "note_multipart",
                    "publish": True,
                    "subnotes": [
                        {
                            "content": "foobar",
                            "jsonmodel_type": "note_text",
                            "publish": True,
                        }
                    ],
                    "type": "odd",
                }
            ],
        ),
        # Multiple notes with content.
        # Behaviour: return True, replace with all notes.
        TestCase(
            new_record={
                "notes": [
                    {"type": "odd", "content": "foobar 1"},
                    {"type": "odd", "content": "foobar 2"},
                ]
            },
            ret=True,
            notes=[
                {
                    "jsonmodel_type": "note_multipart",
                    "publish": True,
                    "subnotes": [
                        {
                            "content": "foobar 1",
                            "jsonmodel_type": "note_text",
                            "publish": True,
                        }
                    ],
                    "type": "odd",
                },
                {
                    "jsonmodel_type": "note_multipart",
                    "publish": True,
                    "subnotes": [
                        {
                            "content": "foobar 2",
                            "jsonmodel_type": "note_text",
                            "publish": True,
                        }
                    ],
                    "type": "odd",
                },
            ],
        ),
    )
    for tcase in tests:
        record = {}
        ret = ArchivesSpaceClient._process_notes(record, tcase.new_record)
        assert ret == tcase.ret
        if ret:  # Avoid KeyError when we already know it's undefined.
            assert record["notes"] == tcase.notes
