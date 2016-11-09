import pytest
import wranglertools.fdnDCIC as fdnDCIC

# test data is in conftest.py

keypairs = {
            "default":
            {"server": "https://test.FDN.org",
             "key": "keystring",
             "secret": "secretstring"
             }
            }


def test_nothing():
    assert(1)


def test_key():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    assert(key)
    assert(type(key.server) is str)
    assert(type(key.authpw) is str)
    assert(type(key.authid) is str)


def test_key_file():
    key = fdnDCIC.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert(type(key.server) is str)
    assert(type(key.authpw) is str)
    assert(type(key.authid) is str)


@pytest.mark.connection
def test_connection():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    assert(connection)
    assert(connection.auth)
    assert(connection.server)


def test_FDN_url():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    test_objid_frame = [["trial", None],
                        ["trial?some", None],
                        ["trial", "object"],
                        ["trial?some", "object"]
                        ]
    expected_url = ["https://test.FDN.org/trial?limit=all",
                    "https://test.FDN.org/trial?some&limit=all",
                    "https://test.FDN.org/trial?limit=all&frame=object",
                    "https://test.FDN.org/trial?some&limit=all&frame=object"
                    ]
    for n, case in enumerate(test_objid_frame):
        t_url = fdnDCIC.FDN_url(case[0], connection, case[1])
        assert t_url == expected_url[n]


def test_md5():
    md5_keypairs = fdnDCIC.md5('./tests/data_files/keypairs.json')
    assert md5_keypairs == "19d43267b642fe1868e3c136a2ee06f2"


# def test_get_FDN(connection_public):
#     # test the schema retrival with public connection
#     award_schema = fdnDCIC.get_FDN("/profiles/award.json", connection_public, frame="object")
#     assert award_schema['title'] == 'Grant'
#     assert award_schema['properties'].get('description')


def test_get_FDN_mock(connection_public, mocker, returned_award_schema):
    with mocker.patch('wranglertools.fdnDCIC.requests.get') as mocked_get:
        mocked_get.return_value = returned_award_schema
        award_schema = fdnDCIC.get_FDN("/profiles/award.json", connection_public, frame="object")
        assert award_schema['title'] == 'Grant'
        assert award_schema['properties'].get('description')


def test_schema(connection_public):
    vendor_schema = fdnDCIC.FDN_Schema(connection_public, "/profiles/vendor.json")
    assert vendor_schema.uri == "/profiles/vendor.json"
    assert vendor_schema.server == connection_public.server
    assert vendor_schema.properties['title'] == {'description': 'The complete name of the originating lab or vendor. ',
                                                 'title': 'Name',
                                                 'type': 'string'}
    assert vendor_schema.required == ["title"]


def test_filter_and_sort():
    test_list = ["submitted_by", "date_created", "organism", "schema_version", "accession", "uuid", "status",
                 "quality_metric_flags", "notes", "restricted", "file_size", "filename", "alternate_accessions",
                 "content_md5sum", "md5sum", "quality_metric", "files_in_set", "experiments", "experiments_in_set",
                 'dbxrefs', 'references', 'url', 'documents', 'award', '*award', 'lab', '*lab', 'description',
                 'title', '*title', 'name', '*name', 'aliases', '#Field Name:', 'extra_field', 'extra_field_2']
    result_list = ['#Field Name:', '*award', '*lab', '*name', '*title', 'aliases', 'award', 'dbxrefs',
                   'description', 'documents', 'extra_field', 'extra_field_2', 'lab', 'name', 'references',
                   'title', 'url']
    assert result_list == fdnDCIC.filter_and_sort(test_list)


def test_move_to_frond():
    test_list = ['#Field Name:', '*award', '*lab', '*name', '*title', 'aliases', 'award', 'dbxrefs',
                 'description', 'documents', 'extra_field', 'extra_field_2', 'lab', 'name', 'references',
                 'title', 'url']
    result_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description', '*lab', 'lab',
                   '*award', 'award', 'dbxrefs', 'documents', 'extra_field', 'extra_field_2', 'references', 'url']
    assert result_list == fdnDCIC.move_to_frond(test_list)


def test_move_to_end():
    test_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description', '*lab', 'lab',
                 '*award', 'award', 'dbxrefs', 'documents', 'extra_field', 'extra_field_2', 'references', 'url']
    result_list = ['#Field Name:', 'aliases', '*name', 'name', '*title', 'title', 'description', '*lab', 'lab',
                   '*award', 'award', 'extra_field', 'extra_field_2', 'documents', 'references', 'url', 'dbxrefs']
    assert result_list == fdnDCIC.move_to_end(test_list)


def test_switch_fields():
    cases = [
            [['cell_line_tier', 'cell_line', 'SOP_cell_line'], 'Biosource'],
            [['start_coordinate', 'start_location', 'location_description',
              'end_location', 'end_coordinate'], "GenomicRegion"],
            [['experiment_relation.relationship_type', 'experiment_sets|3', 'files', 'average_fragment_size',
              'experiment_sets|1', 'fragment_size_range', 'documents', 'experiment_relation.experiment',
              'experiment_sets|2', 'filesets', 'experiment_sets|0'], "Experiment"]
            ]
    result_list = [['cell_line', 'cell_line_tier', 'SOP_cell_line'],
                   ['location_description', 'start_location', 'end_location', 'start_coordinate', 'end_coordinate'],
                   ['average_fragment_size', 'fragment_size_range', 'files', 'filesets',
                    'experiment_relation.relationship_type', 'experiment_relation.experiment', 'experiment_sets|0',
                    'experiment_sets|1', 'experiment_sets|2', 'experiment_sets|3', 'documents']]
    for n, (a, b) in enumerate(cases):
        assert result_list[n] == fdnDCIC.switch_fields(a, b)


def test_fetch_all_items(connection_public):
    fields = ['#Field Name:', 'aliases', 'name', '*title', 'description', 'lab', 'award', 'url']
    all_vendor_items = fdnDCIC.fetch_all_items('Vendor', fields, connection_public)
    for vendor in all_vendor_items:
        assert len(vendor) == len(fields)
        assert vendor[0].startswith("#")


def test_order_FDN(connection_public):
    import os
    try:
        os.remove("./tests/data_files/Vendor_ordered.xls")
    except:
        pass
    fdnDCIC.order_FDN('./tests/data_files/Vendor.xls', connection_public)
    assert os.path.isfile('./tests/data_files/Vendor.xls')
