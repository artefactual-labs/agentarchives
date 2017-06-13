# -*- coding: UTF-8 -*-
import os

import collections
import sys
import unittest

import pytest
import vcr

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)

from agentarchives.archivesspace.client import ArchivesSpaceClient, ArchivesSpaceError, CommunicationError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH = {
    'host': 'http://localhost',
    'user': 'admin',
    'passwd': 'admin'
}


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_listing_collections.yaml'))
def test_listing_collections():
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[0]['title'] == 'Test fonds'
    assert collections[0]['type'] == 'resource'


# The cassette for this test contains a record with a singlepart note, which
# raised errors in a previous version of ArchivesSpaceClient.
@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_singlepart_note.yaml'))
def test_rendering_record_containing_a_singlepart_note():
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert len(collections) == 2
    assert collections[1]['notes'][0]['content'] == 'Singlepart note'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_listing_collections_search.yaml'))
def test_listing_collections_search():
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections(search_pattern='Test fonds')
    assert len(collections) == 1
    assert collections[0]['title'] == 'Test fonds'
    assert collections[0]['type'] == 'resource'

    no_results = client.find_collections(search_pattern='No such fonds')
    assert len(no_results) == 0


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_listing_collections_search_spaces.yaml'))
def test_listing_collections_search_spaces():
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections(identifier="2015044 Aa Ac")
    assert len(collections) == 1
    assert collections[0]['title'] == 'Resource with spaces in the identifier'
    assert collections[0]['levelOfDescription'] == 'collection'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_listing_collections_sort.yaml'))
def test_listing_collections_sort():
    client = ArchivesSpaceClient(**AUTH)
    asc = client.find_collections(sort_by='asc')
    assert len(asc) == 2
    assert asc[0]['title'] == 'Some other fonds'
    assert asc[0]['type'] == 'resource'

    desc = client.find_collections(sort_by='desc')
    assert len(desc) == 2
    assert desc[0]['title'] == 'Test fonds'
    assert desc[0]['type'] == 'resource'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_resource_id.yaml'))
def test_find_resource_id():
    client = ArchivesSpaceClient(**AUTH)
    assert client.find_resource_id_for_component('/repositories/2/archival_objects/3') == '/repositories/2/resources/1'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_component_parent.yaml'))
def test_find_component_parent():
    client = ArchivesSpaceClient(**AUTH)
    type, id = client.find_parent_id_for_component('/repositories/2/archival_objects/3')

    assert type == ArchivesSpaceClient.RESOURCE_COMPONENT
    assert id == '/repositories/2/archival_objects/1'

    type, id = client.find_parent_id_for_component('/repositories/2/archival_objects/1')
    assert type == ArchivesSpaceClient.RESOURCE
    assert id == '/repositories/2/resources/1'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_resource_children.yaml'))
def test_find_resource_children():
    client = ArchivesSpaceClient(**AUTH)
    data = client.get_resource_component_and_children('/repositories/2/resources/1')

    assert type(data) == dict
    assert len(data['children']) == 2
    assert data['has_children'] is True
    assert data['title'] == 'Test fonds'
    assert data['type'] == 'resource'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_resource_children_recursion.yaml'))
def test_find_resource_children_recursion_level():
    client = ArchivesSpaceClient(**AUTH)
    data = client.get_resource_component_and_children('/repositories/2/resources/1',
                                                      recurse_max_level=1)
    assert data['children'] == []
    assert data['has_children'] is True

    data = client.get_resource_component_and_children('/repositories/2/resources/1',
                                                      recurse_max_level=2)
    assert len(data['children']) == 2
    assert data['has_children'] is True


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_resource_children_at_max_recursion_level.yaml'))
def test_find_resource_children_at_max_recursion_level():
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children('/repositories/2/resources/1',
                                                        recurse_max_level=1)
    assert record['children'] == []
    assert record['has_children'] is True


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_resource_component_children_at_max_recursion_level.yaml'))
def test_find_resource_component_children_at_max_recursion_level():
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children('/repositories/2/archival_objects/1',
                                                        recurse_max_level=1)
    assert record['children'] == []
    assert record['has_children'] is True


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_collection_ids.yaml'))
def test_find_collection_ids():
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids()
    assert ids == ['/repositories/2/resources/1', '/repositories/2/resources/2']


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_collection_ids_search.yaml'))
def test_find_collection_ids_search():
    client = ArchivesSpaceClient(**AUTH)
    ids = client.find_collection_ids(search_pattern='Some')
    assert ids == ['/repositories/2/resources/2']

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_count_collection_ids.yaml'))
def test_count_collection_ids():
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections()
    assert ids == 2


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_count_collection_ids_search.yaml'))
def test_count_collection_ids_search():
    client = ArchivesSpaceClient(**AUTH)
    ids = client.count_collections(search_pattern='Some')
    assert ids == 1

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_find_by_id_refid.yaml'))
def test_find_by_id_refid():
    client = ArchivesSpaceClient(**AUTH)
    data = client.find_by_id('archival_objects', 'ref_id', 'a118514fab1b2ee6a7e9ad259e1de355')
    assert len(data) == 1
    item = data[0]
    assert item['identifier'] == 'a118514fab1b2ee6a7e9ad259e1de355'
    assert item['id'] == '/repositories/2/archival_objects/752250'
    assert item['type'] == 'resource_component'
    assert item['title'] == 'Test AO'
    assert item['levelOfDescription'] == 'file'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_augment_ids.yaml'))
