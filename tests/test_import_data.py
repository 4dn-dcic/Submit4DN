import wranglertools.import_data as imp
import pytest
# test data is in conftest.py


@pytest.mark.file_operation
def test_attachment_from_ftp():
    attach = imp.attachment("ftp://speedtest.tele2.net/1KB.zip")
    assert attach


@pytest.mark.file_operation
def test_md5():
    md5_keypairs = imp.md5('./tests/data_files/keypairs.json')
    assert md5_keypairs == "19d43267b642fe1868e3c136a2ee06f2"


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
def test_attachment_wrong_path():
    # system exit with wrong file path
    with pytest.raises(SystemExit) as excinfo:
        imp.attachment("./tests/data_files/dontexisit.txt")
    assert str(excinfo.value) == "1"


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
        # reader deletes the trailing space in description (at index 3.8)
        if n == 2:
            assert row[8] + " " == vendor_raw_xls_fields[n][8]
        else:
            assert row == vendor_raw_xls_fields[n]


@pytest.mark.file_operation
def test_reader_with_sheetname(vendor_raw_xls_fields):
    readxls = imp.reader('./tests/data_files/Vendor.xls', 'Vendor')
    for n, row in enumerate(readxls):
        # reader deletes the trailing space in description (at index 3.8)
        if n == 2:
            assert row[8] + " " == vendor_raw_xls_fields[n][8]
        else:
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


def test_formatter_gets_ints_correctly_with_gap():
    assert 6 == imp.data_formatter('6 ', 'int')
    assert 6 == imp.data_formatter(6, 'integer')


def test_formatter_gets_floats_correctly():
    assert 6.0 == imp.data_formatter('6', 'num')
    assert 7.2456 == imp.data_formatter(7.2456, 'number')


def test_formatter_gets_lists_correctly():
    assert ['1', '2', '3'] == imp.data_formatter('[1,  2 ,3]', 'list')
    assert ['1', '2', '3'] == imp.data_formatter("'[1,2,3]'", 'array')


def test_formatter_gets_strings_correctly():
    assert "test \t string" == imp.data_formatter("\n\t test \t string\t", 'string')


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
        with mocker.patch('dcicutils.submit_utils.requests.get', return_value=returned_vendor_existing_item):
            response = imp.get_existing(post_json, connection)
            assert response == returned_vendor_existing_item.json()


def test_combine_set_expsets():
    post_json = {"aliases": "sample_expset", "description": "sample description"}
    existing_data = {}
    dict_expsets = {'sample_expset': ['awesome_uuid1', 'awesome_uuid4', 'awesome_uuid5']}
    post_json2, dict_expsets2 = imp.combine_set(post_json, existing_data, "ExperimentSet", dict_expsets)

    response = {'experiments_in_set': ['awesome_uuid4', 'awesome_uuid5', 'awesome_uuid1'],
                'description': 'sample description',
                'aliases': 'sample_expset'}
    assert sorted(post_json2) == sorted(response)
    assert dict_expsets2 == {}


def test_combine_set_replicates_with_existing():
    post_json = {"aliases": "sample_repset", "description": "sample description"}
    existing_data = {"uuid": "sampleuuid", "accession": "sample_accession",
                     'replicate_exps': [{'replicate_exp': 'awesome_uuid', 'bio_rep_no': 1.0, 'tec_rep_no': 6.0},
                                        {'replicate_exp': 'awesome_uuid2', 'bio_rep_no': 2.0, 'tec_rep_no': 1.0}]}
    dict_replicates = {'sample_repset': [{'replicate_exp': 'awesome_uuid1', 'bio_rep_no': 1.0, 'tec_rep_no': 1.0},
                                         {'replicate_exp': 'awesome_uuid3', 'bio_rep_no': 1.0, 'tec_rep_no': 2.0}]}
    post_json2, dict_replicates2 = imp.combine_set(post_json, existing_data, "ExperimentSetReplicate", dict_replicates)

    response = {'replicate_exps': [{'replicate_exp': 'awesome_uuid1', 'bio_rep_no': 1.0, 'tec_rep_no': 1.0},
                                   {'replicate_exp': 'awesome_uuid3', 'bio_rep_no': 1.0, 'tec_rep_no': 2.0},
                                   {'replicate_exp': 'awesome_uuid', 'bio_rep_no': 1.0, 'tec_rep_no': 6.0},
                                   {'replicate_exp': 'awesome_uuid2', 'bio_rep_no': 2.0, 'tec_rep_no': 1.0}],
                'description': 'sample description',
                'aliases': 'sample_repset'}
    assert post_json2 == response
    assert dict_replicates2 == {}


