import wranglertools.fdnDCIC as fdnDCIC
import json
import pytest
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
    assert isinstance(key.server, str)
    assert isinstance(key.authpw, str)
    assert isinstance(key.authid, str)


@pytest.mark.file_operation
def test_key_file():
    key = fdnDCIC.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert isinstance(key.server, str)
    assert isinstance(key.authpw, str)
    assert isinstance(key.authid, str)


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


@pytest.mark.file_operation
def test_md5():
    md5_keypairs = fdnDCIC.md5('./tests/data_files/keypairs.json')
    assert md5_keypairs == "19d43267b642fe1868e3c136a2ee06f2"


@pytest.mark.webtest
def test_get_FDN(connection_public):
    # test the schema retrival with public connection
    award_schema = fdnDCIC.get_FDN("/profiles/award.json", connection_public, frame="object")
    assert award_schema['title'] == 'Grant'
    assert award_schema['properties'].get('description')


def test_get_FDN_mock(connection, mocker, returned_award_schema):
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_award_schema):
        award_schema = fdnDCIC.get_FDN("/profiles/award.json", connection, frame="object")
        assert award_schema['title'] == 'Grant'
        assert award_schema['properties'].get('description')


def test_schema_mock(connection, mocker, returned_vendor_schema):
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_schema):
        vendor_schema = fdnDCIC.FDN_Schema(connection, "/profiles/vendor.json")
        assert vendor_schema.uri == "/profiles/vendor.json"
        assert vendor_schema.server == connection.server
        schema_title = {'description': 'The complete name of the originating lab or vendor. ',
                        'title': 'Name',
                        'type': 'string'}
        assert vendor_schema.properties['title'] == schema_title
        assert vendor_schema.required == ["title"]


def test_new_FDN_mock_post_item_dict(connection, mocker, returned_post_new_vendor):
    post_item = {'aliases': ['dcic:vendor_test'], 'description': 'test description', 'title': 'Test Vendor',
                 'url': 'http://www.test_vendor.com'}
    with mocker.patch('wranglertools.fdnDCIC.requests.post', return_value=returned_post_new_vendor):
        fdnDCIC.new_FDN(connection, 'Vendor', post_item)
        url = 'https://data.4dnucleome.org/Vendor'
        auth = ('testkey', 'testsecret')
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        data = json.dumps(post_item)
        args = fdnDCIC.requests.post.call_args
        assert args[0][0] == url
        assert args[1]['auth'] == auth
        assert args[1]['headers'] == headers
        assert args[1]['data'] == data


def test_new_FDN_mock_post_item_str(connection, mocker, returned_post_new_vendor):
    post_item = {'aliases': ['dcic:vendor_test'], 'description': 'test description', 'title': 'Test Vendor',
                 'url': 'http://www.test_vendor.com'}
    data = json.dumps(post_item)
    with mocker.patch('wranglertools.fdnDCIC.requests.post', return_value=returned_post_new_vendor):
        fdnDCIC.new_FDN(connection, 'Vendor', data)
        url = 'https://data.4dnucleome.org/Vendor'
        auth = ('testkey', 'testsecret')
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        data = json.dumps(post_item)
        args = fdnDCIC.requests.post.call_args
        assert args[0][0] == url
        assert args[1]['auth'] == auth
        assert args[1]['headers'] == headers
        assert args[1]['data'] == data


def test_patch_FDN_mock_post_item_dict(connection, mocker, returned__patch_vendor):
    patch_item = {'aliases': ['dcic:vendor_test'], 'description': 'test description new'}
    obj_id = 'some_uuid'
    with mocker.patch('wranglertools.fdnDCIC.requests.patch', return_value=returned__patch_vendor):
        fdnDCIC.patch_FDN(obj_id, connection, patch_item)
        url = 'https://data.4dnucleome.org/some_uuid'
        auth = ('testkey', 'testsecret')
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        data = json.dumps(patch_item)
        args = fdnDCIC.requests.patch.call_args
        assert args[0][0] == url
        assert args[1]['auth'] == auth
        assert args[1]['headers'] == headers
        assert args[1]['data'] == data


def test_patch_FDN_mock_post_item_str(connection, mocker, returned__patch_vendor):
    patch_item = {'aliases': ['dcic:vendor_test'], 'description': 'test description new'}
    data = json.dumps(patch_item)
    obj_id = 'some_uuid'
    with mocker.patch('wranglertools.fdnDCIC.requests.patch', return_value=returned__patch_vendor):
        fdnDCIC.patch_FDN(obj_id, connection, data)
        url = 'https://data.4dnucleome.org/some_uuid'
        auth = ('testkey', 'testsecret')
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        args = fdnDCIC.requests.patch.call_args
        assert args[0][0] == url
        assert args[1]['auth'] == auth
        assert args[1]['headers'] == headers
        assert args[1]['data'] == data


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


def test_fetch_all_items_mock(connection, mocker, returned_vendor_items):
    fields = ['#Field Name:', 'aliases', 'name', '*title', 'description', 'lab', 'award', 'url']
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_items):
        all_vendor_items = fdnDCIC.fetch_all_items('Vendor', fields, connection)
        for vendor in all_vendor_items:
            assert len(vendor) == len(fields)
            assert vendor[0].startswith("#")


def xls_to_list(xls_file, sheet):
    import xlrd
    return_list = []
    wb = xlrd.open_workbook(xls_file)
    read_sheet = wb.sheet_by_name(sheet)
    cols = read_sheet.ncols
    rows = read_sheet.nrows
    for row_idx in range(rows):
        row_val = []
        for col_idx in range(cols):
            cell_value = str(read_sheet.cell(row_idx, col_idx))

            row_val.append(cell_value)
        return_list.append(row_val)
    return return_list


@pytest.mark.file_operation
def test_order_FDN_mock(connection, mocker, returned_vendor_items):
    vendor_file = './tests/data_files/Vendor.xls'
    ordered_file = './tests/data_files/Vendor_ordered.xls'
    ref_file = './tests/data_files/Vendor_ordered reference.xls'
    import os
    try:
        os.remove(ordered_file)
    except OSError:
        pass

    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_items):
        fdnDCIC.order_FDN(vendor_file, connection)
        assert os.path.isfile(ordered_file)
    ord_list = xls_to_list(ordered_file, "Vendor")
    ref_list = xls_to_list(ref_file, "Vendor")
    assert ord_list == ref_list
    try:
        os.remove(ordered_file)
    except OSError:
        pass