def test_augment_ids():
    client = ArchivesSpaceClient(**AUTH)
    data = client.augment_resource_ids(['/repositories/2/resources/1', '/repositories/2/resources/2'])
    assert len(data) == 2
    assert data[0]['title'] == 'Test fonds'
    assert data[0]['type'] == 'resource'
    assert data[1]['title'] == 'Some other fonds'
    assert data[1]['type'] == 'resource'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_resource_type.yaml'))
def test_get_resource_type():
    client = ArchivesSpaceClient(**AUTH)
    assert client.resource_type('/repositories/2/resources/2') == 'resource'
    assert client.resource_type('/repositories/2/archival_objects/3') == 'resource_component'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_resource_type.yaml'))
def test_get_resource_type_raises_on_invalid_input():
    client = ArchivesSpaceClient(**AUTH)
    with pytest.raises(ArchivesSpaceError):
        client.resource_type('invalid')

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_identifier_exact_match.yaml'))
def test_identifier_search_exact_match():
    client = ArchivesSpaceClient(**AUTH)
    assert client.find_collection_ids(identifier='F1') == ['/repositories/2/resources/1']
    assert client.count_collections(identifier='F1') == 1
    assert len(client.find_collections(identifier='F1')) == 1

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_identifier_wildcard.yaml'))
def test_identifier_search_wildcard():
    client = ArchivesSpaceClient(**AUTH)
    # Searching for an identifier prefix with no wildcard returns nothing
    assert client.find_collection_ids(identifier='F') == []
    assert client.count_collections(identifier='F') == 0
    assert len(client.find_collections(identifier='F')) == 0

    assert client.find_collection_ids(identifier='F*') == ['/repositories/2/resources/1', '/repositories/2/resources/2']
    assert client.count_collections(identifier='F*') == 2
    assert len(client.find_collections(identifier='F*')) == 2

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_child_resource.yaml'))
def test_add_child_resource():
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child('/repositories/2/resources/2', title='Test child', level='item')
    assert uri == '/repositories/2/archival_objects/3'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_child_resource_component.yaml'))
def test_add_child_resource_component():
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child('/repositories/2/archival_objects/1', title='Test child', level='item')
    assert uri == '/repositories/2/archival_objects/5'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_adding_child_with_note.yaml'))
def test_adding_child_with_note():
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child('/repositories/2/resources/5',
                           title='Test child',
                           level='item',
                           notes=[{'type': 'odd', 'content': 'This is a test note'}])
    assert uri == '/repositories/2/archival_objects/24'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_posting_contentless_note.yaml'))
