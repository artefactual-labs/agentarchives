import os

import pytest
import vcr

from agentarchives.atom.client import AtomClient
from agentarchives.atom.client import CommunicationError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH = {"url": "http://127.0.0.1/index.php", "key": "68405800c6612599"}


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_levels_of_description.yaml")
)
def test_levels_of_description():
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


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_listing_collections.yaml")
)
def test_listing_collections():
    client = AtomClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["title"] == "Top Fonds"
    assert collections[0]["type"] == "resource"


@vcr.use_cassette(os.path.join(THIS_DIR, "fixtures/atom", "test_collection_list.yaml"))
def test_collection_list():
    client = AtomClient(**AUTH)
    collection_ids = client.collection_list("test-fonds")
    assert len(collection_ids) == 2
    assert collection_ids[0] == "test-subfonds"


@vcr.use_cassette(os.path.join(THIS_DIR, "fixtures/atom", "test_note.yaml"))
def test_rendering_record_containing_a_note():
    client = AtomClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]["notes"][0]["content"] == "Note content"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_find_collections_search.yaml")
)
def test_find_collections_search():
    client = AtomClient(**AUTH)
    collections = client.find_collections(search_pattern="Test fonds")
    assert len(collections) == 1
    assert collections[0]["title"] == "Test fonds"
    assert collections[0]["type"] == "resource"


@vcr.use_cassette(
    os.path.join(
        THIS_DIR, "fixtures/atom", "test_find_collections_search_no_results.yaml"
    )
)
def test_find_collections_search_no_results():
    client = AtomClient(**AUTH)
    no_results = client.find_collections(search_pattern="Nonexistent")
    assert len(no_results) == 0


@vcr.use_cassette(
    os.path.join(
        THIS_DIR, "fixtures/atom", "test_listing_collections_search_spaces.yaml"
    )
)
def test_listing_collections_search_spaces():
    client = AtomClient(**AUTH)
    collections = client.find_collections(identifier="2015044 Aa Ac")
    assert len(collections) == 1
    assert collections[0]["title"] == "Resource with spaces in the identifier"
    assert collections[0]["levelOfDescription"] == "Fonds"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_listing_collections_sort.yaml")
)
def test_listing_collections_sort():
    client = AtomClient(**AUTH)
    asc = client.find_collections(sort_by="asc")
    assert len(asc) == 2
    assert asc[0]["title"] == "Test fonds"
    assert asc[0]["type"] == "resource"

    desc = client.find_collections(sort_by="desc")
    assert len(desc) == 2
    assert desc[0]["title"] == "Top Fonds"
    assert desc[0]["type"] == "resource"


@vcr.use_cassette(
    os.path.join(
        THIS_DIR,
        "fixtures/atom",
        "test_find_component_parent_with_top_level_parent.yaml",
    )
)
def test_find_component_parent_with_top_level_parent():
    client = AtomClient(**AUTH)
    resource_id = client.find_parent_id_for_component("test-subfonds")

    assert resource_id == "test-fonds"


@vcr.use_cassette(
    os.path.join(
        THIS_DIR,
        "fixtures/atom",
        "test_find_component_parent_with_non_top_level_parent.yaml",
    )
)
def test_find_component_parent_with_non_top_level_parent():
    client = AtomClient(**AUTH)
    resource_id = client.find_parent_id_for_component("test-item")

    assert resource_id == "test-subfonds"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_find_resource_children.yaml")
)
def test_find_resource_children():
    client = AtomClient(**AUTH)
    data = client.get_resource_component_and_children("test-fonds")

    assert type(data) == dict
    assert len(data["children"]) == 1
    assert data["has_children"] is True
    assert data["title"] == "Test fonds"
    assert data["type"] == "resource"


@vcr.use_cassette(
    os.path.join(
        THIS_DIR,
        "fixtures/atom",
        "test_find_resource_children_recursion_level_two.yaml",
    )
)
def test_find_resource_children_recursion_level():
    client = AtomClient(**AUTH)
    data = client.get_resource_component_and_children("test-fonds", recurse_max_level=2)
    assert len(data["children"]) == 1
    assert data["has_children"] is True


