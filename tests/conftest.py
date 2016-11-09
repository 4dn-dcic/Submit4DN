# flake8: noqa 
import pytest
import wranglertools.fdnDCIC as fdnDCIC


class MockedResponse(object):
    def __init__(self, json, status):
        self._json = json
        self.status_code = status

    def json(self):
        return self._json


@pytest.fixture
def connection():
    keypairs2 = {
                "default":
                {"server": "https://data.4dnucleome.org/",
                 "key": "testkey",
                 "secret": "testsecret"
                 }
                }
    key = fdnDCIC.FDN_Key(keypairs2, "default")
    connection = fdnDCIC.FDN_Connection(key)
    return connection


@pytest.fixture
def connection_public():
    keypairs2 = {
                "default":
                {"server": "https://data.4dnucleome.org/",
                 "key": "",
                 "secret": ""
                 }
                }
    key2 = fdnDCIC.FDN_Key(keypairs2, "default")
    connection = fdnDCIC.FDN_Connection(key2)
    return connection


@pytest.fixture(scope="module")
def item_properties():
    return {'@id': {'calculatedProperty': True, 'title': 'ID', 'type': 'string'},
            '@type': {'calculatedProperty': True,
                      'items': {'type': 'string'},
                      'title': 'Type',
                      'type': 'array'},
            'description': {'rdfs:subPropertyOf': 'dc:description',
                            'title': 'Description',
                            'type': 'string'},
            "experiment_sets": {"type": "array",
                                "description": "Experiment Sets that are associated with this experiment.",
                                "title": "Experiment Sets",
                                "items": {
                                    "type": "string",
                                    "description": "An experiment set that is associated wtih this experiment.",
                                    "linkTo": "ExperimentSet",
                                    "title": "Experiment Set"},
                                "uniqueItems": True},
            'end_date': {'anyOf': [{'format': 'date-time'}, {'format': 'date'}],
                         'comment': 'Date can be submitted as YYYY-MM-DD or '
                         'YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone '
                         'designator; use Z to express time in UTC or for time '
                         'expressed in local time add a time zone offset from '
                         'UTC +HH:MM or -HH:MM).',
                         'title': 'End date',
                         'type': 'string'},
            'name': {'description': 'The official grant number from the NIH database, if '
                     'applicable',
                     'pattern': '^[A-Za-z0-9\\-]+$',
                     'title': 'Number',
                     'type': 'string',
                     'uniqueKey': True},
            'pi': {'comment': 'See user.json for available identifiers.',
                   'description': 'Principle Investigator of the grant.',
                   'linkTo': 'User',
                   'title': 'P.I.',
                   'type': 'string'},
            'project': {'description': 'The name of the consortium project',
                        'enum': ['4DN', 'External'],
                        'title': 'Project',
                        'type': 'string'},
            'schema_version': {'comment': 'Do not submit, value is assigned by the '
                               'server. The version of the JSON schema that '
                               'the server uses to validate the object. Schema '
                               'version indicates generation of schema used to '
                               'save version to to enable upgrade steps to '
                               'work. Individual schemas should set the '
                               'default.',
                               'default': '1',
                               'pattern': '^\\d+(\\.\\d+)*$',
                               'requestMethod': [],
                               'title': 'Schema Version',
                               'type': 'string'},
            'start_date': {'anyOf': [{'format': 'date-time'}, {'format': 'date'}],
                           'comment': 'Date can be submitted as YYYY-MM-DD or '
                           'YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone '
                           'designator; use Z to express time in UTC or for '
                           'time expressed in local time add a time zone '
                           'offset from UTC +HH:MM or -HH:MM).',
                           'title': 'Start date',
                           'type': 'string'},
            'status': {'default': 'current',
                       'enum': ['current',
                                'in progress',
                                'deleted',
                                'replaced',
                                'released',
                                'revoked'],
                       'title': 'Status',
                       'type': 'string'},
            'title': {'description': 'The grant name from the NIH database, if '
                      'applicable.',
                      'rdfs:subPropertyOf': 'dc:title',
                      'title': 'Name',
                      'type': 'string'},
            'url': {'@type': '@id',
                    'description': 'An external resource with additional information '
                    'about the grant.',
                    'format': 'uri',
                    'rdfs:subPropertyOf': 'rdfs:seeAlso',
                    'title': 'URL',
                    'type': 'string'},
            'uuid': {'format': 'uuid',
                     'requestMethod': 'POST',
                     'serverDefault': 'uuid4',
                     'title': 'UUID',
                     'type': 'string'},
            'viewing_group': {'description': 'The group that determines which set of data '
                              'the user has permission to view.',
                              'enum': ['4DN', 'Not 4DN'],
                              'title': 'View access group',
                              'type': 'string'}}