def test_combine_set_expsets_with_existing():
    post_json = {"aliases": "sample_expset", "description": "sample description"}
    existing_data = {"uuid": "sampleuuid", "accession": "sample_accession",
                     "experiments_in_set": ['awesome_uuid1', 'awesome_uuid2']}
    dict_expsets = {'sample_expset': ['awesome_uuid1', 'awesome_uuid4', 'awesome_uuid5']}
    post_json2, dict_expsets2 = imp.combine_set(post_json, existing_data, "ExperimentSet", dict_expsets)

    response = {'experiments_in_set': ['awesome_uuid4', 'awesome_uuid5', 'awesome_uuid2', 'awesome_uuid1'],
                'description': 'sample description',
                'aliases': 'sample_expset'}
    assert sorted(post_json2) == sorted(response)
    assert dict_expsets2 == {}


def test_error_report(connection):
    # There are 3 errors, 2 of them are legit, one needs to be checked afains the all aliases list, and excluded
    err_dict = {"title": "Unprocessable Entity",
                "status": "error",
                "errors": [
                  {"name": ["protocol_documents", 0],
                   "description": "'dcic:insituhicagar' not found", "location": "body"},
                  {"name": ["age"],
                   "description": "'at' is not of type 'number'", "location": "body"},
                  {"name": ["sex"],
                   "description": "'green' is not one of ['male', 'female', 'unknown', 'mixed']", "location": "body"}],
                "code": 422,
                "@type": ["ValidationFailure", "Error"],
                "description": "Failed validation"}
    rep = imp.error_report(err_dict, "Vendor", ['dcic:insituhicagar'], connection)
    message = '''
ERROR vendor                  Field 'age': 'at' is not of type 'number'
ERROR vendor                  Field 'sex': 'green' is not one of ['male', 'female', 'unknown', 'mixed']
'''
    assert rep.strip() == message.strip()


def test_error_conflict_report(connection):
    # There is one conflict error
    err_dict = {"title": "Conflict",
                "status": "error",
                "description": "There was a conflict when trying to complete your request.",
                "code": 409,
                "detail": "Keys conflict: [('award:name', '1U54DK107981-01')]",
                "@type": ["HTTPConflict", "Error"]}
    rep = imp.error_report(err_dict, "Vendor", ['dcic:insituhicagar'], connection)
    message = "ERROR vendor                  Field 'name': '1U54DK107981-01' already exists, please contact DCIC"
    assert rep.strip() == message.strip()


def test_fix_attribution(connection):
    post_json = {'field': 'value', 'field2': 'value2'}
    result_json = imp.fix_attribution('some_sheet', post_json, connection)
    assert result_json['lab'] == 'test_lab'
    assert result_json['award'] == 'test_award'


# these tests will be replaced with dryrun tests

@pytest.mark.file_operation
def test_excel_reader_no_update_no_patchall_new_doc_with_attachment(capsys, mocker, connection):
    # test new item submission without patchall update tags and check the return message
    test_insert = './tests/data_files/Document_insert.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    with mocker.patch('wranglertools.import_data.remove_deleted', return_value={}):
        imp.excel_reader(test_insert, 'Document', False, connection, False, all_aliases,
                         dict_load, dict_rep, dict_set, True)
        args = imp.remove_deleted.call_args
        attach = args[0][0]['attachment']
        assert attach['href'].startswith('data:image/jpeg;base64')

# @pytest.mark.file_operation
# def test_excel_reader_no_update_no_patchall_new_item(capsys, mocker, connection):
#     # test new item submission without patchall update tags and check the return message
#     test_insert = './tests/data_files/Vendor_insert.xls'
#     dict_load = {}
#     dict_rep = {}
#     dict_set = {}
#     message = "This looks like a new row but the update flag wasn't passed, use --update to post new data"
#     post_json = {'lab': 'sample-lab',
#                  'description': 'Sample description',
#                  'award': 'SampleAward',
#                  'title': 'Sample Vendor',
#                  'url': 'https://www.sample_vendor.com/',
#                  'aliases': ['dcic:sample_vendor']}
#     with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
#         imp.excel_reader(test_insert, 'Vendor', False, connection, False, dict_load, dict_rep, dict_set, True)
#         args = imp.get_existing.call_args
#         assert args[0][0] == post_json
#         out = capsys.readouterr()[0]
#         assert out.strip() == message


