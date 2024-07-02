import os
from unittest import mock

import pytest

from agentarchives.atom.client import AtomClient
from agentarchives.atom.client import CommunicationError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH = {"url": "http://127.0.0.1/index.php", "key": "68405800c6612599"}


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": [
                    {"name": "Collection"},
                    {"name": "File"},
                    {"name": "Fonds"},
                    {"name": "Item"},
                    {"name": "Part"},
                    {"name": "Series"},
                    {"name": "Subfonds"},
                    {"name": "Subseries"},
                ]
            },
        )
    ],
)
def test_levels_of_description(get):
    client = AtomClient(**AUTH)
    levels = client.get_levels_of_description()
    assert levels == [
        "Collection",
        "File",
        "Fonds",
        "Item",
        "Part",
        "Series",
        "Subfonds",
        "Subseries",
    ]


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
    ],
)
def test_listing_collections(get):
    client = AtomClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["title"] == "Top Fonds"
    assert collections[0]["type"] == "resource"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        )
    ],
)
def test_collection_list(get):
    client = AtomClient(**AUTH)
    collection_ids = client.collection_list("test-fonds")
    assert len(collection_ids) == 2
    assert collection_ids[0] == "test-subfonds"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "dates": [
                        {
                            "start_date": "2014-01-01",
                            "end_date": "2015-01-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
    ],
)
def test_rendering_record_containing_a_note(get):
    client = AtomClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["notes"][0]["content"] == "Note content"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F2",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "F2",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "dates": [
                        {
                            "start_date": "2014-01-01",
                            "end_date": "2015-01-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "F2",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "F2",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
    ],
)
def test_find_collections_search(get):
    client = AtomClient(**AUTH)
    collections = client.find_collections(search_pattern="Test fonds")
    assert len(collections) == 1
    assert collections[0]["title"] == "Test fonds"
    assert collections[0]["type"] == "resource"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(status_code=200, **{"json.return_value": {"total": 0, "results": []}})
    ],
)
def test_find_collections_search_no_results(get):
    client = AtomClient(**AUTH)
    no_results = client.find_collections(search_pattern="Nonexistent")
    assert len(no_results) == 0


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "2015044 Aa Ac",
                            "slug": "a-fonds-for-testing",
                            "title": "Resource with spaces in the identifier",
                            "level_of_description": "Fonds",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "2015044 Aa Ac",
                    "title": "Resource with spaces in the identifier",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Resource with spaces in the identifier",
                    "identifier": "2015044 Aa Ac",
                    "slug": "a-fonds-for-testing",
                    "level": "Fonds",
                }
            },
        ),
    ],
)
def test_listing_collections_search_spaces(get):
    client = AtomClient(**AUTH)
    collections = client.find_collections(identifier="2015044 Aa Ac")
    assert len(collections) == 1
    assert collections[0]["title"] == "Resource with spaces in the identifier"
    assert collections[0]["levelOfDescription"] == "Fonds"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "dates": [
                        {
                            "start_date": "2014-01-01",
                            "end_date": "2015-01-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "dates": [
                        {
                            "start_date": "2014-01-01",
                            "end_date": "2015-01-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries with empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
    ],
)
def test_listing_collections_sort(get):
    client = AtomClient(**AUTH)
    asc = client.find_collections(sort_by="asc")
    assert len(asc) == 2
    assert asc[0]["title"] == "Test fonds"
    assert asc[0]["type"] == "resource"

    desc = client.find_collections(sort_by="desc")
    assert len(desc) == 2
    assert desc[0]["title"] == "Top Fonds"
    assert desc[0]["type"] == "resource"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "notes": ["Note content"],
                }
            },
        ),
    ],
)
def test_find_component_parent_with_top_level_parent(get):
    client = AtomClient(**AUTH)
    resource_id = client.find_parent_id_for_component("test-subfonds")

    assert resource_id == "test-fonds"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-subfonds",
                    "reference_code": "testfonds-testsubfonds-testitem",
                    "title": "Test item",
                    "publication_status": "Draft",
                    "level_of_description": "Item",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
    ],
)
def test_find_component_parent_with_non_top_level_parent(get):
    client = AtomClient(**AUTH)
    resource_id = client.find_parent_id_for_component("test-item")

    assert resource_id == "test-subfonds"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-subfonds",
                    "reference_code": "testfonds-testsubfonds-testitem",
                    "title": "Test item",
                    "publication_status": "Draft",
                    "level_of_description": "Item",
                }
            },
        ),
    ],
)
def test_find_resource_children(get):
    client = AtomClient(**AUTH)
    data = client.get_resource_component_and_children("test-fonds")

    assert isinstance(data, dict)
    assert len(data["children"]) == 1
    assert data["has_children"] is True
    assert data["title"] == "Test fonds"
    assert data["type"] == "resource"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
    ],
)
def test_find_resource_children_recursion_level(get):
    client = AtomClient(**AUTH)
    data = client.get_resource_component_and_children("test-fonds", recurse_max_level=2)
    assert len(data["children"]) == 1
    assert data["has_children"] is True


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test subfonds",
                    "identifier": "testsubfonds",
                    "slug": "test-subfonds",
                    "level": "Subfonds",
                    "children": [
                        {
                            "title": "Test item",
                            "identifier": "testitem",
                            "slug": "test-item",
                            "level": "Item",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
    ],
)
def test_find_resource_component_children_at_max_recursion_level(get):
    client = AtomClient(**AUTH)
    record = client.get_resource_component_and_children(
        "test-subfonds", recurse_max_level=1
    )
    assert record["children"] == []
    assert record["has_children"] is True


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                    ],
                }
            },
        )
    ],
)
def test_find_collection_ids(get):
    client = AtomClient(**AUTH)
    ids = client.find_collection_ids()
    assert ids == ["top-level-fonds", "test-fonds"]


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F2",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        }
                    ],
                }
            },
        )
    ],
)
def test_find_collection_ids_search(get):
    client = AtomClient(**AUTH)
    ids = client.find_collection_ids(search_pattern="Test fonds")
    assert ids == ["test-fonds"]


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                    ],
                }
            },
        )
    ],
)
def test_count_collection_ids(get):
    client = AtomClient(**AUTH)
    ids = client.count_collections()
    assert ids == 2


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F1",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        }
                    ],
                }
            },
        )
    ],
)
def test_count_collection_ids_search(get):
    client = AtomClient(**AUTH)
    ids = client.count_collections(search_pattern="Top")
    assert ids == 1


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "top-level-fonds",
                    "reference_code": "toplevelfonds-dogchild",
                    "title": "Dawg Child",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "reference_code": "testfonds-testsubfonds",
                    "title": "Test subfonds",
                    "publication_status": "Draft",
                    "level_of_description": "Subfonds",
                }
            },
        ),
    ],
)
def test_augment_ids(get):
    client = AtomClient(**AUTH)
    data = client.augment_resource_ids(["top-level-fonds", "test-fonds"])
    assert len(data) == 2
    assert data[0]["title"] == "Top Fonds"
    assert data[0]["type"] == "resource"
    assert data[1]["title"] == "Test fonds"
    assert data[1]["type"] == "resource"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F1",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F1",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 1,
                    "results": [
                        {
                            "reference_code": "F1",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "F1",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "F1",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "F1",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
    ],
)
def test_identifier_search_exact_match(get):
    client = AtomClient(**AUTH)
    assert client.find_collection_ids(identifier="F1") == ["top-level-fonds"]
    assert client.count_collections(identifier="F1") == 1
    assert len(client.find_collections(identifier="F1")) == 1


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=201,
            **{
                "json.return_value": {
                    "id": 463,
                    "slug": "second-subfonds",
                    "parent_id": 436,
                }
            },
        )
    ],
)
def test_add_child_resource(post):
    client = AtomClient(**AUTH)
    slug = client.add_child("test-fonds", title="Second subfonds", level="subfonds")
    assert slug == "second-subfonds"


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=201,
            **{
                "json.return_value": {"id": 464, "slug": "test-child", "parent_id": 463}
            },
        )
    ],
)
def test_add_child_resource_component(post):
    client = AtomClient(**AUTH)
    slug = client.add_child("second-subfonds", title="Test child", level="item")
    assert slug == "test-child"


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=201,
            **{
                "json.return_value": {
                    "id": 465,
                    "slug": "another-subfonds",
                    "parent_id": 436,
                }
            },
        )
    ],
)
def test_adding_child_with_note(post):
    client = AtomClient(**AUTH)
    slug = client.add_child(
        "test-fonds",
        title="Another subfonds",
        level="subfonds",
        notes=[{"type": "general", "content": "This is a test note"}],
    )
    assert slug == "another-subfonds"


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=201,
            **{
                "json.return_value": {
                    "id": 472,
                    "slug": "yet-another-subfonds",
                    "parent_id": 436,
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
                    "parent": "test-fonds",
                    "title": "Yet another subfonds",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                }
            },
        )
    ],
)
def test_posting_contentless_note(get, post):
    client = AtomClient(**AUTH)
    slug = client.add_child(
        "test-fonds",
        title="Yet another subfonds",
        level="subfonds",
        notes=[{"type": "general", "content": ""}],
    )
    assert client.get_record(slug)["notes"] == []