@pytest.fixture
def calc_properties():
    return {'@id': {'calculatedProperty': True, 'title': 'ID', 'type':
                    'string'},
            '@type': {'calculatedProperty': True,
                      'items': {'type': 'string'},
                      'title': 'Type',
                      'type': 'array'},
            'description': {'rdfs:subPropertyOf': 'dc:description',
                            'title': 'Description',
                            'type': 'string'},
            }


@pytest.fixture
def embed_properties():
    return {'experiment_relation': {'description': 'All related experiments',
                                    'items': {'additionalProperties': False,
                                              'properties':
                                              {'experiment': {'description': 'The '
                                                                             'related '
                                                                             'experiment',
                                                              'linkTo': 'Experiment',
                                                              'type': 'string'},
                                               'relationship_type': {'description': 'A '
                                                                     'controlled '
                                                                     'term '
                                                                     'specifying '
                                                                     'the '
                                                                     'relationship '
                                                                     'between '
                                                                     'experiments.',
                                                                     'enum': ['controlled '
                                                                              'by',
                                                                              'control '
                                                                              'for',
                                                                              'derived '
                                                                              'from',
                                                                              'source '
                                                                              'for'],
                                                                     'title': 'Relationship '
                                                                              'Type',
                                                                              'type': 'string'}},
                                              'title': 'Experiment relation',
                                              'type': 'object'},
                                    'title': 'Experiment relations',
                                    'type': 'array'},
            }


@pytest.fixture
def file_metadata():
    from collections import OrderedDict
    return OrderedDict([('aliases', 'dcic:HIC00test2'),
                        ('award', '/awards/OD008540-01/'),
                        ('file_classification', 'raw file'),
                        ('file_format', 'fastq'),
                        ('filesets', ''),
                        ('instrument', 'Illumina HiSeq 2000'),
                        ('lab', '/labs/erez-liebermanaiden-lab/'),
                        ('paired_end', ''),
                        ('related_files.file', 'testfile.fastq'),
                        ('related_files.relationship_type', 'related_to'),
                        ('experiment_relation.experiment', 'test:exp002'),
                        ('experiment_relation.relationship_type', 'controlled by'),
                        ('experiment_relation.experiment-1', 'test:exp003'),
                        ('experiment_relation.relationship_type-1', 'source for'),
                        ('experiment_relation.experiment-2', 'test:exp004'),
                        ('experiment_relation.relationship_type-2', 'source for'),
                        ('status', 'uploaded')])


@pytest.fixture
def file_metadata_type():
    return {'aliases': 'array',
            'award': 'string',
            'file_classification': 'string',
            'file_format': 'string',
            'filesets': 'array',
            'instrument': 'string',
            'lab': 'string',
            'paired_end': 'string',
            'related_files.file': 'array',
            'related_files.relationship_type': 'array',
            'experiment_relation.experiment': 'array',
            'experiment_relation.relationship_type': 'array',
            'experiment_relation.experiment-1': 'array',
            'experiment_relation.relationship_type-1': 'array',
            'experiment_relation.experiment-2': 'array',
            'experiment_relation.relationship_type-2': 'array',
            'status': 'string'}


