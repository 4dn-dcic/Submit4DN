import pytest
import import_data as imp

# test data is in conftest.py

def test_formatter_gets_ints_correctly():
    assert 6 == imp.data_formatter('6', 'int')
    assert 6 == imp.data_formatter(6, 'integer')


def test_formatter_gets_floats_correctly():
    assert 6.0 == imp.data_formatter('6', 'num')
    assert 7.2456 == imp.data_formatter(7.2456, 'number')

def test_formatter_gets_lists_correctly():
    assert ['1','2','3'] == imp.data_formatter('[1,  2 ,3]', 'list')
    assert ['1','2','3'] == imp.data_formatter("'[1,2,3]'", 'array')

def test_build_patch_json_removes_empty_fields(file_metadata):
    post_json = imp.build_patch_json(file_metadata)

    # All the below values exist in file_metadatadd
    assert None == post_json.get('filesets:array', None)
    assert None == post_json.get('paired_end', None)

def test_build_patch_json_keeps_valid_fields(file_metadata):
    post_json = imp.build_patch_json(file_metadata)

    assert '/awards/OD008540-01/' == post_json.get('award', None)
    assert 'fastq' == post_json.get('file_format', None)


def test_build_patch_json_coverts_arrays(file_metadata):
    post_json = imp.build_patch_json(file_metadata)

    assert "dcic:HIC00test2" == file_metadata.get('aliases:array')
    assert ['dcic:HIC00test2'] == post_json.get('aliases', None)


def test_build_patch_json_embeds_fields(file_metadata):
    post_json = imp.build_patch_json(file_metadata)

    expected = [{'file': 'testfile.fastq', 'relationship_type': 'related_to'}]
    assert expected == post_json.get('related_files', None )
