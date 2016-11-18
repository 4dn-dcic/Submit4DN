import wranglertools.import_data as imp
import pytest
# test data is in conftest.py


@pytest.mark.file_operation
def test_attachment_image():
    attach = imp.attachment("./tests/data_files/test.jpg")
    assert attach['height'] == 1080
    assert attach['width'] == 1920
    assert attach['download'] == 'test.jpg'
    assert attach['type'] == 'image/jpeg'
    assert attach['href'].startswith('data:image/jpeg;base64')


@pytest.mark.file_operation
def test_attachment_pdf():
    attach = imp.attachment("./tests/data_files/test.pdf")
    assert attach['download'] == 'test.pdf'
    assert attach['type'] == 'application/pdf'
    assert attach['href'].startswith('data:application/pdf;base64')


@pytest.mark.file_operation
def test_attachment_image_wrong_extension():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test_jpeg.tiff")
    assert str(excinfo.value) == 'Wrong extension for image/jpeg: test_jpeg.tiff'


@pytest.mark.file_operation
def test_attachment_text_wrong_extension():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test_txt.pdf")
    assert str(excinfo.value) == 'Wrong extension for text/plain: test_txt.pdf'


@pytest.mark.webtest
def test_attachment_url():
    import os
    attach = imp.attachment("https://wordpress.org/plugins/about/readme.txt")
    assert attach['download'] == 'readme.txt'
    assert attach['type'] == 'text/plain'
    assert attach['href'].startswith('data:text/plain;base64')
    try:
        os.remove('./readme.txt')
    except OSError:
        pass


@pytest.mark.file_operation
def test_attachment_not_accepted():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test.mp3")
    assert str(excinfo.value) == 'Unknown file type for test.mp3'


@pytest.mark.file_operation
def test_reader(vendor_raw_xls_fields):
    readxls = imp.reader('./tests/data_files/Vendor.xls')
    for n, row in enumerate(readxls):
        assert row == vendor_raw_xls_fields[n]


@pytest.mark.file_operation
def test_reader_with_sheetname(vendor_raw_xls_fields):
    readxls = imp.reader('./tests/data_files/Vendor.xls', 'Vendor')
    for n, row in enumerate(readxls):
        assert row == vendor_raw_xls_fields[n]


@pytest.mark.file_operation
def test_reader_wrong_sheetname():
    readxls = imp.reader('./tests/data_files/Vendor.xls', 'Enzyme')
    list_readxls = list(readxls)
    assert list_readxls == []


@pytest.mark.file_operation
def test_cell_value():
    readxls = imp.reader('./tests/data_files/test_cell_values.xls')
    list_readxls = list(readxls)
    assert list_readxls == [['BOOLEAN', '1'], ['NUMBER', '10'], ['DATE', '2016-09-02']]


def test_formatter_gets_ints_correctly():
    assert 6 == imp.data_formatter('6', 'int')
    assert 6 == imp.data_formatter(6, 'integer')


def test_formatter_gets_floats_correctly():
    assert 6.0 == imp.data_formatter('6', 'num')
    assert 7.2456 == imp.data_formatter(7.2456, 'number')


def test_formatter_gets_lists_correctly():
    assert ['1', '2', '3'] == imp.data_formatter('[1,  2 ,3]', 'list')
    assert ['1', '2', '3'] == imp.data_formatter("'[1,2,3]'", 'array')


def test_build_field_empty_is_skipped():
    assert imp.build_field('some_field', '', 'string') is None
    assert imp.build_field('', 'some_data', 'string') is None


def test_build_field_old_stype_field():
    old_style = imp.build_field('some_field:int', "5", None)
    assert old_style == {'some_field': 5}


def test_build_patch_json_removes_empty_fields(file_metadata, file_metadata_type):
    post_json = imp.build_patch_json(file_metadata, file_metadata_type)

    # All the below values exist in file_metadatadd
    assert post_json.get('filesets', None) is None
    assert post_json.get('paired_end', None) is None


def test_build_patch_json_keeps_valid_fields(file_metadata, file_metadata_type):
    post_json = imp.build_patch_json(file_metadata, file_metadata_type)

    assert '/awards/OD008540-01/' == post_json.get('award', None)
    assert 'fastq' == post_json.get('file_format', None)