@pytest.fixture
def returned_award_schema():
    data = {"title":"Grant","id":"/profiles/award.json","$schema":"http://json-schema.org/draft-04/schema#","required":["name"],"identifyingProperties":["uuid","name","title"],"additionalProperties":False,"mixinProperties":[{"$ref":"mixins.json#/schema_version"},{"$ref":"mixins.json#/uuid"},{"$ref":"mixins.json#/submitted"},{"$ref":"mixins.json#/status"}],"type":"object","properties":{"status":{"readonly":True,"type":"string","default":"released","enum":["released","current","revoked","deleted","replaced","in review by lab","in review by project","released to project"],"title":"Status","permission":"import_items"},"submitted_by":{"readonly":True,"type":"string","serverDefault":"userid","linkTo":"User","comment":"Do not submit, value is assigned by the server. The user that created the object.","title":"Submitted by","rdfs:subPropertyOf":"dc:creator","permission":"import_items"},"date_created":{"readonly":True,"type":"string","serverDefault":"now","anyOf":[{"format":"date-time"},{"format":"date"}],"comment":"Do not submit, value is assigned by the server. The date the object is created.","title":"Date created","rdfs:subPropertyOf":"dc:created","permission":"import_items"},"uuid":{"requestMethod":"POST","readonly":True,"type":"string","serverDefault":"uuid4","format":"uuid","title":"UUID","permission":"import_items"},"schema_version":{"requestMethod":[],"type":"string","default":"1","pattern":"^\\d+(\\.\\d+)*$","comment":"Do not submit, value is assigned by the server. The version of the JSON schema that the server uses to validate the object. Schema version indicates generation of schema used to save version to to enable upgrade steps to work. Individual schemas should set the default.","title":"Schema Version"},"title":{"description":"The grant name from the NIH database, if applicable.","type":"string","title":"Name","rdfs:subPropertyOf":"dc:title"},"name":{"description":"The official grant number from the NIH database, if applicable","uniqueKey":True,"type":"string","title":"Number","pattern":"^[A-Za-z0-9\\-]+$"},"description":{"type":"string","title":"Description","rdfs:subPropertyOf":"dc:description"},"start_date":{"anyOf":[{"format":"date-time"},{"format":"date"}],"comment":"Date can be submitted as YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone designator; use Z to express time in UTC or for time expressed in local time add a time zone offset from UTC +HH:MM or -HH:MM).","type":"string","title":"Start date"},"end_date":{"anyOf":[{"format":"date-time"},{"format":"date"}],"comment":"Date can be submitted as YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone designator; use Z to express time in UTC or for time expressed in local time add a time zone offset from UTC +HH:MM or -HH:MM).","type":"string","title":"End date"},"url":{"format":"uri","type":"string","@type":"@id","description":"An external resource with additional information about the grant.","title":"URL","rdfs:subPropertyOf":"rdfs:seeAlso"},"pi":{"description":"Principle Investigator of the grant.","comment":"See user.json for available identifiers.","type":"string","title":"P.I.","linkTo":"User"},"project":{"description":"The name of the consortium project","type":"string","title":"Project","enum":["4DN","External"]},"viewing_group":{"description":"The group that determines which set of data the user has permission to view.","type":"string","title":"View access group","enum":["4DN","Not 4DN"]},"@id":{"calculatedProperty":True,"type":"string","title":"ID"},"@type":{"calculatedProperty":True,"title":"Type","type":"array","items":{"type":"string"}}},"boost_values":{"name":1,"title":1,"pi.title":1},"@type":["JSONSchema"]}
    return MockedResponse(data, 200)


