#Submission of metadata using the 4DN REST API
The 4DN-DCIC metadata database can be accessed using a Hypertext-Transfer-Protocol-(HTTP)-based, Representational-state-transfer (RESTful) application programming interface (API) - aka the REST API.  In fact, this API is used by the ```import_data``` script used to submit metadata entered into excel spreadsheets as described [in this document](https://docs.google.com/document/d/1Xh4GxapJxWXCbCaSqKwUd9a2wTiXmfQByzP0P8q5rnE). This API was developed by the [ENCODE][encode] project so if you have experience retrieving data from or submitting data to ENCODE use of the 4DN-DCIC API should be familiar to you.   The REST API can be used both for data submission and data retrieval, typically using scripts written in your language of choice.  Data objects exchanged with the server conform to the standard JavaScript Object Notation (JSON) format.  Libraries written for use with your chosen language are typically used for the network connection, data transfer, and parsing of data  (for example, requests and json, respectively for Python).  For a good introduction to scripting data retrieval (using GET requests) you can refer to [this page](https://www.encodeproject.org/help/rest-api/) on the [ENCODE][encode] web site that also has a good introduction to viewing and understanding JSON formatted data.

[encode]: https://www.encodeproject.org/

###Connecting to the server
Your script will need to establish a connection with either the test or production server using credentials  format a request to the server to POST or PATCH your json formatted metadata. Exactly how you pass the necessary information to the server depends on your scripting language and the libraries that you use with it. 

**Base URLs for submitting data are:**  
*Test Server:* <https://testportal.4dnucleome.org>  
*Production Server:* <https://data.4dnucleome.org>


contain information regarding connecting to the desired server with appropriate credentials to upload data and will specify that the data will be submitted in json format.


add examples and requirements


###json formatting
The most important component of your submission is the proper formatting of the data into json so it will map correctly onto the 4DN metadata schemas.  The details of the schemas for all object types in the database can be viewed at <https://data.4dnucleome.org/profiles/>.  Individual schemas can be viewed and/or retrieved via GET by appending the schema file name to the above URL (eg. for the Hi-C experiment schema <https://data.4dnucleome.org/profiles/experiment_hi_c.json>). For a listing of all schema files and associated resource names see -

Depending on the Item type that you are submitting there may be fields that require values (eg. experiment_type for experiments), fields for which values should never be submitted (eg. ‘date_created’ as this is an automatically generated value) and fields with specific formatting and fields that accept values of specific types.  In many cases the values must be selected from a list of constrained choices.  The documentation on field values above and the annotated json document below should be used as a guide on formatting your json.