@mock.patch(
    "requests.Session.delete",
    side_effect=[mock.Mock(status_code=204)],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Another subfonds",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "notes": ["This is a test note"],
                }
            },
        ),
        mock.Mock(status_code=404),
    ],
)
def test_delete_record_resource(get, delete):
    client = AtomClient(**AUTH)
    slug = "another-subfonds"
    assert client.get_record(slug)
    r = client.delete_record(slug)
    assert r["status"] == "Deleted"
    with pytest.raises(CommunicationError):
        client.get_record(slug)


@mock.patch(
    "requests.Session.put",
    side_effect=[
        mock.Mock(
            status_code=200, **{"json.return_value": {"id": 463, "parent_id": 436}}
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
                    "parent": "test-fonds",
                    "title": "Second subfonds",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [{"end_date": "2015-01-01", "type": "Creation"}],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Second subfonds",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [{"end_date": "2015-01-01", "type": "Creation"}],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Test edited subfonds",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "start_date": "2014-11-01",
                            "end_date": "2015-11-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["This is a test note"],
                }
            },
        ),
    ],
)
def test_edit_archival_object(get, put):
    client = AtomClient(**AUTH)
    original = client.get_record("second-subfonds")
    assert original["title"] == "Second subfonds"
    assert original["dates"][0]["end"] == "2015-01-01"
    assert not original["notes"]
    new_record = {
        "slug": "second-subfonds",
        "title": "Test edited subfonds",
        "start_date": "2014-11-01",
        "end_date": "2015-11-01",
        "date_expression": "November, 2014 to November, 2015",
        "notes": [{"type": "general", "content": "This is a test note"}],
    }
    client.edit_record(new_record)
    updated = client.get_record("second-subfonds")
    assert updated["title"] == new_record["title"]
    assert updated["dates"][0]["begin"] == new_record["start_date"]
    assert updated["dates"][0]["end"] == new_record["end_date"]
    assert updated["dates"][0]["expression"] == new_record["date_expression"]
    assert updated["notes"][0]["type"] == new_record["notes"][0]["type"]
    assert updated["notes"][0]["content"] == new_record["notes"][0]["content"]


