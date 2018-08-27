import wranglertools.get_field_info as gfi
import pytest
from six import string_types

# test data is in conftest.py

keypairs = {
            "default":
            {"server": "https://data.4dnucleome.org/",
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
    assert isinstance(key.con_key["server"], string_types)
    assert isinstance(key.con_key['key'], string_types)
    assert isinstance(key.con_key['secret'], string_types)


@pytest.mark.file_operation
def test_key_file():
    key = gfi.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert isinstance(key.con_key["server"], string_types)
    assert isinstance(key.con_key['key'], string_types)
    assert isinstance(key.con_key['secret'], string_types)


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
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      side_effect=[returned_user_me_submit_for_one_lab.json(),
                                   returned_lab_w_one_award.json()]):
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
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      side_effect=[returned_user_me_submit_for_one_lab.json(),
                                   returned_lab_w_one_award.json(),
                                   returned_lab_w_one_award.json()]):
        connection = gfi.FDN_Connection(mkey)
        connection.prompt_for_lab_award()
        assert connection.lab == lab2chk
        assert connection.award == awd2chk


def test_connection_for_user_with_no_submits_for(
        mocker, mkey, returned_user_me_submit_for_no_lab):
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      return_value=returned_user_me_submit_for_no_lab.json()):
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
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      side_effect=[returned_user_me_submit_for_two_labs.json(),
                                   returned_lab_w_one_award.json(),
                                   returned_otherlab_w_one_award.json()]):
        connection = gfi.FDN_Connection(mkey)
        assert connection.lab == defaultlab
        assert connection.award == defaultaward
        # monkeypatch the "input" function, so that it returns "2".
        # This simulates the user entering "2" in the terminal:
        monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
        connection.prompt_for_lab_award()
        assert connection.lab == chosenlab
        assert connection.award == chosenaward


def test_connection_prompt_for_lab_award_multi_award(
    mocker, monkeypatch, mkey, returned_user_me_submit_for_one_lab,
        returned_lab_w_two_awards):
    '''this not only tests if the correct award is chosen if given the
        choice but also that multiple awards are linked
        to a lab the first is set as the defaul on init
    '''
    defaultlab = '/labs/bing-ren-lab/'
    defaultaward = '/awards/1U54DK107977-01/'
    chosenaward = '/awards/1U01ES017166-01/'
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      side_effect=[returned_user_me_submit_for_one_lab.json(),
                                   returned_lab_w_two_awards.json(),
                                   returned_lab_w_two_awards.json()]):
        connection = gfi.FDN_Connection(mkey)
        assert connection.lab == defaultlab
        assert connection.award == defaultaward
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
    defaultaward = '/awards/1U54DK107977-01/'
    chosenlab = '/labs/ben-ring-lab/'
    chosenaward = '/awards/7777777/'
    with mocker.patch('dcicutils.ff_utils.get_metadata',
                      side_effect=[returned_user_me_submit_for_two_labs.json(),
                                   returned_lab_w_two_awards.json(),
                                   returned_otherlab_w_two_awards.json()]):
        connection = gfi.FDN_Connection(mkey)
        assert connection.lab == defaultlab
        assert connection.award == defaultaward
        # monkeypatch the "input" function, so that it returns "2".
        # This simulates the user entering "2" in the terminal:
        monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
        connection.prompt_for_lab_award()
        assert connection.lab == chosenlab
        assert connection.award == chosenaward


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
    assert len(field_list) == 13
    names = [i.name for i in field_list]
    assert '*title' in names


def test_build_field_list_gets_enum(item_properties):
    field_list = gfi.build_field_list(item_properties, include_enums=True)
    for field in field_list:
        if field.name == "project":
            assert ['4DN', 'External'] == field.enum

    field_list = gfi.build_field_list(item_properties)
    for field in field_list:
        if field.name == "project":
            assert not field.enum


def test_build_field_list_gets_desc(item_properties):
    field_list = gfi.build_field_list(item_properties, include_description=True)
    for field in field_list:
        if field.name == "name":
            assert "official grant" in field.desc

    field_list = gfi.build_field_list(item_properties)
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
    with mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_vendor_schema.json()):
        field_dict = gfi.get_uploadable_fields(connection_mock, ['Vendor'])
        for field in field_dict['Vendor']:
            assert field.name is not None
            assert field.ftype is not None
            assert field.desc is not None
            assert field.comm is not None
            assert field.enum is not None


def xls_to_list(xls_file, sheet):
    """To compare xls files to reference ones, return a sorted list of content."""
    from operator import itemgetter
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
    return return_list.sort(key=itemgetter(1))


def xls_field_order(xls_file, sheet):
    # returns list of fields (in order) in an excel sheet
    import xlrd
    wb = xlrd.open_workbook(xls_file).sheet_by_name(sheet)
    return [str(wb.cell_value(0, col)) for col in range(1, wb.ncols)]


@pytest.mark.file_operation
def test_create_xls_vendor(connection_mock, mocker, returned_vendor_schema):
    xls_file = "./tests/data_files/GFI_test_vendor.xls"
    xls_ref_file = "./tests/data_files/GFI_test_vendor_reference.xls"
    import os
    try:
        os.remove(xls_file)
    except OSError:
        pass
    with mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_vendor_schema.json()):
        field_dict = gfi.get_uploadable_fields(connection_mock, ['Vendor'])
        gfi.create_xls(field_dict, xls_file)
        assert os.path.isfile(xls_file)
        assert xls_to_list(xls_file, "Vendor") == xls_to_list(xls_ref_file, "Vendor")
    try:
        os.remove(xls_file)
    except OSError:
        pass


@pytest.mark.file_operation
def test_create_xls_lookup_order(connection_mock, mocker, returned_vendor_schema_l):
    xls_file = "./tests/data_files/GFI_test_vendor_lookup.xls"
    ref_list = ['aliases', '*title', 'description', 'contributing_labs', 'tags', 'url']
    import os
    try:
        os.remove(xls_file)
    except OSError:
        pass
    with mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_vendor_schema_l.json()):
        field_dict = gfi.get_uploadable_fields(connection_mock, ['Vendor'])
        gfi.create_xls(field_dict, xls_file)
        assert os.path.isfile(xls_file)
        assert xls_field_order(xls_file, "Vendor") == ref_list
    try:
        os.remove(xls_file)
    except OSError:
        pass


@pytest.mark.file_operation
def test_create_xls_experiment_set(connection_mock, mocker, returned_experiment_set_schema):
    xls_file = "./tests/data_files/GFI_test_Experiment_Set.xls"
    xls_ref_file = "./tests/data_files/GFI_test_Experiment_Set_reference.xls"
    import os
    try:
        os.remove(xls_file)
    except OSError:
        pass
    with mocker.patch('dcicutils.ff_utils.get_metadata', return_value=returned_experiment_set_schema.json()):
        field_dict = gfi.get_uploadable_fields(connection_mock, ['ExperimentSet'], True, True, True)
        gfi.create_xls(field_dict, xls_file)
        assert os.path.isfile(xls_file)
        assert xls_to_list(xls_file, "ExperimentSet") == xls_to_list(xls_ref_file, "ExperimentSet")
    try:
        os.remove(xls_file)
    except OSError:
        pass
