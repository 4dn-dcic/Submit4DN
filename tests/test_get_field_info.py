import wranglertools.get_field_info as gfi
import pytest
from operator import itemgetter
import openpyxl
from pathlib import Path
import os

# test data is in conftest.py

keypairs = {
    "default":
        {
            "server": "https://data.4dnucleome.org/",
            "key": "keystring",
            "secret": "secretstring"
        }
}


@pytest.fixture
def mkey():
    return gfi.FDN_Key(keypairs, "default")


def test_key():
    key = gfi.FDN_Key(keypairs, "default")
    assert(key)
    assert isinstance(key.con_key["server"], str)
    assert isinstance(key.con_key['key'], str)
    assert isinstance(key.con_key['secret'], str)


@pytest.mark.file_operation
def test_key_file():
    key = gfi.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert isinstance(key.con_key["server"], str)
    assert isinstance(key.con_key['key'], str)
    assert isinstance(key.con_key['secret'], str)


def test_key_error_wrong_format(capsys):
    gfi.FDN_Key([("key_name", "my_key")], "key_name")
    out = capsys.readouterr()[0]
    message = "The keyfile does not exist, check the --keyfile path or add 'keypairs.json' to your home folder"
    assert out.strip() == message


def bad_connection_will_exit():
    with pytest.raises(SystemExit) as excinfo:
        keypairs = {
                    "default":
                    {"server": "https://data.4dnucleome.org/",
                     "key": "testkey",
                     "secret": "testsecret"
                     }
                    }
        key = gfi.FDN_Key(keypairs, "default")
        gfi.FDN_Connection(key)
    assert str(excinfo.value) == "1"


def test_connection_success(mocker, mkey, returned_user_me_submit_for_one_lab,
                            returned_lab_w_one_award):
    email = 'bil022@ucsd.edu'
    lab2chk = '/labs/bing-ren-lab/'
    awd2chk = '/awards/1U54DK107977-01/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(), returned_lab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    assert connection.check is True
    assert connection.email == email
    assert lab2chk in connection.labs
    assert connection.lab == lab2chk
    assert connection.award == awd2chk


def test_connection_prompt_for_lab_award_no_prompt_for_one_each(
        mocker, mkey, returned_user_me_submit_for_one_lab,
        returned_lab_w_one_award):
    lab2chk = '/labs/bing-ren-lab/'
    awd2chk = '/awards/1U54DK107977-01/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(),
        returned_lab_w_one_award.json(),
        returned_lab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    connection.prompt_for_lab_award()
    assert connection.lab == lab2chk
    assert connection.award == awd2chk


def test_connection_for_user_with_no_submits_for(mocker, mkey, returned_user_me_submit_for_no_lab):
    mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_user_me_submit_for_no_lab.json())
    connection = gfi.FDN_Connection(mkey)
    assert connection.check is True
    assert not connection.labs


def test_connection_prompt_for_lab_award_multi_lab(
        mocker, monkeypatch, mkey, returned_user_me_submit_for_two_labs,
        returned_lab_w_one_award, returned_otherlab_w_one_award):
    defaultlab = '/labs/bing-ren-lab/'
    defaultaward = '/awards/1U54DK107977-01/'
    chosenlab = '/labs/ben-ring-lab/'
    chosenaward = '/awards/1U01ES017166-01/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_two_labs.json(),
        returned_lab_w_one_award.json(),
        returned_otherlab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    assert connection.lab == defaultlab
    assert connection.award == defaultaward
    # monkeypatch the "input" function, so that it returns "2".
    # This simulates the user entering "2" in the terminal:
    monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
    connection.prompt_for_lab_award()
    assert connection.lab == chosenlab
    assert connection.award == chosenaward


def test_connection_prompt_for_lab_award_multi_lab_bad_choice(
        mocker, monkeypatch, mkey, returned_user_me_submit_for_two_labs,
        returned_lab_w_one_award, returned_otherlab_w_one_award, capsys):
    defaultlab = '/labs/bing-ren-lab/'
    defaultaward = '/awards/1U54DK107977-01/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_two_labs.json(),
        returned_lab_w_one_award.json(),
        returned_otherlab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    assert connection.lab == defaultlab
    assert connection.award == defaultaward
    # monkeypatch the "input" function, so that it returns "2".
    # This simulates the user entering "2" in the terminal:
    monkeypatch.setitem(__builtins__, 'input', lambda x: "3")
    connection.prompt_for_lab_award()
    assert connection.lab == defaultlab
    assert connection.award == defaultaward
    out = capsys.readouterr()
    assert "Not a valid choice - using" in out[0]


