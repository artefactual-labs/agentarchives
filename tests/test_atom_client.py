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
                    "results": [
                        {"slug": "top-level-fonds", "title": "Top Fonds"},
                        {"slug": "test-fonds", "title": "Test fonds"},
                    ],
                    "total": 2,
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
                    "children": [
                        {
                            "slug": "test-subfonds",
                            "children": [{"slug": "test-item"}],
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
                    "results": [{"slug": "test-fonds"}, {"slug": "top-level-fonds"}],
                    "total": 2,
                }
            },
        ),
        mock.Mock(
            status_code=200, **{"json.return_value": {"notes": ["Note content"]}}
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
                    "results": [{"slug": "test-fonds", "title": "Test fonds"}],
                    "total": 1,
                }
            },
        ),
        mock.Mock(
            status_code=200, **{"json.return_value": {"notes": ["Note content"]}}
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
                    "results": [
                        {
                            "level_of_description": "Fonds",
                            "slug": "a-fonds-for-testing",
                            "title": "Resource with spaces in the identifier",
                        }
                    ],
                    "total": 1,
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
                        {"slug": "test-fonds", "title": "Test fonds"},
                        {"slug": "top-level-fonds", "title": "Top Fonds"},
                    ],
                }
            },
        ),
        mock.Mock(
            status_code=200, **{"json.return_value": {"notes": ["Note content"]}}
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {"slug": "top-level-fonds", "title": "Top Fonds"},
                        {"slug": "test-fonds", "title": "Test fonds"},
                    ],
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(
            status_code=200, **{"json.return_value": {"notes": ["Note content"]}}
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
        mock.Mock(status_code=200, **{"json.return_value": {"parent": "test-fonds"}}),
        mock.Mock(
            status_code=200, **{"json.return_value": {"notes": ["Note content"]}}
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
            status_code=200, **{"json.return_value": {"parent": "test-subfonds"}}
        ),
        mock.Mock(status_code=200, **{"json.return_value": {"parent": "test-fonds"}}),
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
                    "children": [
                        {
                            "identifier": "testsubfonds",
                            "level": "Subfonds",
                            "slug": "test-subfonds",
                            "title": "Test subfonds",
                        }
                    ],
                    "identifier": "testfonds",
                    "level": "Fonds",
                    "slug": "test-fonds",
                    "title": "Test fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
                    "children": [
                        {
                            "identifier": "testsubfonds",
                            "level": "Subfonds",
                            "slug": "test-subfonds",
                            "title": "Test subfonds",
                        }
                    ],
                    "identifier": "testfonds",
                    "level": "Fonds",
                    "slug": "test-fonds",
                    "title": "Test fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
                    "children": [],
                    "identifier": "testsubfonds",
                    "level": "Subfonds",
                    "slug": "test-subfonds",
                    "title": "Test subfonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
                        {"slug": "top-level-fonds", "title": "Top Fonds"},
                        {"slug": "test-fonds", "title": "Test fonds"},
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
                    "results": [{"slug": "test-fonds", "title": "Test fonds"}],
                    "total": 1,
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
                    "results": [
                        {"slug": "top-level-fonds", "title": "Top Fonds"},
                        {"slug": "test-fonds", "title": "Test fonds"},
                    ],
                    "total": 2,
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
                    "results": [{"slug": "top-level-fonds", "title": "Top Fonds"}],
                    "total": 1,
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
                    "children": [
                        {
                            "identifier": "dogchild",
                            "level": "Subfonds",
                            "slug": "child-of-top-level",
                            "title": "Dawg Child",
                        }
                    ],
                    "identifier": "toplevelfonds",
                    "slug": "top-level-fonds",
                    "title": "Top Fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "identifier": "testfonds",
                    "level": "Fonds",
                    "slug": "test-fonds",
                    "title": "Test fonds",
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
                    "results": [{"slug": "top-level-fonds", "title": "Top Fonds"}],
                    "total": 1,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [{"slug": "top-level-fonds", "title": "Top Fonds"}],
                    "total": 1,
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "results": [{"slug": "top-level-fonds", "title": "Top Fonds"}],
                    "total": 1,
                }
            },
        ),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "identifier": "F1",
                    "slug": "top-level-fonds",
                    "title": "Top Fonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "identifier": "F1",
                    "slug": "top-level-fonds",
                    "title": "Top Fonds",
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
        mock.Mock(status_code=201, **{"json.return_value": {"slug": "second-subfonds"}})
    ],
)
def test_add_child_resource(post):
    client = AtomClient(**AUTH)
    slug = client.add_child("test-fonds", title="Second subfonds", level="subfonds")
    assert slug == "second-subfonds"


