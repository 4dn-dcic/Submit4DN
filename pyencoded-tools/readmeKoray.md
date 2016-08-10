#Some notes on py tools

##Connection
first thing you need is the keyfile to access the REST application
it is a json formatted file that contains key,secret and server
under one identifier. Here is the default structure. The default path
is /Users/user/keypairs.json

    {
      "default": {
        "key": "BBXSW2MN",
        "secret": "2ikpug5futbov5ap",
        "server": "http://ec2-54-210-11-70.compute-1.amazonaws.com/"
      }
    }
if file name is different and the key is not named default add it to the code:
python3 code.py --keyfile nameoffile.json --key NotDefault



##Fetching Data
Once the connection is created, one can fetch the dict of an accession with
obj = encodedcc.get_ENCODE(acc, connection)