def test_connection_prompt_for_lab_award_multi_award(
        mocker, monkeypatch, mkey, returned_user_me_submit_for_one_lab,
        returned_lab_w_two_awards):
    '''this not only tests if the correct award is chosen if given the
        choice but also that multiple awards are linked
        to a lab the first is set as the default on init
    '''
    defaultlab = '/labs/bing-ren-lab/'
    chosenaward = '/awards/1U01ES017166-01/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(),
        returned_lab_w_two_awards.json(),
        returned_lab_w_two_awards.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    assert connection.lab == defaultlab
    assert connection.award is None
    # monkeypatch the "input" function, so that it returns "2".
    # This simulates the user entering "2" in the terminal:
    monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
    connection.prompt_for_lab_award()
    assert connection.lab == defaultlab
    assert connection.award == chosenaward


def test_connection_prompt_for_lab_award_multi_lab_award(
        mocker, monkeypatch, mkey, returned_user_me_submit_for_two_labs,
        returned_lab_w_two_awards, returned_otherlab_w_two_awards):
    defaultlab = '/labs/bing-ren-lab/'
    chosenlab = '/labs/ben-ring-lab/'
    chosenaward = '/awards/7777777/'
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_two_labs.json(),
        returned_lab_w_two_awards.json(),
        returned_otherlab_w_two_awards.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    assert connection.lab == defaultlab
    assert connection.award is None
    # monkeypatch the "input" function, so that it returns "2".
    # This simulates the user entering "2" in the terminal:
    monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
    connection.prompt_for_lab_award()
    assert connection.lab == chosenlab
    assert connection.award == chosenaward


def test_set_award_no_lab(mocker, mkey, returned_user_me_submit_for_one_lab,
                          returned_lab_w_one_award):
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(), returned_lab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    connection.set_award(None)
    assert connection.award is None


def test_set_award_one_lab_one_award(mocker, mkey, returned_user_me_submit_for_one_lab,
                                     returned_lab_w_one_award):
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(),
        returned_lab_w_one_award.json(),
        returned_lab_w_one_award.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    connection.set_award(returned_lab_w_one_award.json()['@id'])
    assert connection.lab == returned_lab_w_one_award.json()['@id']
    assert connection.award == returned_lab_w_one_award.json()['awards'][0]['@id']


def test_set_award_multi_awards_dontPrompt(mocker, mkey, returned_user_me_submit_for_one_lab,
                                           returned_lab_w_two_awards):
    mocker.patch('dcicutils.ff_utils.get_metadata', side_effect=[
        returned_user_me_submit_for_one_lab.json(),
        returned_lab_w_two_awards.json(),
        returned_lab_w_two_awards.json()
    ])
    connection = gfi.FDN_Connection(mkey)
    connection.set_award(returned_lab_w_two_awards.json()['@id'], True)
    assert connection.award is None


def test_get_field_type():
    field1 = {'type': 'string'}
    assert gfi.get_field_type(field1) == 'string'

    field2 = {'type': 'number'}
    assert gfi.get_field_type(field2) == 'number'


def test_is_subobject():
    field = {'items': {'type': 'object'}}
    assert gfi.is_subobject(field)


def test_is_not_subobject_wrong_type():
    field = {'items': {'type': 'string'}}
    assert not gfi.is_subobject(field)


def test_is_not_subobject_invalid_data():
    field = {'items': 'ugly'}
    assert not gfi.is_subobject(field)


def test_dotted_field_name():
    assert "parent.child" == gfi.dotted_field_name("child", "parent")


def test_dotted_field_name_no_parent():
    assert "child" == gfi.dotted_field_name("child")


def test_build_field_list(item_properties):
    field_list = gfi.build_field_list(item_properties, required_fields=["title", "pi"])
    assert field_list
    assert len(field_list) == 16
    names = [i.name for i in field_list]
    assert '*title' in names


