import collections
import json
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


SESSION_MOCK = mock.Mock(status_code=200, **{"json.return_value": {"session": "1"}})


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Test fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Some other fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
    ],
)
def test_listing_collections(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["title"] == "Test fonds"
    assert collections[0]["type"] == "resource"


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Some other fonds",
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [
                                        {
                                            "content": ["Singlepart note"],
                                            "jsonmodel_type": "note_singlepart",
                                            "type": "physdesc",
                                        }
                                    ],
                                    "title": "Test fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
    ],
)
def test_rendering_record_containing_a_singlepart_note(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[1]["notes"][0]["content"] == "Singlepart note"


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Test fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [],
                    "node_type": "resource",
                    "title": "Test fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"results": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "collection",
                                    "notes": [],
                                    "title": "Resource with spaces in the identifier",
                                    "uri": "/repositories/2/resources/6",
                                }
                            ),
                        }
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
    ],
)
def test_listing_collections_search_spaces(get, post):
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections(identifier="2015044 Aa Ac")
    assert len(collections) == 1
    assert collections[0]["title"] == "Resource with spaces in the identifier"
    assert collections[0]["levelOfDescription"] == "collection"


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Some other fonds",
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Test fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Test fonds",
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "title": "Some other fonds",
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "resource": {"ref": "/repositories/2/resources/1"}
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": {"ref": "/repositories/2/archival_objects/1"}
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "resource": {"ref": "/repositories/2/resources/1"}
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/1",
                        },
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/2",
                        },
                    ],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "level": "fonds",
                    "notes": [],
                    "title": "Test fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [{"children": []}, {"children": []}],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/1",
                        },
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/2",
                        },
                    ],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [
                        {
                            "children": [
                                {
                                    "children": [],
                                    "level": "subseries",
                                    "record_uri": "/repositories/2/archival_objects/3",
                                },
                            ],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/1",
                        },
                    ],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
    ],
)
def test_find_resource_children_at_max_recursion_level(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children(
        "/repositories/2/resources/1", recurse_max_level=1
    )
    assert record["children"] == []
    assert record["has_children"] is True


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "level": "series",
                    "notes": [],
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "uri": "/repositories/2/archival_objects/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {
                        "level": "subseries",
                        "notes": [],
                        "resource": {"ref": "/repositories/2/resources/1"},
                        "uri": "/repositories/2/archival_objects/3",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "results": [
                        {"uri": "/repositories/2/resources/1"},
                        {"uri": "/repositories/2/resources/2"},
                    ],
                    "this_page": 1,
                    "total_hits": 2,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 11,
                    "offset_last": 2,
                    "results": [],
                    "this_page": 2,
                    "total_hits": 2,
                }
            },
        ),
    ],
)
def test_find_collection_ids(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids()
    assert ids == ["/repositories/2/resources/1", "/repositories/2/resources/2"]


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "results": [{"uri": "/repositories/2/resources/2"}],
                    "this_page": 1,
                    "total_hits": 1,
                }
            },
        )
    ],
)
def test_find_collection_ids_search(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids(search_pattern="Some")
    assert ids == ["/repositories/2/resources/2"]


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "results": [
                        {"uri": "/repositories/2/resources/1"},
                        {"uri": "/repositories/2/resources/2"},
                    ],
                    "this_page": 1,
                    "total_hits": 2,
                }
            },
        )
    ],
)
def test_count_collection_ids(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections()
    assert ids == 2


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "results": [{"uri": "/repositories/2/resources/2"}],
                    "this_page": 1,
                    "total_hits": 1,
                }
            },
        )
    ],
)
def test_count_collection_ids_search(get, post):
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections(search_pattern="Some")
    assert ids == 1


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
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
                                "level": "file",
                                "notes": [],
                                "ref_id": "a118514fab1b2ee6a7e9ad259e1de355",
                                "title": "Test AO",
                                "uri": "/repositories/2/archival_objects/752250",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/1",
                            "title": "Test series",
                        },
                        {
                            "children": [],
                            "level": "series",
                            "record_uri": "/repositories/2/archival_objects/2",
                            "title": "Test series 2",
                        },
                    ],
                    "level": "fonds",
                    "title": "Test fonds",
                    "record_uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [],
                    "title": "Test fonds",
                    "uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [],
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "title": "Test series",
                    "uri": "/repositories/2/archival_objects/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [],
                    "resource": {"ref": "/repositories/2/resources/1"},
                    "title": "Test series 2",
                    "uri": "/repositories/2/archival_objects/2",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/2",
                    "title": "Some other fonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [],
                    "repository": {"ref": "/repositories/2"},
                    "title": "Some other fonds",
                    "uri": "/repositories/2/resources/2",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