def test_build_patch_json_embeds_fields(file_metadata, file_metadata_type):
    post_json = imp.build_patch_json(file_metadata, file_metadata_type)
    expected = [{'file': 'testfile.fastq', 'relationship_type': 'related_to'}]
    assert expected == post_json.get('related_files', None)


def test_build_patch_json_join_multiple_embeds_fields(file_metadata, file_metadata_type):
    post_json = imp.build_patch_json(file_metadata, file_metadata_type)
    expected1 = {'experiment': 'test:exp002', 'relationship_type': 'controlled by'}
    expected2 = {'experiment': 'test:exp003', 'relationship_type': 'source for'}
    expected3 = {'experiment': 'test:exp004', 'relationship_type': 'source for'}
    exp_rel = post_json.get('experiment_relation', None)
    assert expected1 in exp_rel
    assert expected2 in exp_rel
    assert expected3 in exp_rel


def test_get_fields_type():
    test_case = ["name", "number:num", "integer:int", "list:array"]
    expected_result = ["string", "num", "int", "array"]
    for i, ix in enumerate(test_case):
        assert imp.get_field_type(ix) == expected_result[i]


def test_get_existing_uuid(connection, mocker, returned_vendor_existing_item):
    post_jsons = [{'uuid': 'some_uuid'},
                  {'accession': 'some_accession'},
                  {'aliases': ['some_acc']},
                  {'@id': 'some_@id'}]
    for post_json in post_jsons:
        with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_existing_item):
            response = imp.get_existing(post_json, connection)
            assert response == returned_vendor_existing_item.json()


@pytest.mark.file_operation
def test_excel_reader_no_update_no_patchall_new_doc_with_attachment(capsys, mocker, connection):
    # test new item submission without patchall update tags and check the return message
    test_insert = './tests/data_files/Document_insert.xls'
    dict_load = {}
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        imp.excel_reader(test_insert, 'Document', False, connection, False, dict_load)
        args = imp.get_existing.call_args
        attach = args[0][0]['attachment']
        assert attach['href'].startswith('data:image/jpeg;base64')


@pytest.mark.file_operation
def test_excel_reader_no_update_no_patchall_new_item(capsys, mocker, connection):
    # test new item submission without patchall update tags and check the return message
    test_insert = './tests/data_files/Vendor_insert.xls'
    dict_load = {}
    message = "This looks like a new row but the update flag wasn't passed, use --update to post new data"
    post_json = {'lab': 'sample-lab',
                 'description': 'Sample description',
                 'award': 'SampleAward',
                 'title': 'Sample Vendor',
                 'url': 'https://www.sample_vendor.com/',
                 'aliases': ['dcic:sample_vendor']}
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        imp.excel_reader(test_insert, 'Vendor', False, connection, False, dict_load)
        args = imp.get_existing.call_args
        assert args[0][0] == post_json
        out, err = capsys.readouterr()
        assert out.strip() == message


@pytest.mark.file_operation
def test_excel_reader_no_update_no_patchall_existing_item(capsys, mocker, connection):
    # test exisiting item submission without patchall update tags and check the return message
    test_insert = "./tests/data_files/Vendor_insert.xls"
    dict_load = {}
    message = "VENDOR: 0 out of 1 posted, 0 errors, 0 patched, 1 not patched (use --patchall to patch)."
    post_json = {'lab': 'sample-lab',
                 'description': 'Sample description',
                 'award': 'SampleAward',
                 'title': 'Sample Vendor',
                 'url': 'https://www.sample_vendor.com/',
                 'aliases': ['dcic:sample_vendor']}
    existing_vendor = {'uuid': 'sample_uuid'}
    with mocker.patch('wranglertools.import_data.get_existing', return_value=existing_vendor):
        imp.excel_reader(test_insert, 'Vendor', False, connection, False, dict_load)
        args = imp.get_existing.call_args
        assert args[0][0] == post_json
        out, err = capsys.readouterr()
        assert out.strip() == message