def test_build_field_list_excludes_from_and_skip_import_items(item_properties):
    field_list = gfi.build_field_list(item_properties)
    assert not [field for field in field_list if field.name == 'schema_version']  # exclude_from
    assert not [field for field in field_list if field.name == 'accession']  # import_items


def test_build_field_list_does_not_skip_import_items_if_admin(item_properties):
    field_list = gfi.build_field_list(item_properties, admin=True)
    assert not [field for field in field_list if field.name == 'schema_version']  # exclude_from
    assert [field for field in field_list if field.name == 'accession']  # import_items


def test_build_field_list_gets_enum_or_suggested_enum(item_properties):
    field_list = gfi.build_field_list(item_properties)
    for field in field_list:
        if field.name == "project":
            assert ['4DN', 'External'] == field.enum
        if field.name == "url":
            assert ['https://www.test.com', 'https://www.example.com'] == field.enum
        if field.name == "status":
            assert 'awesome' not in field.enum
            assert 'current' in field.enum

    field_list = gfi.build_field_list(item_properties, no_enums=True)
    for field in field_list:
        if field.name == "project":
            assert not field.enum


def test_build_field_list_gets_desc(item_properties):
    field_list = gfi.build_field_list(item_properties)
    for field in field_list:
        if field.name == "name":
            assert "official grant" in field.desc

    field_list = gfi.build_field_list(item_properties, no_description=True)
    for field in field_list:
        if field.name == "name":
            assert len(field.comm) == 0


def test_build_field_list_gets_comments(item_properties):
    field_list = gfi.build_field_list(item_properties, include_comment=True)
    for field in field_list:
        if field.name == "end_date":
            assert len(field.comm) >= 1

    field_list = gfi.build_field_list(item_properties)
    for field in field_list:
        if field.name == "end_date":
            assert len(field.comm) == 0


def test_build_field_list_skips_calculated_properties(calc_properties):
    field_list = gfi.build_field_list(calc_properties)
    assert 1 == len(field_list)
    assert field_list[0].name == 'description'


def test_build_field_list_embeds_with_dots(embed_properties):
    field_list = gfi.build_field_list(embed_properties)
    assert 2 == len(field_list)
    assert field_list[0].name.startswith('experiment_relation')
    assert "array of embedded objects" in field_list[0].ftype
    assert field_list[1].name.startswith('experiment_relation')


def test_get_uploadable_fields_mock(connection_mock, mocker, returned_vendor_schema):
    mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_vendor_schema.json())
    field_dict = gfi.get_uploadable_fields(connection_mock, ['Vendor'])
    for field in field_dict['Vendor']:
        assert field.name is not None
        assert field.ftype is not None
        assert field.desc is not None
        assert field.comm is not None
        assert field.enum is not None


def xls_to_list(xls_file, sheet):
    """To compare xls files to reference ones, return a sorted list of content."""
    return_list = []
    wb = openpyxl.load_workbook(xls_file)
    return sorted([value for row in wb[sheet].values for value in row if value])


def xls_field_order(xls_file, sheet):
    ''' returns the list of fields in the order they appear in an excel sheet
        removes the commented out first col header
    '''
    wb = openpyxl.load_workbook(xls_file)
    return list(next(wb[sheet].values))[1:]