def test_get_resource_type(post):
    client = ArchivesSpaceClient(**AUTH)
    assert client.resource_type("/repositories/2/resources/2") == "resource"
    assert (
        client.resource_type("/repositories/2/archival_objects/3")
        == "resource_component"
    )


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
def test_get_resource_type_raises_on_invalid_input(post):
    client = ArchivesSpaceClient(**AUTH)
    with pytest.raises(ArchivesSpaceError):
        client.resource_type("invalid")


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "results": [{"uri": "/repositories/2/resources/1"}],
                    "this_page": 1,
                    "total_hits": 1,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 1,
                    "results": [{"uri": "/repositories/2/resources/1"}],
                    "this_page": 1,
                    "total_hits": 1,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                        }
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
    ],
)
def test_identifier_search_exact_match(get, post):
    client = ArchivesSpaceClient(**AUTH)
    assert client.find_collection_ids(identifier="F1") == [
        "/repositories/2/resources/1"
    ]
    assert client.count_collections(identifier="F1") == 1
    assert len(client.find_collections(identifier="F1")) == 1


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "offset_first": 1,
                    "offset_last": 0,
                    "results": [],
                    "this_page": 1,
                    "total_hits": 0,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "offset_first": 1,
                    "offset_last": 0,
                    "results": [],
                    "this_page": 1,
                    "total_hits": 0,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 0,
                    "offset_first": 1,
                    "offset_last": 0,
                    "results": [],
                    "this_page": 1,
                    "total_hits": 0,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "results": [
                        {"uri": "/repositories/2/resources/1"},
                        {"uri": "/repositories/2/resources/2"},
                    ],
                    "this_page": 1,
                    "total_hits": 2,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 11,
                    "offset_last": 3,
                    "results": [],
                    "this_page": 2,
                    "total_hits": 3,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "results": [
                        {"uri": "/repositories/2/resources/1"},
                        {"uri": "/repositories/2/resources/2"},
                    ],
                    "this_page": 1,
                    "total_hits": 2,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "first_page": 1,
                    "last_page": 1,
                    "offset_first": 1,
                    "offset_last": 2,
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                            "uri": "/repositories/2/resources/1",
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                            "uri": "/repositories/2/resources/2",
                        },
                    ],
                    "this_page": 1,
                    "total_hits": 2,
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/3"}},
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
                    "level": "collection",
                    "notes": [],
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/resources/2",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/5"}},
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
                    "repository": {"ref": "/repositories/2"},
                    "resource": {"ref": "/repositories/2/resources/2"},
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/24"}},
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
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/resources/5",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/29"}},
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
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/35"}},
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
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/resources/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [
                        {
                            "subnotes": [{"content": "General"}],
                            "type": "odd",
                        },
                        {
                            "subnotes": [{"content": "Access"}],
                            "type": "accessrestrict",
                        },
                    ],
                    "uri": "/repositories/2/archival_objects/35",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/resources/3"}},
        ),
        mock.Mock(
            status_code=404, **{"json.return_value": {"error": "Resource not found"}}
        ),
    ],
)
@mock.patch(
    "requests.Session.delete",
    side_effect=[
        mock.Mock(status_code=200, **{"json.return_value": {"status": "Deleted"}})
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/4"}},
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
        mock.Mock(status_code=200, **{"json.return_value": {"status": "Deleted"}})
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/3"}},
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
                    "dates": [
                        {
                            "begin": "2014-01-01",
                            "end": "2015-01-01",
                        }
                    ],
                    "notes": [],
                    "title": "Test subseries",
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "begin": "2014-01-01",
                            "end": "2015-01-01",
                        }
                    ],
                    "notes": [],
                    "title": "Test subseries",
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "expression": "November, 2014 to November, 2015",
                        }
                    ],
                    "notes": [
                        {
                            "subnotes": [{"content": "This is a test note"}],
                            "type": "odd",
                        }
                    ],
                    "title": "Test edited subseries",
                    "uri": "/repositories/2/archival_objects/3",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/3"}},
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
                    "notes": [
                        {
                            "subnotes": [{"content": "This is a test note"}],
                            "type": "odd",
                        }
                    ],
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "expression": "November, 2014 to November, 2015",
                        }
                    ],
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/9253"}},
        )
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [
                        {
                            "subnotes": [{"content": "General note content"}],
                            "type": "odd",
                        },
                        {
                            "subnotes": [{"content": "Access restriction note"}],
                            "type": "accessrestrict",
                        },
                    ],
                    "uri": "/repositories/2/archival_objects/9253",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/digital_objects/8"}},
        ),
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/3"}},
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
                    "instances": [],
                    "linked_agents": [],
                    "notes": [],
                    "repository": {"ref": "/repositories/2"},
                    "subjects": [],
                    "uri": "/repositories/2/archival_objects/3",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/digital_objects/7"}},
        ),
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/3"}},
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
                    "instances": [],
                    "linked_agents": [],
                    "notes": [],
                    "repository": {"ref": "/repositories/2"},
                    "subjects": [],
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "notes": [
                        {"content": ["The ether"], "type": "originalsloc"},
                        {"content": ["This is a test note"], "type": "note"},
                    ],
                    "repository": {"ref": "/repositories/2"},
                    "subjects": [],
                    "uri": "/repositories/2/digital_objects/7",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/digital_objects/9"}},
        ),
        mock.Mock(
            status_code=200,
            **{"json.return_value": {"uri": "/repositories/2/archival_objects/21"}},
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
                    "instances": [],
                    "linked_agents": [],
                    "notes": [],
                    "repository": {"ref": "/repositories/2"},
                    "subjects": [],
                    "uri": "/repositories/2/archival_objects/21",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "linked_agents": [],
                    "notes": [{"content": ["This is an abstract"], "type": "note"}],
                    "repository": {"ref": "/repositories/2"},
                    "subjects": [],
                    "uri": "/repositories/2/digital_objects/9",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "uri": "/repositories/2/digital_object_components/3"
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
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/digital_objects/1",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "uri": "/repositories/2/digital_object_components/5"
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
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/digital_objects/1",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": {"ref": "/repositories/2/digital_object_components/3"},
                    "repository": {"ref": "/repositories/2"},
                    "uri": "/repositories/2/digital_object_components/5",
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "begin": "2014-11-01",
                            "end": "2015-11-01",
                            "expression": "November, 2014 to November, 2015",
                        }
                    ],
                    "level": "subseries",
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/3",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": [{}]}),
    ],
)
def test_date_expression(get, post):
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children(
        "/repositories/2/archival_objects/3", recurse_max_level=1
    )
    assert record["date_expression"] == "November, 2014 to November, 2015"


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "level": "series",
                    "notes": [],
                    "uri": "/repositories/2/archival_objects/2",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {
                        "level": "series",
                        "notes": [],
                        "uri": "/repositories/2/archival_objects/7",
                    }
                ]
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": []}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "children": [],
                    "level": "fonds",
                    "record_uri": "/repositories/2/resources/2",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"notes": []}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "repository": {"ref": "/repositories/2"},
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                            "uri": "/repositories/2/resources/1",
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "repository": {"ref": "/repositories/2"},
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                            "uri": "/repositories/2/resources/2",
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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


@mock.patch("requests.post", side_effect=[SESSION_MOCK])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "uri": "/repositories/2/resources/1",
                                }
                            ),
                            "uri": "/repositories/2/resources/1",
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "fonds",
                                    "notes": [],
                                    "uri": "/repositories/2/resources/2",
                                }
                            ),
                            "uri": "/repositories/2/resources/2",
                        },
                        {
                            "json": json.dumps(
                                {
                                    "level": "collection",
                                    "notes": [
                                        {
                                            "type": "bioghist",
                                            "subnotes": [
                                                {"items": ["Second"], "title": "First"}
                                            ],
                                        }
                                    ],
                                    "uri": "/repositories/2/resources/4",
                                }
                            ),
                            "uri": "/repositories/2/resources/4",
                        },
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