@vcr.use_cassette(
    os.path.join(
        THIS_DIR,
        "fixtures/atom",
        "test_find_resource_component_children_at_max_recursion_level.yaml",
    )
)
def test_find_resource_component_children_at_max_recursion_level():
    client = AtomClient(**AUTH)
    record = client.get_resource_component_and_children(
        "test-subfonds", recurse_max_level=1
    )
    assert record["children"] == []
    assert record["has_children"] is True


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_find_collection_ids.yaml")
)
def test_find_collection_ids():
    client = AtomClient(**AUTH)
    ids = client.find_collection_ids()
    assert ids == ["top-level-fonds", "test-fonds"]


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_find_collection_ids_search.yaml")
)
def test_find_collection_ids_search():
    client = AtomClient(**AUTH)
    ids = client.find_collection_ids(search_pattern="Test fonds")
    assert ids == ["test-fonds"]


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_count_collection_ids.yaml")
)
def test_count_collection_ids():
    client = AtomClient(**AUTH)
    ids = client.count_collections()
    assert ids == 2


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_count_collection_ids_search.yaml")
)
def test_count_collection_ids_search():
    client = AtomClient(**AUTH)
    ids = client.count_collections(search_pattern="Top")
    assert ids == 1


@vcr.use_cassette(os.path.join(THIS_DIR, "fixtures/atom", "test_augment_ids.yaml"))
def test_augment_ids():
    client = AtomClient(**AUTH)
    data = client.augment_resource_ids(["top-level-fonds", "test-fonds"])
    assert len(data) == 2
    assert data[0]["title"] == "Top Fonds"
    assert data[0]["type"] == "resource"
    assert data[1]["title"] == "Test fonds"
    assert data[1]["type"] == "resource"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_identifier_exact_match.yaml")
)
def test_identifier_search_exact_match():
    client = AtomClient(**AUTH)
    assert client.find_collection_ids(identifier="F1") == ["top-level-fonds"]
    assert client.count_collections(identifier="F1") == 1
    assert len(client.find_collections(identifier="F1")) == 1


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_add_child_resource.yaml")
)
def test_add_child_resource():
    client = AtomClient(**AUTH)
    slug = client.add_child("test-fonds", title="Second subfonds", level="subfonds")
    assert slug == "second-subfonds"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_add_child_resource_component.yaml")
)
def test_add_child_resource_component():
    client = AtomClient(**AUTH)
    slug = client.add_child("second-subfonds", title="Test child", level="item")
    assert slug == "test-child"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_adding_child_with_note.yaml")
)
def test_adding_child_with_note():
    client = AtomClient(**AUTH)
    slug = client.add_child(
        "test-fonds",
        title="Another subfonds",
        level="subfonds",
        notes=[{"type": "general", "content": "This is a test note"}],
    )
    assert slug == "another-subfonds"


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_posting_contentless_note.yaml")
)
def test_posting_contentless_note():
    client = AtomClient(**AUTH)
    slug = client.add_child(
        "test-fonds",
        title="Yet another subfonds",
        level="subfonds",
        notes=[{"type": "general", "content": ""}],
    )
    assert client.get_record(slug)["notes"] == []


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_delete_record_resource.yaml")
)
def test_delete_record_resource():
    client = AtomClient(**AUTH)
    slug = "another-subfonds"
    assert client.get_record(slug)
    r = client.delete_record(slug)
    assert r["status"] == "Deleted"
    with pytest.raises(CommunicationError):
        client.get_record(slug)


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_edit_archival_object.yaml")
)
def test_edit_archival_object():
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


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_edit_record_empty_note.yaml")
)
def test_edit_record_empty_note():
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


@vcr.use_cassette(
    os.path.join(THIS_DIR, "fixtures/atom", "test_add_digital_object.yaml")
)
def test_add_digital_object():
    client = AtomClient(**AUTH)
    do = client.add_digital_object(
        "test-child",
        title="kitty.jpg",
        uri="http://www.artefactual.com/wp-content/uploads/2016/04/cat.jpg",
    )
    assert do["slug"] == "kitty-jpg"


@vcr.use_cassette(os.path.join(THIS_DIR, "fixtures/atom", "test_date_expression.yaml"))
def test_date_expression():
    client = AtomClient(**AUTH)
    record = client.get_resource_component_and_children(
        "second-subfonds", recurse_max_level=1
    )
    assert record["date_expression"] == "November, 2014 to November, 2015"


@vcr.use_cassette(os.path.join(THIS_DIR, "fixtures/atom", "test_empty_dates.yaml"))
def test_empty_dates():
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