@pytest.fixture
def award_dict():
    return {'properties': {'project': {'type': 'string', 'title': 'Project', 'description': 'The name of the consortium project', 'enum': ['4DN', 'External']}, 'start_date': {'anyOf': [{'format': 'date-time'}, {'format': 'date'}], 'type': 'string', 'title': 'Start date', 'comment': 'Date can be submitted as YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone designator; use Z to express time in UTC or for time expressed in local time add a time zone offset from UTC +HH:MM or -HH:MM).'}, '@id': {'type': 'string', 'title': 'ID', 'calculatedProperty': True}, 'description': {'type': 'string', 'rdfs:subPropertyOf': 'dc:description', 'title': 'Description'}, 'end_date': {'anyOf': [{'format': 'date-time'}, {'format': 'date'}], 'type': 'string', 'title': 'End date', 'comment': 'Date can be submitted as YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSTZD (TZD is the time zone designator; use Z to express time in UTC or for time expressed in local time add a time zone offset from UTC +HH:MM or -HH:MM).'}, 'name': {'uniqueKey': True, 'type': 'string', 'pattern': '^[A-Za-z0-9\\-]+$', 'title': 'Number', 'description': 'The official grant number from the NIH database, if applicable'}, '@type': {'items': {'type': 'string'}, 'type': 'array', 'title': 'Type', 'calculatedProperty': True}, 'submitted_by': {'serverDefault': 'userid', 'permission': 'import_items', 'type': 'string', 'rdfs:subPropertyOf': 'dc:creator', 'title': 'Submitted by', 'readonly': True, 'linkTo': 'User', 'comment': 'Do not submit, value is assigned by the server. The user that created the object.'}, 'date_created': {'serverDefault': 'now', 'permission': 'import_items', 'type': 'string', 'rdfs:subPropertyOf': 'dc:created', 'title': 'Date created', 'readonly': True, 'comment': 'Do not submit, value is assigned by the server. The date the object is created.', 'anyOf': [{'format': 'date-time'}, {'format': 'date'}]}, 'title': {'type': 'string', 'rdfs:subPropertyOf': 'dc:title', 'title': 'Name', 'description': 'The grant name from the NIH database, if applicable.'}, 'viewing_group': {'type': 'string', 'title': 'View access group', 'description': 'The group that determines which set of data the user has permission to view.', 'enum': ['4DN', 'Not 4DN']}, 'schema_version': {'type': 'string', 'pattern': '^\\d+(\\.\\d+)*$', 'title': 'Schema Version', 'default': '1', 'requestMethod': [], 'comment': 'Do not submit, value is assigned by the server. The version of the JSON schema that the server uses to validate the object. Schema version indicates generation of schema used to save version to to enable upgrade steps to work. Individual schemas should set the default.'}, 'url': {'type': 'string', 'rdfs:subPropertyOf': 'rdfs:seeAlso', 'format': 'uri', 'title': 'URL', 'description': 'An external resource with additional information about the grant.', '@type': '@id'}, 'uuid': {'serverDefault': 'uuid4', 'permission': 'import_items', 'type': 'string', 'format': 'uuid', 'title': 'UUID', 'readonly': True, 'requestMethod': 'POST'}, 'status': {'enum': ['released', 'current', 'revoked', 'deleted', 'replaced', 'in review by lab', 'in review by project', 'released to project'], 'permission': 'import_items', 'type': 'string', 'title': 'Status', 'readonly': True, 'default': 'released'}, 'pi': {'linkTo': 'User', 'type': 'string', 'title': 'P.I.', 'description': 'Principle Investigator of the grant.', 'comment': 'See user.json for available identifiers.'}}, 'type': 'object', 'mixinProperties': [{'$ref': 'mixins.json#/schema_version'}, {'$ref': 'mixins.json#/uuid'}, {'$ref': 'mixins.json#/submitted'}, {'$ref': 'mixins.json#/status'}], 'title': 'Grant', 'required': ['name'], 'boost_values': {'pi.title': 1.0, 'title': 1.0, 'name': 1.0}, 'identifyingProperties': ['uuid', 'name', 'title'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-04/schema#', '@type': ['JSONSchema'], 'id': '/profiles/award.json'}