@pytest.mark.file_operation
def test_excel_reader_no_update_no_patchall_new_experiment_expset_combined(mocker, connection):
    # check if the separated exp set fields in experiments get combined.
    test_insert = './tests/data_files/Exp_HiC_insert.xls'
    dict_load = {}
    post_json = {'experiment_sets': ['a', 'b', 'c', 'd'], 'aliases': ['dcic:test'], 'award': 'test-award',
                 'experiment_type': 'in situ Hi-C', 'lab': 'test-lab', 'filename': 'example.fastq.gz',
                 'biosample': 'test-biosample'}
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        imp.excel_reader(test_insert, 'ExperimentHiC', False, connection, False, dict_load)
        args = imp.get_existing.call_args
        assert args[0][0] == post_json


@pytest.mark.file_operation
def test_excel_reader_update_new_experiment_post_and_file_upload(capsys, mocker, connection):
    # check if the separated exp set fields in experiments get combined
    test_insert = './tests/data_files/Exp_HiC_insert.xls'
    dict_load = {}
    message0 = "calculating md5 sum for file ./tests/data_files/example.fastq.gz"
    message1 = "EXPERIMENTHIC: 1 out of 1 posted, 0 errors, 0 patched."
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('wranglertools.fdnDCIC.new_FDN', return_value=e):
                imp.excel_reader(test_insert, 'ExperimentHiC', True, connection, False, dict_load)
                args = imp.fdnDCIC.new_FDN.call_args
                out, err = capsys.readouterr()
                outlist = [i.strip() for i in out.split('\n') if i is not ""]
                post_json_arg = args[0][2]
                assert post_json_arg['md5sum'] == '8f8cc612e5b2d25c52b1d29017e38f2b'
                assert message0 == outlist[0]
                assert message1 == outlist[1]


@pytest.mark.file_operation
def test_excel_reader_patch_experiment_post_and_file_upload(capsys, mocker, connection):
    # check if the separated exp set fields in experiments get combined
    test_insert = './tests/data_files/Exp_HiC_insert.xls'
    dict_load = {}
    message0 = "calculating md5 sum for file ./tests/data_files/example.fastq.gz"
    message1 = "EXPERIMENTHIC: 1 out of 1 posted, 0 errors, 1 patched."
    existing_exp = {'uuid': 'sample_uuid'}
    e = {'status': 'success',
         '@graph': [{'uuid': 'some_uuid',
                     'upload_credentials': 'old_creds',
                     'accession': 'some_accession'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value=existing_exp):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('wranglertools.fdnDCIC.patch_FDN', return_value=e):
                # mock get upload creds
                with mocker.patch('wranglertools.import_data.get_upload_creds', return_value="new_creds"):
                    imp.excel_reader(test_insert, 'ExperimentHiC', False, connection, True, dict_load)
                    # check for md5sum
                    args = imp.fdnDCIC.patch_FDN.call_args
                    post_json_arg = args[0][2]
                    assert post_json_arg['md5sum'] == '8f8cc612e5b2d25c52b1d29017e38f2b'
                    # check for cred getting updated (from old_creds to new_creds)
                    args_upload = imp.upload_file.call_args
                    updated_post = args_upload[0][0]
                    assert updated_post['@graph'][0]['upload_credentials'] == 'new_creds'
                    # check for output message
                    out, err = capsys.readouterr()
                    outlist = [i.strip() for i in out.split('\n') if i is not ""]
                    assert message0 == outlist[0]
                    assert message1 == outlist[1]


def test_order_sorter(capsys):
    test_list = ["ExperimentHiC", "BiosampleCellCulture", "Biosource", "Document", "Modification",
                 "IndividualMouse", "Biosample", "Lab", "User", "Trouble"]
    ordered_list = ['User', 'Lab', 'Document', 'IndividualMouse', 'Biosource', 'Modification',
                    'BiosampleCellCulture', 'Biosample', 'ExperimentHiC']
    message0 = "WARNING! Trouble sheet(s) are not loaded"
    message1 = '''WARNING! Check the sheet names and the reference list "sheet_order"'''
    assert ordered_list == imp.order_sorter(test_list)
    out, err = capsys.readouterr()
    outlist = [i.strip() for i in out.split('\n') if i is not ""]
    assert message0 == outlist[0]
    assert message1 == outlist[1]
