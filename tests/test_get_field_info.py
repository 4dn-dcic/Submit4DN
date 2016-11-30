import wranglertools.get_field_info as gfi
import pytest

# test data is in conftest.py


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


def test_get_uploadable_fields_mock(connection, mocker, returned_vendor_schema):
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_schema):
        field_dict = gfi.get_uploadable_fields(connection, ['Vendor'])
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


@pytest.mark.file_operation
def test_create_xls_vendor(connection, mocker, returned_vendor_schema):
    xls_file = "./tests/data_files/GFI_test_vendor.xls"
    xls_ref_file = "./tests/data_files/GFI_test_vendor_reference.xls"
    import os
    try:
        os.remove(xls_file)
    except OSError:
        pass
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_vendor_schema):
        field_dict = gfi.get_uploadable_fields(connection, ['Vendor'])
        gfi.create_xls(field_dict, xls_file)
        assert os.path.isfile(xls_file)
        assert xls_to_list(xls_file, "Vendor") == xls_to_list(xls_ref_file, "Vendor")
    try:
        os.remove(xls_file)
    except OSError:
        pass


@pytest.mark.file_operation
def test_create_xls_experiment_set(connection, mocker, returned_experiment_set_schema):
    xls_file = "./tests/data_files/GFI_test_Experiment_Set.xls"
    xls_ref_file = "./tests/data_files/GFI_test_Experiment_Set_reference.xls"
    import os
    try:
        os.remove(xls_file)
    except OSError:
        pass
    with mocker.patch('wranglertools.fdnDCIC.requests.get', return_value=returned_experiment_set_schema):
        field_dict = gfi.get_uploadable_fields(connection, ['ExperimentSet'], True, True, True)
        gfi.create_xls(field_dict, xls_file)
        assert os.path.isfile(xls_file)
        assert xls_to_list(xls_file, "ExperimentSet") == xls_to_list(xls_ref_file, "ExperimentSet")
    try:
        os.remove(xls_file)
    except OSError:
        pass
