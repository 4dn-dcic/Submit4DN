#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""All common classes and methods for dcic work."""
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


class FDN_Key:
    """captures the keyfile parameters."""

    def __init__(self, keyfile, keyname):
        """open key file and extract parameters."""
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


class FDN_Connection(object):
    """sets parameters for the api connection."""

    def __init__(self, key):
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.server = key.server
        self.auth = (key.authid, key.authpw)


class FDN_Collection(object):
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
        self.schema = get_FDN(schema_uri, connection)
        self.frame = frame
        search_string = '/search/?format=json&limit=all&\
                        type=%s&frame=%s' % (self.search_name, frame)
        collection = get_FDN(search_string, connection)
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


class FDN_Schema(object):
    def __init__(self, connection, uri):
        self.uri = uri
        self.connection = connection
        self.server = connection.server
        response = get_FDN(uri, connection)
        self.properties = response['properties']


class FDN_Item(object):
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
            item = get_FDN(get_string, connection)
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
            on_server = get_FDN(get_string, self.connection)
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


def get_FDN(obj_id, connection, frame="object"):
    '''GET an FDN object as JSON and return as dict'''
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

class GetFields():
    def __init__(self, connection, args, facet=None):
        self.connection = connection
        self.data = []
        self.header = []
        self.accessions = []
        self.fields = []
        self.subobj = ""
        self.facet = facet
        self.args = args

    def setup(self):
        ''' facet contains a list with the first item being a list
        of the accessions and the second a list of the fieldnames
        essentially: facet = [ [accession1, accession2, ...], [field1, field2, ...] ]'''
        if self.facet:
            self.accessions = self.facet[0]
            self.fields = self.facet[1]
        else:
            temp = []
            if self.args.collection:
                if self.args.es:
                    temp = get_FDN("/search/?type=" + self.args.collection, self.connection).get("@graph", [])
                else:
                    temp = get_FDN(self.args.collection, self.connection, frame=None).get("@graph", [])
            elif self.args.query:
                if "search" in self.args.query:
                    temp = get_FDN(self.args.query, self.connection).get("@graph", [])
                else:
                    temp = [get_FDN(self.args.query, self.connection)]
            elif self.args.object:
                if os.path.isfile(self.args.object):
                    self.accessions = [line.strip() for line in open(self.args.object)]
                else:
                    self.accessions = self.args.object.split(",")
            if any(temp):
                for obj in temp:
                    if obj.get("accession"):
                        self.accessions.append(obj["accession"])
                    elif obj.get("uuid"):
                        self.accessions.append(obj["uuid"])
                    elif obj.get("@id"):
                        self.accessions.append(obj["@id"])
                    elif obj.get("aliases"):
                        self.accessions.append(obj["aliases"][0])
                    else:
                        print("ERROR: object has no identifier", file=sys.stderr)
            if self.args.allfields:
                if self.args.collection:
                    obj = get_FDN("/profiles/" + self.args.collection + ".json", self.connection).get("properties")
                else:
                    obj_type = get_FDN(self.accessions[0], self.connection).get("@type")
                    if any(obj_type):
                        obj = get_FDN("/profiles/" + obj_type[0] + ".json", self.connection).get("properties")
                self.fields = list(obj.keys())
                for key in obj.keys():
                    if obj[key]["type"] == "string":
                        self.header.append(key)
                    else:
                        self.header.append(key + ":" + obj[key]["type"])
                self.header.sort()
            elif self.args.field:
                if os.path.isfile(self.args.field):
                    self.fields = [line.strip() for line in open(self.args.field)]
                else:
                    self.fields = self.args.field.split(",")
        if len(self.accessions) == 0:
            print("ERROR: Need to provide accessions", file=sys.stderr)
            sys.exit(1)
        if len(self.fields) == 0:
            print("ERROR: Need to provide fields!", file=sys.stderr)
            sys.exit(1)

    def get_fields(self):
        import csv
        from collections import deque
        self.setup()
        self.header = ["accession"]
        for acc in self.accessions:
            acc = quote(acc)
            obj = get_FDN(acc, self.connection)
            newObj = {}
            newObj["accession"] = acc
            for f in self.fields:
                path = deque(f.split("."))  # check to see if someone wants embedded value
                field = self.get_embedded(path, obj)  # get the last element in the split list
                if field:  # after the above loop, should have final field value
                    name = f
                    if not self.facet:
                        name = name + self.get_type(field)
                    newObj[name] = field
                    if not self.args.allfields:
                        if name not in self.header:
                            self.header.append(name)
            self.data.append(newObj)
        if not self.facet:
            writer = csv.DictWriter(sys.stdout, delimiter='\t', fieldnames=self.header)
            writer.writeheader()
            for d in self.data:
                writer.writerow(d)

    def get_type(self, attr):
        ''' given an object return its type as a string to append
        '''
        if type(attr) == int:
            return ":integer"
        elif type(attr) == list:
            return ":array"
        elif type(attr) == dict:
            return ":dict"
        else:
            # this must be a string
            return ""

    def get_embedded(self, path, obj):
        '''
        The 'path' is built from a string such as "target.title"
        that has been split on the "." to result in ["target", "title"]
        and saved as a queue object

        'obj' is the object currently being explored and expanded

        The 'path' queue is checked for length, because it points to the final
        location of the desired value, if the queue is 1 then we have reached
        the bottom of the search and we return "obj[path]" value
        Otherwise the leftmost item is popped from the list and treated as a
        link to the new object to be expanded, then the new object and the
        shortened queue are fed back into the method

        EXAMPLE:
        path = ["target", "title"]
        obj = {Experiment}
        Length is greather than 1, pop leftmost value
        field = "target"
        path = ["title"]

        get obj[field] and save as new obj, in this case Experiment["target"]
        call get_embedded() with new value for path and obj

        path = ["title"]
        obj = {target}
        path is length 1, we have reached end of search queue
        pop leftmost value
        field = "title"
        return obj[field] which is target["title"]

        There are some special cases checked for, such as if the value
        expended is a list-type setup, such as path = ["replicates", "status"]

        Here path.popleft() gets us "replicates" which is a list
        This list is stored temporarily and then iterated through
        immediately to retrieve the next value (in this case "status")

        This is why it can't retrieve lists the are doubly embedded
            Ex: path = ["replicates", "library", "anyvalue"]
                won't work because both replicates and library are lists

        There is another special check for "files" to iterate through it
        '''
        if len(path) > 1:
            field = path.popleft()  # first element in queue
            if obj.get(field):  # check to see if the element is in the current object
                if field == "files":
                    files_list = []  # empty list for later
                    for f in obj[field]:
                        temp = get_FDN(f, self.connection)
                        if temp.get(path[0]):
                            if len(path) == 1:  # if last element in path then get from each item in list
                                files_list.append(temp[path[0]])  # add items to list
                            else:
                                return self.get_embedded(path, temp)
                    if self.args.listfull:
                        return files_list
                    else:
                        return list(set(files_list))  # return unique list of last element items
                else:
                    if type(obj[field]) == int:
                        return obj[field]  # just return integers as is, we can't expand them
                    elif type(obj[field]) == list:
                        if len(path) == 1:  # if last element in path then get from each item in list
                            files_list = []
                            for f in obj[field]:
                                if type(f) == dict:  # if this is like a flowcell or something it should catch here
                                    return f
                                temp = get_FDN(f, self.connection)
                                if temp.get(path[0]):
                                    if type(temp[path[0]]) == list:
                                        files_list.append(temp[path[0]][0])
                                    else:
                                        files_list.append(temp[path[0]])
                            if self.args.listfull:
                                return files_list
                            else:
                                return list(set(files_list))  # return unique list of last element items
                        elif self.facet:  # facet is a special case for the search page flattener
                            temp = get_FDN(obj[field][0], self.connection)
                            return self.get_embedded(path, temp)
                        else:  # if this is not the last item in the path, but we are in a list
                            return obj[field]  # return the item since we can't dig deeper without getting lost
                    elif type(obj[field]) == dict:
                        return obj[field]  # return dictionary objects, probably things like flowcells anyways
                    else:
                        temp = get_FDN(obj[field], self.connection)  # if found get_FDN the embedded object
                        return self.get_embedded(path, temp)
            else:  # if not obj.get(field) then we kick back an error
                return ""
        else:
            field = path.popleft()
            if obj.get(field):
                return obj[field]
            else:
                return ""