def test_posting_contentless_note():
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child('/repositories/2/resources/1',
                           title='Test child',
                           level='recordgrp',
                           notes=[{'type': 'odd', 'content': ''}])
    assert client.get_record(uri)['notes'] == []

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_posting_multiple_notes.yaml'))
def test_posting_multiple_notes():
    client = ArchivesSpaceClient(**AUTH)
    uri = client.add_child('/repositories/2/resources/1',
                           title='Test child',
                           level='recordgrp',
                           notes=[{'type': 'odd', 'content': 'General'}, {'type': 'accessrestrict', 'content': 'Access'}])
    record = client.get_record(uri)
    assert record['notes'][0]['type'] == 'odd'
    assert record['notes'][0]['subnotes'][0]['content'] == 'General'
    assert record['notes'][1]['type'] == 'accessrestrict'
    assert record['notes'][1]['subnotes'][0]['content'] == 'Access'

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_delete_record_resource.yaml'))
def test_delete_record_resource():
    client = ArchivesSpaceClient(**AUTH)
    record_id = '/repositories/2/resources/3'
    assert client.get_record(record_id)
    r = client.delete_record(record_id)
    assert r['status'] == 'Deleted'
    with pytest.raises(CommunicationError):
        client.get_record(record_id)

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_delete_record_archival_object.yaml'))
def test_delete_record_archival_object():
    client = ArchivesSpaceClient(**AUTH)
    record_id = '/repositories/2/archival_objects/4'
    assert client.get_record(record_id)
    r = client.delete_record(record_id)
    assert r['status'] == 'Deleted'
    with pytest.raises(CommunicationError):
        client.get_record(record_id)

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_edit_archival_object.yaml'))
def test_edit_archival_object():
    client = ArchivesSpaceClient(**AUTH)
    original = client.get_record('/repositories/2/archival_objects/3')
    assert original['title'] == 'Test subseries'
    assert original['dates'][0]['end'] == '2015-01-01'
    assert not original['notes']
    new_record = {
        'id': '/repositories/2/archival_objects/3',
        'title': 'Test edited subseries',
        'start_date': '2014-11-01',
        'end_date': '2015-11-01',
        'date_expression': 'November, 2014 to November, 2015',
        'notes': [{
            'type': 'odd',
            'content': 'This is a test note'
        }],
    }
    client.edit_record(new_record)
    updated = client.get_record('/repositories/2/archival_objects/3')
    assert updated['title'] == new_record['title']
    assert updated['dates'][0]['begin'] == new_record['start_date']
    assert updated['dates'][0]['end'] == new_record['end_date']
    assert updated['dates'][0]['expression'] == new_record['date_expression']
    assert updated['notes'][0]['type'] == new_record['notes'][0]['type']
    assert updated['notes'][0]['subnotes'][0]['content'] == new_record['notes'][0]['content']


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_edit_record_empty_note.yaml'))
def test_edit_record_empty_note():
    client = ArchivesSpaceClient(**AUTH)
    original = client.get_record('/repositories/2/archival_objects/3')
    assert original['notes']
    new_record = {
        'id': '/repositories/2/archival_objects/3',
        'title': 'Test edited subseries w/ empty note',
        'start_date': '2014-11-01',
        'end_date': '2015-11-01',
        'date_expression': 'November, 2014 to November, 2015',
        'notes': [{
            'type': 'odd',
            'content': ''
        }],
    }
    client.edit_record(new_record)
    updated = client.get_record('/repositories/2/archival_objects/3')
    assert not updated['notes']

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_edit_record_multiple_notes.yaml'))
def test_edit_record_multiple_notes():
    client = ArchivesSpaceClient(**AUTH)
    new_record = {
        'id': '/repositories/2/archival_objects/9253',
        'notes': [
            {
                'type': 'odd',
                'content': 'General note content'
            },
            {
                'type': 'accessrestrict',
                'content': 'Access restriction note',
            }
        ],
    }
    client.edit_record(new_record)
    updated = client.get_record('/repositories/2/archival_objects/9253')
    assert updated['notes'][0]['type'] == new_record['notes'][0]['type']
    assert updated['notes'][0]['subnotes'][0]['content'] == new_record['notes'][0]['content']

    assert updated['notes'][1]['type'] == new_record['notes'][1]['type']
    assert updated['notes'][1]['subnotes'][0]['content'] == new_record['notes'][1]['content']

@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_digital_object.yaml'))
def test_add_digital_object():
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object('/repositories/2/archival_objects/3',
                                   identifier='38c99e89-20a1-4831-ba57-813fb6420e59',
                                   title='Test digital object')
    assert do['id'] == '/repositories/2/digital_objects/8'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_digital_object_note.yaml'))
def test_digital_object_with_location_of_originals_note():
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object('/repositories/2/archival_objects/3',
                                   identifier='925bfc8a-d6f8-4479-9b6a-d811a4e7f6bf',
                                   title='Test digital object with note',
                                   location_of_originals='The ether')
    note = client.get_record(do['id'])['notes'][0]
    assert note['content'][0] == 'The ether'
    assert note['type'] == 'originalsloc'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_adding_a_digital_object_to_a_record_with_a_singlepart_note.yaml'))
def test_adding_a_digital_object_to_a_record_with_a_singlepart_note():
    client = ArchivesSpaceClient(**AUTH)
    do = client.add_digital_object('/repositories/2/archival_objects/21',
                                   identifier='5f464db2-9365-492f-b7c7-7958baeb0388',
                                   title='Test digital object whose parent has a singlepart note')
    note = client.get_record(do['id'])['notes'][0]
    assert len(note['content']) == 1


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_digital_object_component.yaml'))
def test_add_digital_object_component():
    client = ArchivesSpaceClient(**AUTH)
    doc = client.add_digital_object_component('/repositories/2/digital_objects/1',
                                              label='Test DOC',
                                              title='This is a test DOC')
    assert doc['id'] == '/repositories/2/digital_object_components/3'
    assert doc['label'] == 'Test DOC'
    assert doc['title'] == 'This is a test DOC'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_add_nested_digital_object_component.yaml'))
