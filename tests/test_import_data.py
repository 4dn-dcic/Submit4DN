import wranglertools.import_data as imp
import pytest
# test data is in conftest.py


def test_attachment_image():
    attach = imp.attachment("./tests/data_files/test.jpg")
    assert attach['height'] == 1080
    assert attach['width'] == 1920
    assert attach['download'] == 'test.jpg'
    assert attach['type'] == 'image/jpeg'
    assert attach['href'].startswith('data:image/jpeg;base64')


def test_attachment_pdf():
    attach = imp.attachment("./tests/data_files/test.pdf")
    assert attach['download'] == 'test.pdf'
    assert attach['type'] == 'application/pdf'
    assert attach['href'].startswith('data:application/pdf;base64')


def test_attachment_image_wrong_extension():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test_jpeg.tiff")
    assert str(excinfo.value) == 'Wrong extension for image/jpeg: test_jpeg.tiff'


def test_attachment_text_wrong_extension():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test_txt.pdf")
    assert str(excinfo.value) == 'Wrong extension for text/plain: test_txt.pdf'


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


def test_attachment_not_accepted():
    with pytest.raises(ValueError) as excinfo:
        imp.attachment("./tests/data_files/test.mp3")
    assert str(excinfo.value) == 'Unknown file type for test.mp3'


def test_reader(vendor_raw_xls_fields):
    readxls = imp.reader('./tests/data_files/Vendor.xls')
    for n, row in enumerate(readxls):
        assert row == vendor_raw_xls_fields[n]


def test_reader_with_sheetname(vendor_raw_xls_fields):
    readxls = imp.reader('./tests/data_files/Vendor.xls', 'Vendor')
    for n, row in enumerate(readxls):
        assert row == vendor_raw_xls_fields[n]


def test_reader_wrong_sheetname():
    readxls = imp.reader('./tests/data_files/Vendor.xls', 'Enzyme')
    list_readxls = list(readxls)
    assert list_readxls == []


def test_cell_value():
    readxls = imp.reader('./tests/data_files/test_cell_values.xls')
    list_readxls = list(readxls)
    print(list_readxls)
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
                  {'aliases': ['some_uuid']},
                  {'@id': 'some_@id'}]
    for post_json in post_jsons:
        with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_existing_item):
            response = imp.get_existing(post_json, connection)
            assert response == returned_vendor_existing_item.json()