@mock.patch(
    "requests.Session.post",
    side_effect=[
        mock.Mock(status_code=201, **{"json.return_value": {"slug": "test-child"}})
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
            status_code=201, **{"json.return_value": {"slug": "another-subfonds"}}
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
            status_code=201, **{"json.return_value": {"slug": "yet-another-subfonds"}}
        ),
    ],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[mock.Mock(status_code=200, **{"json.return_value": {}})],
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


@mock.patch("requests.Session.delete", side_effect=[mock.Mock(status_code=204)])
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(status_code=200, **{"json.return_value": {}}),
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
    side_effect=[mock.Mock(status_code=200, **{"json.return_value": {}})],
)
@mock.patch(
    "requests.Session.get",
    side_effect=[
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [{"end_date": "2015-01-01", "type": "Creation"}],
                    "level_of_description": "Subfonds",
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Second subfonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [{"end_date": "2015-01-01", "type": "Creation"}],
                    "level_of_description": "Subfonds",
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Second subfonds",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "end_date": "2015-11-01",
                            "start_date": "2014-11-01",
                            "type": "Creation",
                        }
                    ],
                    "level_of_description": "Subfonds",
                    "notes": ["This is a test note"],
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Test edited subfonds",
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
    side_effect=[mock.Mock(status_code=200, **{"json.return_value": {}})],
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
                            "date": "November, 2014 to November, 2015",
                            "end_date": "2015-11-01",
                            "start_date": "2014-11-01",
                            "type": "Creation",
                        }
                    ],
                    "level_of_description": "Subfonds",
                    "notes": ["Gen note"],
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Test edited subseries with empty note",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "end_date": "2015-11-01",
                            "start_date": "2014-11-01",
                            "type": "Creation",
                        }
                    ],
                    "level_of_description": "Subfonds",
                    "notes": ["Gen note"],
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Test edited subseries with empty note",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "end_date": "2015-11-01",
                            "start_date": "2014-11-01",
                            "type": "Creation",
                        }
                    ],
                    "level_of_description": "Subfonds",
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Test edited subseries with empty note",
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
        "title": "Test edited subseries with empty note",
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
        mock.Mock(status_code=201, **{"json.return_value": {"slug": "kitty-jpg"}})
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
                    "identifier": None,
                    "level": "Subfonds",
                    "slug": "second-subfonds",
                    "title": "Test edited subseries with empty note",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "dates": [
                        {
                            "date": "November, 2014 to November, 2015",
                            "end_date": "2015-11-01",
                            "start_date": "2014-11-01",
                            "type": "Creation",
                        }
                    ],
                    "level_of_description": "Subfonds",
                    "parent": "test-fonds",
                    "publication_status": "Published",
                    "title": "Test edited subseries with empty note",
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
                    "identifier": None,
                    "level": "Item",
                    "slug": "test-child",
                    "title": "Test child",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "level_of_description": "Item",
                    "parent": "second-subfonds",
                    "publication_status": "Published",
                    "title": "Test child",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "identifier": None,
                    "level": "Item",
                    "slug": "test-child",
                    "title": "Test child",
                }
            },
        ),
        mock.Mock(
            status_code=200,
            **{"json.return_value": {}},
        ),
        mock.Mock(
            status_code=200,
            **{
                "json.return_value": {
                    "total": 2,
                    "results": [
                        {
                            "level_of_description": "Fonds",
                            "reference_code": "testfonds",
                            "slug": "test-fonds",
                            "title": "Test fonds",
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
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {}}),
        mock.Mock(status_code=200, **{"json.return_value": {"children": []}}),
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
