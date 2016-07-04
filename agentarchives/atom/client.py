import json
import logging
import re
import requests
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from .. import DEFAULT_TIMEOUT

__all__ = ['AtomError', 'ConnectionError', 'AuthenticationError', 'AtomClient']

LOGGER = logging.getLogger(__name__)


class AtomError(Exception):
    pass


class ConnectionError(AtomError):
    pass


class AuthenticationError(AtomError):
    pass


class CommunicationError(AtomError):
    def __init__(self, status_code, response):
        message = 'AtoM server responded with status code {} (URL: {})'.format(status_code, response.url)
        self.response = response
        super(CommunicationError, self).__init__(message)


class AtomClient(object):
    """
    Client to communicate with a remote AtoM installation using its backend API.

    Note that, while functions follow the same API as the ArchivistsToolkitClient, one major difference is the handling of resource and component IDs.
    In ArchivistsToolkitClient, resource IDs are longs representing the database row ID.
    In this client, resource IDs are instead slugs representing the unique part of a record's URL:
        my-fonds-title
    This change is due to the fact that slugs are visible by users whereas IDs aren't.
    """

    def __init__(self, url, key, timeout=DEFAULT_TIMEOUT):
        self.key = key
        self.base_url = urljoin(url, 'api/')
        self.timeout = timeout

        # Create session that will send the access token on each request
        self.session = requests.Session()
        self.session.headers.update({'REST-API-Key': self.key})

    def _request(self, method, url, params, expected_response, data=None):
        # AtoM's REST API won't parse JSON-encoded body data unless this header's set
        headers = {'Content-type': 'application/json'} if data is not None else None

        response = method(url, params=params, data=data, headers=headers, timeout=self.timeout)
        if response.status_code != expected_response:
            LOGGER.error('Response code: %s', response.status_code)
            LOGGER.error('Response body: %s', response.text)
            raise CommunicationError(response.status_code, response)

        if expected_response != 204:
            try:
                output = response.json()
            except Exception:
                raise AtomError("Atom server responded with status {}, but returned a non-JSON document".format(response.status_code))

            if 'error' in output:
                raise AtomError(output['error'])

        return response

    def _get(self, url, params={}, expected_response=200):
        return self._request(self.session.get, url,
                             params=params,
                             expected_response=expected_response)

    def _put(self, url, params={}, data=None, expected_response=200):
        return self._request(self.session.put, url,
                             params=params, data=data,
                             expected_response=expected_response)

    def _post(self, url, params={}, data=None, expected_response=200):
        return self._request(self.session.post, url,
                             params=params, data=data,
                             expected_response=expected_response)

    def _delete(self, url, params={}, expected_response=200):
        return self._request(self.session.delete, url,
                             params=params,
                             expected_response=expected_response)

    def _format_notes(self, record):
        """
        Extracts notes from a record and reformats them in a simplified format.
        """
        notes = []

        if 'notes' in record:
            for note in record['notes']:
                self._append_note_dict_to_list(notes, 'general', note)

        if 'language_and_script_notes' in record:
            self._append_note_dict_to_list(notes, 'language_and_script', record['language_and_script_notes'])

        if 'publication_notes' in record:
            self._append_note_dict_to_list(notes, 'publication_notes', record['publication_notes'])

        if 'physical_characteristics_and_technical_requirements' in record:
            self._append_note_dict_to_list(notes, 'physical_condition', record['physical_characteristics_and_technical_requirements'])

        return notes

    def _append_note_dict_to_list(self, note_list, note_type, note_content):
        n = {}
        n['type'] = note_type
        n['content'] = note_content

        note_list.append(n)

    @staticmethod
    def _escape_lucene_query(query, field=None):
        """
        Escapes special characters in Solr queries.
        Note that this omits * - this is intentionally permitted in user queries.
        The list of special characters is located at http://lucene.apache.org/core/4_0_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#Escaping_Special_Characters
        """
        replacement = r'\\\1'
        return re.sub(r'([\'" +\-!\(\)\{\}\[\]^"~?:\\/]|&&|\|\|)', replacement, query)

    def get_record(self, record_id):
        record = self._get(urljoin(self.base_url, 'informationobjects/{}'.format(record_id))).json()
        if 'dates' in record:
            for date in record['dates']:
                self._format_date_from_atom(date)

        record['notes'] = self._format_notes(record)

        return record

    def _format_date_from_atom(self, date):
        # Map AtoM date specification to generic
        updated_date = {}

        date_mapping = {
            'start_date': 'begin',
            'end_date': 'end',
            'date': 'expression'
        }

        for date_field in date_mapping:
            if date_field in date:
                date[date_mapping[date_field]] = date[date_field]
                del date[date_field]

    def edit_record(self, new_record):
        """
        Update a record in AtoM using the provided new_record.

        The format of new_record is identical to the format returned by get_resource_component_and_children and related methods; consult the documentation for that method in ArchivistsToolkitClient to see the format.
        This means it's possible, for example, to request a record, modify the returned dict, and pass that dict to this method to update the server.

        Currently supported fields are:
            * title
            * notes
            * start_date
            * end_date
            * date_expression

        :raises ValueError: if the 'slug' field isn't specified, or no fields to edit were specified.
        """
        try:
            record_id = new_record['slug']
        except KeyError:
            raise ValueError('No slug provided!')

        record = self.get_record(record_id)

        field_map = {'title': 'title', 'level': 'levelOfDescription'}
        fields_updated = False
        for field, targetfield in field_map.items():
            try:
                record[targetfield] = new_record[field]
                fields_updated = True
            except KeyError:
                continue

        # Optionally add notes
        if 'notes' in new_record and new_record['notes']:
            note = new_record['notes'][0]
            new_note = {
                'content': note['content'],
                'type': note['type']
            }
            # This only supports editing a single note, and a single piece of content
            # within that note.
            # If the record already has at least one note, then replace the first note
            # within that record with this one.
            if not 'notes' in record or record['notes'] == []:
                record['notes'] = [new_note]
            else:
                record['notes'][0] = new_note

            fields_updated = True
        else:
            # Remove existing notes if the record didn't have a valid note;
            # a note with an empty string as content should be counted as
            # a request to delete the note.
            record['notes'] = []

        # Update date
        updated_date = {}

        # Only single dates are currently supported
        if 'dates' in new_record and type(new_record['dates']) is list:
            new_record['dates'] = new_record['dates'][0]

        # Map agentarchives date specification to AtoM specification
        date_mapping = {
            'start_date': 'start_date',
            #'begin': 'start_date',
            'end_date': 'end_date',
            #'end': 'end_date',
            'date_expression': 'date'
        }

        for date_field in date_mapping:
            if date_field in new_record:
                updated_date[date_mapping[date_field]] = new_record[date_field]

        # Add updated date specification to record update
        if updated_date != {}:
            record['dates'] = [updated_date]
            fields_updated = True

        if not fields_updated:
            raise ValueError('No fields to update specified!')

        self._put(urljoin(self.base_url, 'informationobjects/{}'.format(record_id)), data=json.dumps(record))

    def get_levels_of_description(self):
        """
        Returns an array of all levels of description defined in this AtoM instance.
        """
        if not hasattr(self, 'levels_of_description'):
            self.levels_of_description = [item['name'] for item in self._get(urljoin(self.base_url, 'taxonomies/34')).json()]

        return self.levels_of_description

    def collection_list(self, resource_id, resource_type='collection'):
        """
        Fetches a list of slug representing descriptions within the specified parent description.

        :param resource_id str: The slug of the description to fetch children from.
        :param resource_type str: no-op; not required or used in this implementation.

        :return: A list of strings representing the slugs for all children of the requested description.
        :rtype list:
        """
        def fetch_children(children):
            results = []

            for child in children:
                results.append(child['slug'])

                if 'children' in child:
                    results.extend(fetch_children(child['children']))

            return results

        response = self._get(urljoin(self.base_url, 'informationobjects/tree/{}'.format(resource_id)))
        tree = response.json()
        return fetch_children(tree['children'])

    def get_resource_component_children(self, slug):
        """
        Given a resource component, fetches detailed metadata for it and all of its children.

        This is implemented using AtomClient.get_resource_component_children and uses its default options when fetching children.

        :param string slug: The slug of the description from which to fetch metadata.
        """
        return self.get_resource_component_and_children(slug, 'resource_component')

    def _get_resources(self, resource_id, level=1, recurse_max_level=False, sort_by=None):
        def format_record(record, level):
            descend = recurse_max_level != level
            level += 1

            full_record = self.get_record(record['slug'])
            dates = self._fetch_dates_from_record(record)
            date_expression = self._fetch_date_expression_from_record(record)

            result = {
                'id': record['slug'],
                'type': 'resource',
                'sortPosition': level,
                'identifier': record['identifier'],
                'title': record['title'],
                'dates': dates,
                'date_expression': date_expression,
                'display_title': record['title'],
                'levelOfDescription': record.get('level', '')
            }

            if 'notes' in record:
                result['notes'] = record['notes']

            if 'children' in record and descend:
                result['children'] = [format_record(child, level) for child in record['children']]
                result['has_children'] = True
                if sort_by is not None:
                    kwargs = {'reverse': True} if sort_by == 'desc' else {}
                    result['children'] = sorted(result['children'], key=lambda c: c['title'], **kwargs)
            elif 'children' in record:
                result['children'] = []
                result['has_children'] = True
            else:
                result['children'] = False
                result['has_children'] = False

            if 'dates' in full_record:
                result['date_expression'] = full_record['dates'][0]['expression']

            return result

        response = self._get(urljoin(self.base_url, 'informationobjects/tree/{}'.format(resource_id)))
        tree = response.json()
        return format_record(tree, 1)

    def get_resource_component_and_children(self, resource_id, resource_type='collection', level=1, sort_data={}, recurse_max_level=False, sort_by=None, **kwargs):
        """
        Fetch detailed metadata for the specified resource_id and all of its children.

        :param str resource_id: The slug for which to fetch description metadata.
        :param str resource_type: no-op; not required or used in this implementation.
        :param int recurse_max_level: The maximum depth level to fetch when fetching children.
            Default is to fetch all of the resource's children, descending as deeply as necessary.
            Pass 1 to fetch no children.

        :return: A dict containing detailed metadata about both the requested resource and its children.
            Consult ArchivistsToolkitClient.get_resource_component_and_children for the output format.
        :rtype dict:
        """
        return self._get_resources(resource_id, recurse_max_level=recurse_max_level, sort_by=sort_by)

    def _format_dates(self, start, end=None):
        if end is not None:
            return "{}-{}".format(start, end)
        else:
            return start

    def _fetch_dates_from_record(self, record):
        dates = self._fetch_date_expression_from_record(record)
        if not dates:
            try:
                if 'dates' in record:
                    start_date = record['dates'][0]['begin']
                else:
                    return ''
            except IndexError:
                return ''
            end_date = record['dates'][0].get('end')
            return self._format_dates(start_date, end_date)

    def _fetch_date_expression_from_record(self, record):
        if not record.get('dates'):
            return ''
        # use the first date, though there can be multiple sets
        elif 'expression' in record['dates'][0]:
            return record['dates'][0]['expression']
        else:
            return ''

    def find_resource_id_for_component(self, component_id):
        """
        Given the URL to a component, returns the parent resource's URL.

        :param string component_id: The URL of the resource.
        :return: The URL of the component's parent resource.
        :rtype: string
        """
        raise NotImplementedError("AtoM does not implement find_resource_id_for_component")

    def find_parent_id_for_component(self, slug):
        """
        Given the slug of a description, returns the parent description's slug.

        :param string slug: The slug of a description.
        :return: The URL of the parent record.
        :rtype: string
        """
        response = self.get_record(slug)

        if 'parent' in response:
            return response['parent']
        # resource was passed in, which has no higher-up record;
        # return the same ID
        else:
            return slug

    def find_collection_ids(self, search_pattern='', identifier='', fetched=0, page=1):
        """
        Fetches a list of resource URLs for every top-level description in the database.

        :param string search_pattern: A search pattern to use in looking up resources by title or resourceid.
            The search will match any title containing this string;
            for example, "text" will match "this title has this text in it".
            If omitted, then all resources will be fetched.
        :param string identifier: Only records containing this identifier will be returned.
            Substring matching will not be performed; however, wildcards are supported.
            For example, searching "F1" will only return records with the identifier "F1", while searching "F*" will return "F1", "F2", etc.

        :return: A list containing every matched resource's URL.
        :rtype list:
        """
        response = self._collections_search_request(search_pattern, identifier, page)
        hits = response.json()
        results = [r['slug'] for r in hits['results']]

        results_so_far = fetched + len(results)
        if hits['total'] > results_so_far:
            results.extend(self.find_collection_ids(fetched=results_so_far, page=page + 1))

        return results

    def _collections_search_request(self, search_pattern='', identifier='', page=1, page_size=50, sort_by=None):
        """
        Fetches a list of resource URLs for every top-level description in the database.

        :param string search_pattern: A search pattern to use in looking up resources by title or resourceid.
            The search will match any title containing this string;
            for example, "text" will match "this title has this text in it".
            If omitted, then all resources will be fetched.
        :param string identifier: Only records containing this identifier will be returned.
            Substring matching will not be performed; however, wildcards are supported.
            For example, searching "F1" will only return records with the identifier "F1", while searching "F*" will return "F1", "F2", etc.

        :return: A list containing every matched resource's URL.
        :rtype list:
        """
        skip = (page - 1) * page_size

        params = {
            'limit': page_size,
            'skip': skip,
            'topLod': '1',
            'sf0': '_all',
            'sq0': ''
        }

        if search_pattern:
            params['sq0'] = '"' + self._escape_lucene_query(search_pattern) + '"'

        if identifier != '':
            params['sf1'] = 'identifier'
            params['sq1'] = self._escape_lucene_query(identifier)

        if sort_by is not None:
            params['sort'] = 'alphabetic'
            if sort_by == 'desc':
                params['reverse'] = True

        return self._get(urljoin(self.base_url, 'informationobjects'), params=params)

    def count_collections(self, search_pattern='', identifier=''):
        response = self._collections_search_request(search_pattern, identifier, 1)
        return response.json()['total']

    def find_collections(self, search_pattern='', identifier='', fetched=0, page=1, page_size=30, sort_by=None):
        """
        Fetches a list of all resource IDs for every resource in the database.

        :param string search_pattern: A search pattern to use in looking up resources by title or resourceid.
            The search will match any title or resourceid containing this string;
            for example, "text" will match "this title has this text in it".
            If omitted, then all resources will be fetched.
        :param string identifier: Restrict records to only those with this identifier.
            This refers to the human-assigned record identifier, not the automatically generated internal ID.
            This value can contain wildcards.

        :return: A list containing every matched resource's ID.
        :rtype: list
        """
        def format_record(record):
            # Get record details
            full_record = self.get_record(record['slug'])
            dates = self._fetch_dates_from_record(record)
            date_expression = self._fetch_date_expression_from_record(record)

            # Determine whether descendents exist
            url = urljoin(self.base_url, 'informationobjects/tree/{}'.format(record['slug']))
            tree = self._get(url).json()
            if 'children' in tree:
                has_children = len(self._get(url).json()['children']) > 0
            else:
                has_children = False

            formatted = {
                'id': record['slug'],
                'type': 'resource',
                'sortPosition': 1,
                'identifier': record.get('reference_code', ''),
                'title': record.get('title', ''),
                'dates': dates,
                'date_expression': date_expression,
                'children': [] if has_children else False,
                'has_children': has_children,
                'notes': full_record.get('notes', [])
            }

            if 'level_of_description' in record:
                formatted['levelOfDescription'] = record['level_of_description']

            return formatted

        response = self._collections_search_request(search_pattern, identifier, page, page_size, sort_by)
        hits = response.json()
        return [format_record(r) for r in hits['results']]

    def find_by_id(self, object_type, field, value):
        """ Find resource by a specific ID. """
        raise NotImplementedError("AtoM does not implement find_by_id")

    def augment_resource_ids(self, resource_ids):
        """
        Given a list of resource IDs, returns a list of dicts containing detailed information about the specified resources and their children.

        This function recurses to a maximum of two levels when fetching children from the specified resources.
        Consult the documentation of ArchivistsToolkitClient.get_resource_component_children for the format of the returned dicts.

        :param list resource_ids: A list of one or more resource IDs.
        :return: A list containing metadata dicts.
        :rtype list:
        """
        resources_augmented = []
        for id in resource_ids:
            #resource_data = self.get_resource_component_and_children(id, recurse_max_level=2)
            #resources_augmented.append(resource_data)
            resources_augmented.append(
                self.get_resource_component_and_children(id, recurse_max_level=2)
            )

        return resources_augmented

    def add_digital_object(self, information_object_slug, identifier=None, title=None, uri=None, location_of_originals=None, object_type=None, xlink_show="embed", xlink_actuate="onLoad", restricted=False, use_statement="", use_conditions=None, access_conditions=None, size=None, format_name=None, format_version=None, format_registry_key=None, format_registry_name=None, file_uuid=None, aip_uuid=None, inherit_dates=False, usage=None):
        """ Creates a new digital object. """

        new_object = {'information_object_slug': information_object_slug}

        if title is not None:
            new_object['name'] = title

        if uri is not None:
            new_object['uri'] = uri

        if size is not None:
            new_object['byte_size'] = size

        if object_type is not None:
            new_object['media_type'] = object_type

        if usage is not None:
            new_object['usage'] = usage

        if file_uuid is not None:
            new_object['file_uuid'] = file_uuid
        if aip_uuid is not None:
            new_object['aip_uuid'] = aip_uuid

        if format_name is not None:
            new_object['format_name'] = format_name
        if format_version is not None:
            new_object['format_version'] = format_version
        if format_registry_key is not None:
            new_object['format_registry_key'] = format_registry_key
        if format_registry_name is not None:
            new_object['format_registry_name'] = format_registry_name

        new_object['slug'] = self._post(urljoin(self.base_url, 'digitalobjects'), data=json.dumps(new_object), expected_response=201).json()['slug']

        return new_object

    def add_digital_object_component(self, parent_digital_object, parent_digital_object_component=None, label=None, title=None):
        """ Creates a new digital object component. """
        raise NotImplementedError("add_digital_object_component not yet implemented in AtoM client")

    def add_child(self, parent_slug=None, title="", level="", start_date=None, end_date=None, date_expression=None, notes=[]):
        """
        Adds a new resource component parented within `parent`.

        :param str parent_slug: The parent's slug.
        :param str title: A title for the record.
        :param str level: The level of description.

        :return: The ID of the newly-created record.
        """

        new_object = {
            "title": title,
            "level_of_description": level
        }

        if parent_slug is not None:
            new_object['parent_slug'] = parent_slug

        # Optionally add date specification
        new_date = {}

        if start_date is not None:
            new_date['start_date'] = start_date

        if end_date is not None:
            new_date['end_date'] = end_date

        if date_expression is not None:
            new_date['date'] = date_expression

        if new_date != {}:
            new_object['dates'] = [new_date]

        # Optionally add notes
        new_object['notes'] = []
        for note in notes:
            note_type = note.get('type', 'General note')
            # If there is a note, but it's an empty string, skip this;
            content = note.get('content')
            if not content:
                continue
            new_note = {
                'content': content,
                'type': note_type
            }
            new_object['notes'].append(new_note)

        return self._post(urljoin(self.base_url, 'informationobjects'), data=json.dumps(new_object), expected_response=201).json()['slug']

    def delete_record(self, record_id):
        """
        Delete a record with record_id.
        """
        self._delete(urljoin(self.base_url, 'informationobjects/{}'.format(record_id)), expected_response=204)
        return {'status': 'Deleted'}
