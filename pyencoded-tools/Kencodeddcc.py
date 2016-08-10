#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import requests
import json
import sys
import logging
from urllib.parse import urljoin
from urllib.parse import quote
import os.path
import hashlib
import copy
import subprocess


class dict_diff(object):
    """
    Calculate items added, items removed, keys same in both but changed values,
    keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        diff = self.current_keys - self.intersect
        if diff == set():
            return None
        else:
            return diff

    def removed(self):
        diff = self.past_keys - self.intersect
        if diff == set():
            return None
        else:
            return diff

    def changed(self):
        diff = set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])
        if diff == set():
            return None
        else:
            return diff

    def unchanged(self):
        diff = set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
        if diff == set():
            return None
        else:
            return diff

    def same(self):
        return self.added() is None and self.removed() is None and self.changed() is None


class ENC_Key:
    def __init__(self, keyfile, keyname):
        if os.path.isfile(str(keyfile)):
            keys_f = open(keyfile, 'r')
            keys_json_string = keys_f.read()
            keys_f.close()
            keys = json.loads(keys_json_string)
        else:
            keys = keyfile
        key_dict = keys[keyname]
        self.authid = key_dict['key']
        self.authpw = key_dict['secret']
        self.server = key_dict['server']
        if not self.server.endswith("/"):
            self.server += "/"


class ENC_Connection(object):
    def __init__(self, key):
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.server = key.server
        self.auth = (key.authid, key.authpw)


class ENC_Collection(object):
    def __init__(self, connection, supplied_name, frame='object'):
        if supplied_name.endswith('s'):
            self.name = supplied_name.replace('_', '-')
            self.search_name = supplied_name.rstrip('s').replace('-', '_')
            self.schema_name = self.search_name + '.json'
        elif supplied_name.endswith('.json'):
            self.name = supplied_name.replace('_', '-').rstrip('.json')
            self.search_name = supplied_name.replace('-', '_').rstrip('.json')
            self.schema_name = supplied_name
        else:
            self.name = supplied_name.replace('_', '-') + 's'
            self.search_name = supplied_name.replace('-', '_')
            self.schema_name = supplied_name.replace('-', '_') + '.json'
        schema_uri = '/profiles/' + self.schema_name
        self.connection = connection
        self.server = connection.server
        self.schema = get_ENCODE(schema_uri, connection)
        self.frame = frame
        search_string = '/search/?format=json&limit=all&\
                        type=%s&frame=%s' % (self.search_name, frame)
        collection = get_ENCODE(search_string, connection)
        self.items = collection['@graph']
        self.es_connection = None

    def query(self, query_dict, maxhits=10000):
        from pyelasticsearch import ElasticSearch
        if self.es_connection is None:
            es_server = self.server.rstrip('/') + ':9200'
            self.es_connection = ElasticSearch(es_server)
        results = self.es_connection.search(query_dict, index='encoded',
                                            doc_type=self.search_name,
                                            size=maxhits)
        return results

global schemas
schemas = []


class ENC_Schema(object):
    def __init__(self, connection, uri):
        self.uri = uri
        self.connection = connection
        self.server = connection.server
        response = get_ENCODE(uri, connection)
        self.properties = response['properties']


class ENC_Item(object):
    def __init__(self, connection, id, frame='object'):
        self.id = id
        self.connection = connection
        self.server = connection.server
        self.frame = frame

        if id is None:
            self.type = None
            self.properties = {}
        else:
            if id.rfind('?') == -1:
                get_string = id + '?'
            else:
                get_string = id + '&'
            get_string += 'frame=%s' % (frame)
            item = get_ENCODE(get_string, connection)
            self.type = next(x for x in item['@type'] if x != 'item')
            self.properties = item

    def get(self, key):
        try:
            return self.properties[key]
        except KeyError:
            return None

    def sync(self):
        if self.id is None:  # There is no id, so this is a new object to POST
            excluded_from_post = ['schema_version']
            self.type = self.properties.pop('@type')
            schema_uri = 'profiles/%s.json' % (self.type)
            try:
                schema = next(x for x in schemas if x.uri == schema_uri)
            except StopIteration:
                schema = ENC_Schema(self.connection, schema_uri)
                schemas.append(schema)

            post_payload = {}
            for prop in self.properties:
                if prop in schema.properties and prop not in excluded_from_post:
                    post_payload.update({prop: self.properties[prop]})
                else:
                    pass
            # should return the new object that comes back from the patch
            new_object = new_ENCODE(self.connection, self.type, post_payload)

        else:  # existing object to PATCH or PUT
            if self.id.rfind('?') == -1:
                get_string = self.id + '?'
            else:
                get_string = self.id + '&'
            get_string += 'frame=%s' % (self.frame)
            on_server = get_ENCODE(get_string, self.connection)
            diff = dict_diff(on_server, self.properties)
            if diff.same():
                logging.warning("%s: No changes to sync" % (self.id))
            elif diff.added() or diff.removed():  # PUT
                excluded_from_put = ['schema_version']
                schema_uri = '/profiles/%s.json' % (self.type)
                try:
                    schema = next(x for x in schemas if x.uri == schema_uri)
                except StopIteration:
                    schema = ENC_Schema(self.connection, schema_uri)
                    schemas.append(schema)

                put_payload = {}
                for prop in self.properties:
                    if prop in schema.properties and prop not in excluded_from_put:
                        put_payload.update({prop: self.properties[prop]})
                    else:
                        pass
                # should return the new object that comes back from the patch
                new_object = replace_ENCODE(self.id, self.connection, put_payload)

            else:  # PATCH

                excluded_from_patch = ['schema_version', 'accession', 'uuid']
                patch_payload = {}
                for prop in diff.changed():
                    if prop not in excluded_from_patch:
                        patch_payload.update({prop: self.properties[prop]})
                # should probably return the new object that comes back from the patch
                new_object = patch_ENCODE(self.id, self.connection, patch_payload)

        return new_object

    def new_creds(self):
        if self.type.lower() == 'file':  # There is no id, so this is a new object to POST
            r = requests.post("%s/%s/upload/" % (self.connection.server, self.id),
                              auth=self.connection.auth,
                              headers=self.connection.headers,
                              data=json.dumps({}))
            return r.json()['@graph'][0]['upload_credentials']
        else:
            return None


def get_ENCODE(obj_id, connection, frame="object"):
    '''GET an ENCODE object as JSON and return as dict'''
    if frame is None:
        if '?' in obj_id:
            url = urljoin(connection.server, obj_id+'&limit=all')
        else:
            url = urljoin(connection.server, obj_id+'?limit=all')
    elif '?' in obj_id:
        url = urljoin(connection.server, obj_id+'&limit=all&frame='+frame)
    else:
        url = urljoin(connection.server, obj_id+'?limit=all&frame='+frame)
    logging.debug('GET %s' % (url))
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    logging.debug('GET RESPONSE code %s' % (response.status_code))
    try:
        if response.json():
            logging.debug('GET RESPONSE JSON: %s' % (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    except:
        logging.debug('GET RESPONSE text %s' % (response.text))
    if not response.status_code == 200:
        if response.json().get("notification"):
            logging.warning('%s' % (response.json().get("notification")))
        else:
            logging.warning('GET failure.  Response code = %s' % (response.text))
    return response.json()
