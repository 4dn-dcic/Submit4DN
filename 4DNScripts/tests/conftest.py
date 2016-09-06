import pytest

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
                    'properties': {'experiment': {'description': 'The '
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