# @pytest.mark.file_operation
# def test_excel_reader_no_update_no_patchall_existing_item(capsys, mocker, connection):
#     # test exisiting item submission without patchall update tags and check the return message
#     test_insert = "./tests/data_files/Vendor_insert.xls"
#     dict_load = {}
#     dict_rep = {}
#     dict_set = {}
#     message = "VENDOR(1)                  :  0 posted / 0 not posted       0 patched / 1 not patched, 0 errors"
#     post_json = {'lab': 'sample-lab',
#                  'description': 'Sample description',
#                  'award': 'SampleAward',
#                  'title': 'Sample Vendor',
#                  'url': 'https://www.sample_vendor.com/',
#                  'aliases': ['dcic:sample_vendor']}
#     existing_vendor = {'uuid': 'sample_uuid'}
#     with mocker.patch('wranglertools.import_data.get_existing', return_value=existing_vendor):
#         imp.excel_reader(test_insert, 'Vendor', False, connection, False, dict_load, dict_rep, dict_set, True)
#         args = imp.get_existing.call_args
#         assert args[0][0] == post_json
#         out = capsys.readouterr()[0]
#         assert out.strip() == message


@pytest.mark.file_operation
def test_excel_reader_post_ftp_file_upload(capsys, mocker, connection):
    test_insert = './tests/data_files/Ftp_file_test_md5.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    message0_1 = "INFO: Attempting to download file from this url to your computer before upload "
    message0_2 = "ftp://speedtest.tele2.net/1KB.zip"
    message1 = "FILECALIBRATION(1)         :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid', '@id': 'some_uuid'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
                imp.excel_reader(test_insert, 'FileCalibration', True, connection, False, all_aliases,
                                 dict_load, dict_rep, dict_set, True)
                args = imp.submit_utils.new_FDN.call_args
                out = capsys.readouterr()[0]
                outlist = [i.strip() for i in out.split('\n') if i.strip()]
                post_json_arg = args[0][2]
                assert post_json_arg['md5sum'] == '0f343b0931126a20f133d67c2b018a3b'
                assert message0_1 + message0_2 == outlist[0]
                assert message1 == outlist[1]


@pytest.mark.file_operation
def test_excel_reader_post_ftp_file_upload_no_md5(capsys, mocker, connection):
    test_insert = './tests/data_files/Ftp_file_test.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    message0 = "WARNING: File not uploaded"
    message1 = "Please add original md5 values of the files"
    message2 = "FILECALIBRATION(1)         :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid', '@id': 'some_uuid'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
                imp.excel_reader(test_insert, 'FileCalibration', True, connection, False, all_aliases,
                                 dict_load, dict_rep, dict_set, True)
                out = capsys.readouterr()[0]
                outlist = [i.strip() for i in out.split('\n') if i.strip()]
                assert message0 == outlist[0]
                assert message1 == outlist[1]
                assert message2 == outlist[2]


@pytest.mark.file_operation
def test_excel_reader_update_new_experiment_post_and_file_upload(capsys, mocker, connection):
    test_insert = './tests/data_files/Exp_HiC_insert.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    message0 = "calculating md5 sum for file ./tests/data_files/example.fastq.gz"
    message1 = "EXPERIMENTHIC(1)           :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid', '@id': 'some_uuid'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
                imp.excel_reader(test_insert, 'ExperimentHiC', True, connection, False, all_aliases,
                                 dict_load, dict_rep, dict_set, True)
                args = imp.submit_utils.new_FDN.call_args
                out = capsys.readouterr()[0]
                outlist = [i.strip() for i in out.split('\n') if i is not ""]
                post_json_arg = args[0][2]
                assert post_json_arg['md5sum'] == '8f8cc612e5b2d25c52b1d29017e38f2b'
                assert message0 == outlist[0]
                assert message1 == outlist[1]