@mock.patch(
    "requests.Session.put",
    side_effect=[
        mock.Mock(
            status_code=200, **{"json.return_value": {"id": 463, "parent_id": 436}}
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
                    "parent": "test-fonds",
                    "title": "Test edited subseries w/ empty note",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "start_date": "2014-11-01",
                            "end_date": "2015-11-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Gen note"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Test edited subseries w/ empty note",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "start_date": "2014-11-01",
                            "end_date": "2015-11-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Gen note"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Test edited subseries w/ empty note",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "start_date": "2014-11-01",
                            "end_date": "2015-11-01",
                            "type": "Creation",
                        }
                    ],
                }
            },
        ),
    ],
)
def test_edit_record_empty_note(get, put):
    client = AtomClient(**AUTH)
    original = client.get_record("second-subfonds")
    assert original["notes"]
    new_record = {
        "slug": "second-subfonds",
        "title": "Test edited subseries w/ empty note",
        "start_date": "2014-11-01",
        "end_date": "2015-11-01",
        "date_expression": "November, 2014 to November, 2015",
        "notes": [{"type": "general", "content": ""}],
    }
    client.edit_record(new_record)
    updated = client.get_record("second-subfonds")
    assert not updated["notes"]


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(
            status_code=201, **{"json.return_value": {"id": 478, "slug": "kitty-jpg"}}
        )
    ],
)
def test_add_digital_object(post):
    client = AtomClient(**AUTH)
    do = client.add_digital_object(
        "test-child",
        title="kitty.jpg",
        uri="http://www.artefactual.com/wp-content/uploads/2016/04/cat.jpg",
    )
    assert do["slug"] == "kitty-jpg"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test edited subseries w/ empty note",
                    "identifier": None,
                    "slug": "second-subfonds",
                    "level": "Subfonds",
                    "children": [
                        {
                            "title": "Test child",
                            "identifier": None,
                            "slug": "test-child",
                            "level": "Item",
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "test-fonds",
                    "title": "Test edited subseries w/ empty note",
                    "publication_status": "Published",
                    "level_of_description": "Subfonds",
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "start_date": "2014-11-01",
                            "end_date": "2015-11-01",
                            "type": "Creation",
                        }
                    ],
                }
            },
        ),
    ],
)
def test_date_expression(get):
    client = AtomClient(**AUTH)
    record = client.get_resource_component_and_children(
        "second-subfonds", recurse_max_level=1
    )
    assert record["date_expression"] == "November, 2014 to November, 2015"


