import pytest
import wranglertools.fdnDCIC as fdnDCIC

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


@pytest.mark.key
def test_key():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    assert(key)
    assert(type(key.server) is str)
    assert(type(key.authpw) is str)
    assert(type(key.authid) is str)


@pytest.mark.connection
def test_connection():
    key = fdnDCIC.FDN_Key(keypairs, "default")
    connection = fdnDCIC.FDN_Connection(key)
    assert(connection)
    assert(connection.auth)
    assert(connection.server)


# @pytest.mark.get
# def test_get():
#     key = fdnDCIC.FDN_Key(keypairs, "default")
#     connection = fdnDCIC.FDN_Connection(key)
#     result = fdnDCIC.get_FDN("/profiles/", connection)
#     assert(type(result) is dict)