# a weird test that has filename in an experiment
# needs to change
@pytest.mark.file_operation
def test_excel_reader_patch_experiment_post_and_file_upload(capsys, mocker, connection):
    test_insert = './tests/data_files/Exp_HiC_insert.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    message0 = "calculating md5 sum for file ./tests/data_files/example.fastq.gz"
    message1 = "EXPERIMENTHIC(1)           :  0 posted / 0 not posted       1 patched / 0 not patched, 0 errors"
    existing_exp = {'uuid': 'sample_uuid', 'status': "uploading"}
    e = {'status': 'success',
         '@graph': [{'uuid': 'some_uuid',
                     '@id': 'some_uuid',
                     'upload_credentials': 'old_creds',
                     'accession': 'some_accession'}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value=existing_exp):
        # mock upload file and skip
        with mocker.patch('wranglertools.import_data.upload_file', return_value={}):
            # mock posting new items
            with mocker.patch('dcicutils.submit_utils.patch_FDN', return_value=e):
                # mock get upload creds
                with mocker.patch('wranglertools.import_data.get_upload_creds', return_value="new_creds"):
                    imp.excel_reader(test_insert, 'ExperimentHiC', False, connection, True, all_aliases,
                                     dict_load, dict_rep, dict_set, True)
                    # check for md5sum
                    args = imp.submit_utils.patch_FDN.call_args
                    post_json_arg = args[0][2]
                    assert post_json_arg['md5sum'] == '8f8cc612e5b2d25c52b1d29017e38f2b'
                    # check for cred getting updated (from old_creds to new_creds)
                    args_upload = imp.upload_file.call_args
                    updated_post = args_upload[0][0]
                    assert updated_post['@graph'][0]['upload_credentials'] == 'new_creds'
                    # check for output message
                    out = capsys.readouterr()[0]
                    outlist = [i.strip() for i in out.split('\n') if i is not ""]
                    assert message0 == outlist[0]
                    assert message1 == outlist[1]


@pytest.mark.file_operation
def test_excel_reader_update_new_filefastq_post(capsys, mocker, connection):
    test_insert = './tests/data_files/File_fastq_insert.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {}
    all_aliases = {}
    message = "FILEFASTQ(1)               :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid', '@id': 'some_uuid'}]}
    final_post = {'aliases': ['dcic:test_alias'],
                  'lab': 'test-lab',
                  'award': 'test-award',
                  'file_format': 'fastq'}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock posting new items
        with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
            imp.excel_reader(test_insert, 'FileFastq', True, connection, False, all_aliases,
                             dict_load, dict_rep, dict_set, True)
            args = imp.submit_utils.new_FDN.call_args
            out = capsys.readouterr()[0]
            print([i for i in args])
            assert message == out.strip()
            assert args[0][2] == final_post


@pytest.mark.file_operation
def test_excel_reader_update_new_replicate_set_post(capsys, mocker, connection):
    test_insert = './tests/data_files/Exp_Set_Replicate_insert.xls'
    dict_load = {}
    dict_rep = {'sample_repset': [{'replicate_exp': 'awesome_uuid', 'bio_rep_no': 1.0, 'tec_rep_no': 1.0}]}
    dict_set = {}
    all_aliases = {}
    message = "EXPERIMENTSETREPLICATE(1)  :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'sample_repset', '@id': 'sample_repset'}]}
    final_post = {'aliases': ['sample_repset'],
                  'replicate_exps': [{'bio_rep_no': 1.0, 'tec_rep_no': 1.0, 'replicate_exp': 'awesome_uuid'}],
                  'award': 'test_award', 'lab': 'test_lab'}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
            imp.excel_reader(test_insert, 'ExperimentSetReplicate', True, connection, False, all_aliases,
                             dict_load, dict_rep, dict_set, True)
            args = imp.submit_utils.new_FDN.call_args
            out = capsys.readouterr()[0]
            assert message == out.strip()
            assert args[0][2] == final_post


@pytest.mark.file_operation
def test_excel_reader_update_new_experiment_set_post(capsys, mocker, connection):
    test_insert = './tests/data_files/Exp_Set_insert.xls'
    dict_load = {}
    dict_rep = {}
    dict_set = {'sample_expset': ['awesome_uuid']}
    all_aliases = {}
    message = "EXPERIMENTSET(1)           :  1 posted / 0 not posted       0 patched / 0 not patched, 0 errors"
    e = {'status': 'success', '@graph': [{'uuid': 'sample_expset', '@id': 'sample_expset'}]}
    final_post = {'aliases': ['sample_expset'], 'experiments_in_set': ['awesome_uuid'],
                  'award': 'test_award', 'lab': 'test_lab'}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock upload file and skip
        with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
            imp.excel_reader(test_insert, 'ExperimentSet', True, connection, False, all_aliases,
                             dict_load, dict_rep, dict_set, True)
            args = imp.submit_utils.new_FDN.call_args
            out = capsys.readouterr()[0]
            assert message == out.strip()
            print(args[0][2])
            assert args[0][2] == final_post


@pytest.mark.file_operation
def test_user_workflow_reader_wfr_post(capsys, mocker, connection):
    test_insert = './tests/data_files/Pseudo_wfr_insert.xls'
    sheet_name = 'user_workflow_1'

    message = "USER_WORKFLOW_1(1)         :  1 posted / 0 not posted       - patched / - not patched, 0 errors"
    e = {'status': 'SUCCEEDED'}
    final_post = {'wfr_meta':
                  {'lab': 'test_lab',
                   'submitted_by': 'test_user',
                   'description': 'testing testing',
                   'award': 'test_award',
                   'aliases': [u'dcic:test_wfrs0004']},
                  'parameters': {},
                  'args': {},
                  'app_name': None,
                  'metadata_only': True,
                  'output_files': [
                      {'uuid': 'b0aaf32c-58de-475a-a222-3f16d3cb68f4',
                       'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                       'workflow_argument_name': 'annotated_bam',
                       'object_key': '4DNFIVQPE4WT.bam'},
                      {'uuid': '0292e08e-facf-4a16-a94e-59606f2bfc71',
                       'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                       'workflow_argument_name':
                       'filtered_pairs',
                       'object_key': '4DNFIGOJW3XZ.pairs.gz'}],
                  'config': {},
                  'workflow_uuid': '023bfb3e-9a8b-42b9-a9d4-216079526f68',
                  'input_files': [{'uuid': '4a6d10ee-2edb-4402-a98f-0edb1d58f5e9',
                                   'bucket_name': 'elasticbeanstalk-fourfront-webdev-files',
                                   'workflow_argument_name': 'chromsize',
                                   'object_key': '4DNFI823LSII.chrom.sizes'},
                                  {'uuid': ['11c12207-6684-4346-9038-e7819dfde4e5',
                                            '4d55623a-1698-44c2-b111-1aa1379edc57'],
                                   'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                                   'workflow_argument_name': 'input_bams',
                                   'object_key': ['4DNFIYI7YMVU.bam', '4DNFIPMZQNF5.bam']}]}
    # mock fetching existing info, return None
    with mocker.patch('wranglertools.import_data.get_existing', return_value={}):
        # mock formating files
        with mocker.patch('wranglertools.import_data.format_file',
                          side_effect=[
                              {'bucket_name': 'elasticbeanstalk-fourfront-webdev-files',
                               'workflow_argument_name': 'chromsize', 'object_key': '4DNFI823LSII.chrom.sizes',
                               'uuid': '4a6d10ee-2edb-4402-a98f-0edb1d58f5e9'},
                              {'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                               'workflow_argument_name': 'input_bams',
                               'object_key': ['4DNFIYI7YMVU.bam', '4DNFIPMZQNF5.bam'],
                               'uuid': ['11c12207-6684-4346-9038-e7819dfde4e5',
                                        '4d55623a-1698-44c2-b111-1aa1379edc57']},
                              {'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                               'workflow_argument_name': 'annotated_bam', 'object_key': '4DNFIVQPE4WT.bam',
                               'uuid': 'b0aaf32c-58de-475a-a222-3f16d3cb68f4'},
                              {'bucket_name': 'elasticbeanstalk-fourfront-webdev-wfoutput',
                               'workflow_argument_name': 'filtered_pairs', 'object_key': '4DNFIGOJW3XZ.pairs.gz',
                               'uuid': '0292e08e-facf-4a16-a94e-59606f2bfc71'}
                            ]):
            with mocker.patch('dcicutils.submit_utils.new_FDN', return_value=e):
                imp.user_workflow_reader(test_insert, sheet_name, connection)
                args = imp.submit_utils.new_FDN.call_args
                out = capsys.readouterr()[0]
                print([i for i in args])
                assert message == out.strip()
                for a_key in args[0][2]:
                    assert args[0][2][a_key] == final_post[a_key]


def test_order_sorter(capsys):
    test_list = ["ExperimentHiC", "BiosampleCellCulture", "Biosource", "Document", "Modification",
                 "IndividualMouse", "Biosample", "Lab", "User", "Trouble"]
    ordered_list = ['User', 'Lab', 'Document', 'IndividualMouse', 'Modification', 'Biosource',
                    'BiosampleCellCulture', 'Biosample', 'ExperimentHiC']
    message0 = "WARNING! Trouble sheet(s) are not loaded"
    message1 = '''WARNING! Check the sheet names and the reference list "sheet_order"'''
    assert ordered_list == imp.order_sorter(test_list)
    out = capsys.readouterr()[0]
    outlist = [i.strip() for i in out.split('\n') if i is not ""]
    import sys
    if (sys.version_info > (3, 0)):
        assert message0 in outlist[0]
        assert message1 in outlist[1]


@pytest.mark.file_operation
def test_loadxl_cycle(capsys, mocker, connection):
    patch_list = {'Experiment': [{"uuid": "some_uuid"}]}
    e = {'status': 'success', '@graph': [{'uuid': 'some_uuid'}]}
    message = "EXPERIMENT(phase2): 1 items patched."
    with mocker.patch('dcicutils.submit_utils.patch_FDN', return_value=e):
        imp.loadxl_cycle(patch_list, connection)
        out = capsys.readouterr()[0]
        assert message == out.strip()


@pytest.mark.file_operation
def test_cabin_cross_check_key_error(connection_public):
    with pytest.raises(SystemExit) as excinfo:
        imp.cabin_cross_check(connection_public, False, False, './tests/data_files/Exp_Set_insert.xls', False)
    assert str(excinfo.value) == "1"


@pytest.mark.file_operation
def test_cabin_cross_check_dryrun(connection_fake, capsys):
    imp.cabin_cross_check(connection_fake, False, False, './tests/data_files/Exp_Set_insert.xls', False)
    out = capsys.readouterr()[0]
    message = '''
Running on:       https://data.4dnucleome.org/
Submitting User:  test@test.test
Submitting Lab:   test_lab
Submitting Award: test_award

##############   DRY-RUN MODE   ################
Since there are no '--update' and/or '--patchall' arguments, you are running the DRY-RUN validation
The validation will only check for schema rules, but not for object relations
##############   DRY-RUN MODE   ################
'''
    assert out.strip() == message.strip()


def test_get_collections(connection_public):
    all_cols = imp.get_collections(connection_public)
    assert len(all_cols) > 10


def test_get_all_aliases():
    wb = "./tests/data_files/Exp_Set_insert.xls"
    sheet = ["ExperimentSet"]
    my_aliases = {'sample_expset': 'ExperimentSet'}
    all_aliases = imp.get_all_aliases(wb, sheet)
    assert my_aliases == all_aliases


@pytest.fixture
def fields2type():
    return {
        'biosource': 'array of Item:Biosource',
        'biosample': 'Item:Biosample',
        'description': 'string',
        'biosample_quantity': 'number',
        'experiment_relations.relationship_type': 'string',
        'experiment_relations.experiment': 'Item:Experiment',
        'average_fragment_size': 'integer',
        'aliases': 'array of string'
    }


@pytest.fixture
def json2post():
    return {
        'biosource': 'dcic:imr90',
        '#biosample': 'dcic:biosamp',
        'description': '',
        'biosample_quantity': 1,
        'aliases': 'dcic:test'
    }


@pytest.fixture
def alias_dict():
    return {
        'test:alias1': 'Biosource',
        'test:alias2': 'Biosource',
    }


def test_get_f_type(fields2type):
    fields = fields2type.keys()
    for f in fields:
        assert imp.get_f_type(f, fields2type) == fields2type[f]
    assert not imp.get_f_type('nonexistent field', fields2type)


def test_add_to_mistype_message_3_words():
    words = ['eeny', 'meeny', 'moe']
    msg = imp.add_to_mistype_message(*words, msg='')
    assert msg == "ERROR: 'eeny' is TYPE meeny - THE REQUIRED TYPE IS moe\n"


def test_add_to_mistype_message_w_msg():
    words = ['eeny', 'meeny', 'moe']
    msg1 = "ERROR: 'eeny' is TYPE meeny - THE REQUIRED TYPE IS moe\n"
    msg2 = imp.add_to_mistype_message(*words, msg=msg1)
    assert msg2 == msg1 * 2


def test_add_to_mistype_message_2_words():
    words = ['eeny', 'meeny', '']
    msg = imp.add_to_mistype_message(*words, msg='')
    assert msg == "ERROR: 'eeny' is TYPE meeny - THE REQUIRED TYPE IS \n"


def test_add_to_mistype_message_not_found():
    words = ['eeny', 'HTTPNotFound', 'moe']
    msg = imp.add_to_mistype_message(*words, msg='')
    assert msg == "ERROR: 'eeny' is NOT FOUND - THE REQUIRED TYPE IS moe\n"


def test_validate_item_in_alias_dict_correct_type(alias_dict, connection):
    item = 'test:alias1'
    msg = imp.validate_item([item], 'Biosource', alias_dict, connection)
    assert not msg


def test_validate_item_in_alias_dict_incorrect_type(alias_dict, connection):
    item = 'test:alias1'
    msg = imp.validate_item([item], 'Biosample', alias_dict, connection)
    assert msg.startswith("ERROR")


def test_validate_multiple_items_in_alias_dict_correct_type(alias_dict, connection):
    items = ['test:alias1', 'test:alias2']
    msg = imp.validate_item(items, 'Biosource', alias_dict, connection)
    assert not msg


def test_validate_multiple_items_in_alias_dict_incorrect_type(alias_dict, connection):
    items = ['test:alias1', 'test:alias2']
    msg = imp.validate_item(items, 'Biosample', alias_dict, connection)
    lns = msg.split('\n')
    assert len(lns) == 2
    for l in lns:
        assert l.startswith("ERROR")


def test_validate_item_not_in_alias_dict_alias_indb(mocker, connection):
    item = 'test:alias1'
    with mocker.patch('dcicutils.submit_utils.get_FDN',
                      return_value={'@type': ['Biosource']}):
        msg = imp.validate_item([item], 'Biosource', {}, connection)
        assert not msg


def test_validate_item_not_in_alias_dict_alias_indb_long_name(mocker, connection):
    item = '/labs/test-lab'
    with mocker.patch('dcicutils.submit_utils.get_FDN',
                      return_value={'@type': ['Lab']}):
        msg = imp.validate_item([item], 'Lab', {}, connection)
        assert not msg


def test_validate_item_not_in_alias_dict_alias_not_indb(mocker, connection):
    item = 'test:alias1'
    with mocker.patch('dcicutils.submit_utils.get_FDN',
                      return_value={'@type': ['HTTPNotFound']}):
        msg = imp.validate_item([item], 'Biosource', {}, connection)
        assert msg.startswith("ERROR")


def test_validate_item_one_in_one_not_in_db(mocker, connection):
    items = ['test:alias1', 'test:alias2']
    with mocker.patch('dcicutils.submit_utils.get_FDN',
                      side_effect=[{'@type': ['HTTPNotFound']},
                                   {'@type': ['Biosource', 'Item']}]):
        msg = imp.validate_item(items, 'Biosource', {}, connection)
        assert msg.startswith("ERROR")
        assert 'test:alias1' in msg
        assert 'test:alias2' not in msg


def test_validate_string_are_strings_not_alias(alias_dict):
    s = ['test_string', 'test_string2']
    msg = imp.validate_string(s, alias_dict)
    assert not msg


def test_validate_string_one_string_is_alias(alias_dict):
    s = ['test:alias1', 'test_string2']
    msg = imp.validate_string(s, alias_dict)
    assert msg == 'WARNING: ALIAS test:alias1 USED IN string Field'


def test_convert_to_array_is_array():
    arrstr = 'eeny, meeny,moe'
    result = imp._convert_to_array(arrstr, True)
    assert len(result) == 3


def test_convert_to_array_is_string():
    s = ' whatsup,! '
    result = imp._convert_to_array(s, False)
    assert len(result) == 1
    assert result[0] == s.strip()


def test_validate_field_single_string(mocker, connection, alias_dict):
    fdata = 'test_string'
    ftype = 'string'
    with mocker.patch('wranglertools.import_data.validate_string',
                      return_value=''):
        assert not imp.validate_field(fdata, ftype, alias_dict, connection)


def test_validate_field_array_of_string(mocker, connection, alias_dict):
    fdata = 'test_string'
    ftype = 'array of string'
    with mocker.patch('wranglertools.import_data.validate_string',
                      return_value=''):
        assert not imp.validate_field(fdata, ftype, alias_dict, connection)


def test_validate_field_single_item(mocker, connection, alias_dict):
    fdata = 'test_item'
    ftype = 'Item:Biosource'
    with mocker.patch('wranglertools.import_data.validate_item',
                      return_value=''):
        assert not imp.validate_field(fdata, ftype, alias_dict, connection)


def test_validate_field_array_of_items(mocker, connection, alias_dict):
    fdata = 'test_item'
    ftype = 'array of Item:Biosource'
    with mocker.patch('wranglertools.import_data.validate_item',
                      return_value=''):
        assert not imp.validate_field(fdata, ftype, alias_dict, connection)


def test_validate_field_array_of_embedded_objects(mocker, connection, alias_dict):
    fdata = 'test_item'
    ftype = 'array of embedded objects, Item:File'
    with mocker.patch('wranglertools.import_data.validate_item',
                      return_value=''):
        assert not imp.validate_field(fdata, ftype, alias_dict, connection)


def test_pre_validate_json(mocker, json2post, fields2type, alias_dict, connection):
    with mocker.patch('wranglertools.import_data.validate_field',
                      side_effect=['', '']):
        assert not imp.pre_validate_json(json2post, fields2type, alias_dict, connection)


@pytest.fixture
def fastq_sheet():
    return [
        ['#Field Name:', 'aliases', 'description', '*file_format', 'paired_end', 'related_files.relationship_type',
         'related_files.file', 'read_length', 'instrument'],
        ['', 'test:file1', '', 'fastq', '1', '', '', '75', ''],
        ['', 'test:file2', '', 'fastq', '2', 'paired with', 'test:file1', '75', ''],
        ['', 'test:file3', '', 'fastq', '1', 'paired with', 'test:file4', '75', ''],
        ['', 'test:file4', '', 'fastq', '2', '', '', '75', ''],
        ['', 'test:file5', '', 'fastq', '1', 'paired with', 'test:file4', '75', ''],
        ['', 'test:file6', '', 'fastq', '1', '', '', '75', ''],
        ['', 'test:file7', '', 'fastq', '', 'paired with', 'test:file6', '75', ''],
        ['', 'test:file8', '', 'fastq', '1', '', '', '75', ''],
        ['', 'test:file9', '', 'fastq', '2', 'paired with', '44DNFIYI7YMVU', '75', ''],
        ['', 'test:file10', '', 'fastq', '2', 'paired with', 'test:file8', 'paired with', 'test:file7', '75', ''],
        ['', '', 'File with no alias', 'fastq', '1', '', '', '75', ''],
        ['', '', 'Another File with no alias', 'fastq', '1', '', '', '75', '']
    ]


def test_file_pair_chk_good_pairs(fastq_sheet):
    rows = iter(fastq_sheet[0:5])
    report = imp.check_file_pairing(rows)
    assert not report


def test_file_pair_chk_mulitple_pairing(fastq_sheet):
    tochk = fastq_sheet[3:6]
    tochk.insert(0, fastq_sheet[0])
    rows = iter(tochk)
    report = imp.check_file_pairing(rows)
    assert 'test:file5' in report
    assert 'MISMATCH' in report
    assert 'attempting to alter existing pair' in report['test:file5'][0]


def test_file_pair_chk_2_paired_with(fastq_sheet):
    rows = iter([fastq_sheet[0], fastq_sheet[10]])
    report = imp.check_file_pairing(rows)
    assert 'test:file10' in report
    assert 'single row with multiple paired_with values' in report['test:file10']


def test_file_pair_chk_pairing_w_no_paired_end(fastq_sheet):
    tochk = fastq_sheet[6:8]
    tochk.insert(0, fastq_sheet[0])
    rows = iter(tochk)
    report = imp.check_file_pairing(rows)
    assert 'test:file7' in report
    assert 'missing paired_end number' in report['test:file7']


def test_file_pair_chk_pairing_w_paired_file_not_alias(fastq_sheet):
    tochk = fastq_sheet[8:10]
    tochk.insert(0, fastq_sheet[0])
    rows = iter(tochk)
    report = imp.check_file_pairing(rows)
    assert 'test:file8' in report
    assert 'no paired file but paired_end = 1' in report['test:file8']
    assert 'test:file9' in report
    assert 'paired with not found 44DNFIYI7YMVU' in report['test:file9']


def test_file_pair_chk_pairing_w_no_alias(fastq_sheet):
    rows = iter([fastq_sheet[0], fastq_sheet[11], fastq_sheet[12]])
    report = imp.check_file_pairing(rows)
    assert 'unaliased' in report
    assert len(report['unaliased']) == 1
    assert "alias missing - can't check file pairing" in report['unaliased']


def test_file_pair_chk_sheets_w_no_aliases_col_skipped():
    rows = iter([['#Field Name:', '*file_format', 'paired_end',
                 'related_files.relationship_type', 'related_files.file'],
                ['', 'fastq', '1', 'paired with', 'test:file2']])
    report = imp.check_file_pairing(rows)
    assert 'NO GO' in report
    assert report['NO GO'] == 'Can only check file pairing by aliases'