@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test child",
                    "identifier": None,
                    "slug": "test-child",
                    "level": "Item",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "second-subfonds",
                    "title": "Test child",
                    "publication_status": "Published",
                    "level_of_description": "Item",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test child",
                    "identifier": None,
                    "slug": "test-child",
                    "level": "Item",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "parent": "second-subfonds",
                    "title": "Test child",
                    "publication_status": "Published",
                    "level_of_description": "Item",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
                            "level_of_description": "Fonds",
                        },
                        {
                            "reference_code": "toplevelfonds",
                            "slug": "top-level-fonds",
                            "title": "Top Fonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "testfonds",
                    "title": "Test fonds",
                    "publication_status": "Draft",
                    "level_of_description": "Fonds",
                    "dates": [
                        {
                            "start_date": "2014-01-01",
                            "end_date": "2015-01-01",
                            "type": "Creation",
                        }
                    ],
                    "notes": ["Note content"],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries w/ empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Test fonds",
                    "identifier": "testfonds",
                    "slug": "test-fonds",
                    "level": "Fonds",
                    "children": [
                        {
                            "title": "Test subfonds",
                            "identifier": "testsubfonds",
                            "slug": "test-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test item",
                                    "identifier": "testitem",
                                    "slug": "test-item",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Test edited subseries w/ empty note",
                            "identifier": None,
                            "slug": "second-subfonds",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Test child",
                                    "identifier": None,
                                    "slug": "test-child",
                                    "level": "Item",
                                }
                            ],
                        },
                        {
                            "title": "Yet another subfonds",
                            "identifier": None,
                            "slug": "yet-another-subfonds",
                            "level": "Subfonds",
                        },
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "reference_code": "toplevelfonds",
                    "title": "Top Fonds",
                    "publication_status": "Published",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "title": "Top Fonds",
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "children": [
                        {
                            "title": "Dawg Child",
                            "identifier": "dogchild",
                            "slug": "child-of-top-level",
                            "level": "Subfonds",
                            "children": [
                                {
                                    "title": "Dawg Item",
                                    "identifier": "dogitem",
                                    "slug": "item-level",
                                    "level": "Item",
                                }
                            ],
                        }
                    ],
                }
            },
        ),
    ],
)
def test_empty_dates(get):
    client = AtomClient(**AUTH)
    record = client.get_resource_component_children("test-child")
    assert record["dates"] == ""
    assert record["date_expression"] == ""
    record = client.get_resource_component_and_children(
        "test-child", recurse_max_level=1
    )
    # dates are mandatory for resources, so this record does have a date but no expression
    assert record["date_expression"] == ""
    collections = client.find_collections()
    assert collections[0]["date_expression"] == ""


def test_escaping_lucene_queries():
    def escape(s, **kwargs):
        return AtomClient._escape_lucene_query(s, **kwargs)

    query = '"quotes"'
    # Test escaping single characters
    assert escape(query, field="identifier") == r"\"quotes\""
    assert escape(query, field="title") == r"\"quotes\""
    # And double characters, which require only one set of escape tokens
    assert escape("&&test", field="identifier") == r"\&&test"
    assert escape("test") == "test"