@pytest.mark.file_operation
def test_create_xlsx_default_options(connection_mock, mocker, returned_bcc_schema):
    """ creates a workbook with one BiosampleCellCulture sheet with default options for populating rows
        schema used is a fixture with a trimmed version that cotains properties to test various permutations
    """
    EXPECTED = [
        '#Additional Info:', '#Description:', '#Field Name:', '#Field Type:', '*culture_start_date',
        '-', '-', '-', '-', '-', '-',
        'A short description of the cell culture procedure - eg. Details on culturing a preparation of K562 cells',
        "Choices:['Yes', 'No']", "Choices:['cardiac muscle myoblast', 'cardiac muscle cell']", "Choices:['non synchronized', 'G1']",
        'If a culture is synchronized the cell cycle stage from which the biosample used in an experiment is prepared',
        'Item:OntologyTerm', 'Protocols including additional culture manipulations such as stem cell differentiation or cell cycle synchronization.',
        'Relevant for pluripotent and stem cell lines - set to Yes if cells have undergone in vitro differentiation',
        'The resulting tissue or cell type for cells that have undergone differentiation.',
        'Total number of culturing days since receiving original vial', 'YYYY-MM-DD format date for most recently thawed cell culture.',
        'array of Item:Protocol', 'culture_duration', 'culture_harvest_date', 'description', 'in_vitro_differentiated',
        'integer', 'number', 'passage_number', 'protocols_additional', 'string', 'string', 'string', 'string', 'string',
        'synchronization_stage', 'tissue'
    ]
    xls_file = "./tests/data_files/workbooks/GFI_test_bcc_sheet.xlsx"
    try:
        os.remove(xls_file)  # file should be created by the test
    except OSError:
        pass
    mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_bcc_schema.json())
    field_dict = gfi.get_uploadable_fields(connection_mock, ['BiosampleCellCulture'])
    gfi.create_xls(field_dict, xls_file)
    assert Path(xls_file).is_file()
    expected = xls_to_list(xls_file, "BiosampleCellCulture")
    assert xls_to_list(xls_file, "BiosampleCellCulture") == EXPECTED
    try:
        os.remove(xls_file)
    except OSError as e:
        assert False
        print("Cleanup needed! {}".format(e))


@pytest.mark.file_operation
def test_create_xlsx_non_defaults(connection_mock, mocker, returned_bcc_schema):
    xls_file = "./tests/data_files/workbooks/GFI_test_bcc_sheet.xlsx"
    EXPECTED = [
        '#Additional Info:', '#Description:', '#Field Name:', '#Field Type:',
        '*culture_start_date', '-', '-', '-', '-', '-', '-', '-', '-',
        'Date can be submitted in as YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSTZD',
        'Item:OntologyTerm', 'array of Item:Protocol', 'culture_duration',
        'culture_harvest_date', 'description', 'in_vitro_differentiated', 'integer',
        'number', 'passage_number', 'protocols_additional', 'string',
        'string', 'string', 'string', 'string', 'synchronization_stage', 'tissue'
    ]
    try:
        os.remove(xls_file)
    except OSError:
        pass
    mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_bcc_schema.json())
    field_dict = gfi.get_uploadable_fields(connection_mock, ['BiosampleCellCulture'], no_description=True, include_comments=True, no_enums=True)
    gfi.create_xls(field_dict, xls_file)
    assert os.path.isfile(xls_file)
    assert xls_to_list(xls_file, "BiosampleCellCulture") == EXPECTED
    try:
        os.remove(xls_file)
    except OSError as e:
        assert False
        print("Cleanup needed! {}".format(e))


@pytest.mark.file_operation
def test_create_xls_lookup_order(connection_mock, mocker, returned_vendor_schema_l):
    xls_file = "./tests/data_files/GFI_test_vendor_lookup.xlsx"
    ref_list = ['aliases', '*title', 'description', 'contributing_labs', 'tags', 'url']
    try:
        os.remove(xls_file)
    except OSError:
        pass
    mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_vendor_schema_l.json())
    field_dict = gfi.get_uploadable_fields(connection_mock, ['Vendor'])
    gfi.create_xls(field_dict, xls_file)
    assert Path(xls_file).is_file()
    assert xls_field_order(xls_file, "Vendor") == ref_list
    try:
        os.remove(xls_file)
    except OSError as e:
        assert False
        print("Cleanup needed! {}".format(e))


def test_get_sheet_names(capfd):
    input_list = ['hic', 'experi-ment_capture-c', 'TreatmentChemical', 'Biosample']
    result = gfi.get_sheet_names(input_list)
    out, err = capfd.readouterr()
    assert result == [
        'Protocol', 'Publication', 'Image', 'Biosource', 'BiosampleCellCulture',
        'Biosample', 'FileFastq', 'ExperimentHiC', 'ExperimentCaptureC', 'ExperimentSetReplicate'
        ]
    assert len(result) == len(list(set(result)))
    assert 'No schema found for type TreatmentChemical' in out
