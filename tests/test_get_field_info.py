import wranglertools.get_field_info as gfi

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
    field_list = gfi.build_field_list(item_properties)
    assert field_list


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
