import wranglertools.fdnDCIC as fdnDCIC
import json
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
    return fdnDCIC.FDN_Key(keypairs, "default")


def test_nothing():
    assert(1)


def test_key():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    assert(key)
    assert isinstance(key.server, string_types)
    assert isinstance(key.authpw, string_types)
    assert isinstance(key.authid, string_types)


@pytest.mark.file_operation
def test_key_file():
    key = fdnDCIC.FDN_Key('./tests/data_files/keypairs.json', "default")
    assert(key)
    assert isinstance(key.server, string_types)
    assert isinstance(key.authpw, string_types)
    assert isinstance(key.authid, string_types)


def test_key_error_wrong_format(capsys):
    fdnDCIC.FDN_Key([("key_name", "my_key")], "key_name")
    out = capsys.readouterr()[0]
    message = "The keyfile does not exist, check the --keyfile path or add 'keypairs.json' to your home folder"
    assert out.strip() == message


def test_connection():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    assert(connection)
    assert(connection.auth)
    assert(connection.server)


def test_test_connection_fail():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    assert connection.check is False


def test_connection_success(mocker, mkey, returned_user_me_submit_for_one_lab,
                            returned_lab_w_one_award):
    email = 'bil022@ucsd.edu'
    lab2chk = '/labs/bing-ren-lab/'
    awd2chk = '/awards/1U54DK107977-01/'
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      side_effect=[returned_user_me_submit_for_one_lab,
                                   returned_lab_w_one_award]):
        connection = fdnDCIC.FDN_Connection(mkey)
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
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      side_effect=[returned_user_me_submit_for_one_lab,
                                   returned_lab_w_one_award,
                                   returned_lab_w_one_award]):
        connection = fdnDCIC.FDN_Connection(mkey)
        connection.prompt_for_lab_award()
        assert connection.lab == lab2chk
        assert connection.award == awd2chk


def test_connection_for_user_with_no_submits_for(
        mocker, mkey, returned_user_me_submit_for_no_lab):
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      return_value=returned_user_me_submit_for_no_lab):
        connection = fdnDCIC.FDN_Connection(mkey)
        assert connection.check is True
        assert not connection.labs


def test_connection_prompt_for_lab_award_multi_lab(
    mocker, monkeypatch, mkey, returned_user_me_submit_for_two_labs,
        returned_lab_w_one_award, returned_otherlab_w_one_award):
    defaultlab = '/labs/bing-ren-lab/'
    defaultaward = '/awards/1U54DK107977-01/'
    chosenlab = '/labs/ben-ring-lab/'
    chosenaward = '/awards/1U01ES017166-01/'
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      side_effect=[returned_user_me_submit_for_two_labs,
                                   returned_lab_w_one_award,
                                   returned_otherlab_w_one_award]):
        connection = fdnDCIC.FDN_Connection(mkey)
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
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      side_effect=[returned_user_me_submit_for_one_lab,
                                   returned_lab_w_two_awards,
                                   returned_lab_w_two_awards]):
        connection = fdnDCIC.FDN_Connection(mkey)
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
    with mocker.patch('wranglertools.fdnDCIC.requests.get',
                      side_effect=[returned_user_me_submit_for_two_labs,
                                   returned_lab_w_two_awards,
                                   returned_otherlab_w_two_awards]):
        connection = fdnDCIC.FDN_Connection(mkey)
        assert connection.lab == defaultlab
        assert connection.award == defaultaward
        # monkeypatch the "input" function, so that it returns "2".
        # This simulates the user entering "2" in the terminal:
        monkeypatch.setitem(__builtins__, 'input', lambda x: "2")
        connection.prompt_for_lab_award()
        assert connection.lab == chosenlab
        assert connection.award == chosenaward


def test_FDN_url():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    test_objid_frame = [["trial", None],
                        ["trial?some", None],
                        ["trial", "object"],
                        ["trial?some", "object"]
                        ]
    expected_url = ["https://data.4dnucleome.org/trial?limit=all",
                    "https://data.4dnucleome.org/trial?some&limit=all",
                    "https://data.4dnucleome.org/trial?limit=all&frame=object",
                    "https://data.4dnucleome.org/trial?some&limit=all&frame=object"
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


@pytest.mark.webtest
def test_search_FDN(connection_public):
    my_award = fdnDCIC.search_FDN("Award", 'name', '1U01CA200059-01', connection_public)
    assert my_award[0]['uuid']


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