def test_add_nested_digital_object_component():
    client = ArchivesSpaceClient(**AUTH)
    parent = '/repositories/2/digital_object_components/3'
    doc = client.add_digital_object_component('/repositories/2/digital_objects/1',
                                              parent_digital_object_component=parent,
                                              label='Child DOC',
                                              title='This is a child DOC')
    assert client.get_record(doc['id'])['parent']['ref'] == parent


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_date_expression.yaml'))
def test_date_expression():
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_and_children('/repositories/2/archival_objects/3',
                                                        recurse_max_level=1)
    assert record['date_expression'] == 'November, 2014 to November, 2015'


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_empty_dates.yaml'))
def test_empty_dates():
    client = ArchivesSpaceClient(**AUTH)
    record = client.get_resource_component_children('/repositories/2/archival_objects/2')
    assert record['dates'] == ''
    assert record['date_expression'] == ''
    record = client.get_resource_component_and_children('/repositories/2/resources/2',
                                                        recurse_max_level=1)
    # dates are mandatory for resources, so this record does have a date but no expression
    assert record['date_expression'] == ''
    collections = client.find_collections()
    assert collections[0]['date_expression'] == ''


@vcr.use_cassette(os.path.join(THIS_DIR, 'fixtures', 'test_contentless_notes.yaml'))
def test_contentless_notes():
    client = ArchivesSpaceClient(**AUTH)
    collections = client.find_collections()
    assert collections[-1]['notes'][0]['type'] == 'bioghist'
    assert collections[-1]['notes'][0]['content'] == ''


def test_escaping_solr_queries():
    def escape(s, **kwargs):
        return ArchivesSpaceClient._escape_solr_query(s, **kwargs)

    query = '"quotes"'
    # Test escaping single characters
    assert escape(query, field='identifier') == r'\"quotes\"'
    assert escape(query, field='title') == r'\\"quotes\\"'
    # And double characters, which require only one set of escape tokens
    assert escape('&&test', field='identifier') == r'\&&test'
    assert escape('test') == 'test'


def test_process_notes(monkeypatch):
    empty_note = {'type': 'odd'}
    TestCase = collections.namedtuple('TestCase', 'new_record ret notes')
    tests = (
        # No notes submitted.
        # Behaviour: return False, do nothing.
        TestCase(
            new_record={},
            ret=False,
            notes=None
        ),
        # Empty list.
        # Behaviour: return False, do nothing.
        TestCase(
            new_record={
                'notes': []
            },
            ret=False,
            notes=None
        ),
        # Single empty note.
        # Behaviour: return True, delete notes (empty list).
        TestCase(
            new_record={
                'notes': [
                    empty_note
                ]
            },
            ret=True,
            notes=[]
        ),
        # Multiple notes, all are empty.
        # Behaviour: return True, delete notes (empty list).
        TestCase(
            new_record={
                'notes': [
                    empty_note,
                    empty_note
                ]
            },
            ret=True,
            notes=[]
        ),
        # Multiple notes, first is empty.
        # Behaviour: return True, replace with only non-empty nodes.
        TestCase(
            new_record={
                'notes': [
                    empty_note,
                    {
                        'type': 'odd',
                        'content': 'foobar'
                    }
                ]
            },
            ret=True,
            notes=[
                {
                    'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [
                        {
                            'content': 'foobar',
                            'jsonmodel_type': 'note_text',
                            'publish': True
                        }
                    ],
                    'type': 'odd'
                }
            ]
        ),
        # Multiple notes with content.
        # Behaviour: return True, replace with all notes.
        TestCase(
            new_record={
                'notes': [
                    {
                        'type': 'odd',
                        'content': 'foobar 1'
                    },
                    {
                        'type': 'odd',
                        'content': 'foobar 2'
                    }
                ]
            },
            ret=True,
            notes=[
                {
                    'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [
                        {
                            'content': 'foobar 1',
                            'jsonmodel_type': 'note_text',
                            'publish': True
                        }
                    ],
                    'type': 'odd'
                },
                {
                    'jsonmodel_type': 'note_multipart',
                    'publish': True,
                    'subnotes': [
                        {
                            'content': 'foobar 2',
                            'jsonmodel_type': 'note_text',
                            'publish': True
                        }
                    ],
                    'type': 'odd'
                }
            ]
        )
    )
    for tcase in tests:
        record = {}
        ret = ArchivesSpaceClient._process_notes(record, tcase.new_record)
        assert ret == tcase.ret
        if ret:  # Avoid KeyError when we already know it's undefined.
            assert record['notes'] == tcase.notes
