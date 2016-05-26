# How does the data transfer from Parse to Syncano work?

## Overview

The provided tool uses both Syncano and Parse API. 

1. Parse schemas are fetched and transferred to Syncano as classes. All field types are supported.
2. Data is transferred for each schema/class. This can be divided into following steps:

   1. The call to the Parse API is made - to obtain 1000 objects of particular class;
   2. The conversion is made - the Object from Parse is transformed to the Syncano Data Object;
   3. The batch API call is made to the Syncano API - with 50 elements (API limitations);

3. All the object relations are restored. This is the most challenging task. During the first and second step, all the information about relations are saved. The map of references are built -- which binds Parse objects with Syncano Data Objects -- and based on that the relations are restored. It's a time consuming process due to Parse API limitations and Syncano throttling functionality. More information on that can be found in the [data transfer](#data-transfer) section below.

### Schemas to classes transfer

**Name normalization**

For each Parse schema, the Syncano Class schema is created. The class name and name of all fields are normalized. 
The normalization process usually just makes a lowercase name. So when you transfer schema from Parse, where class name name is `SomeOutstandingClass`, in Syncano it will be called: `someoutstandingclass`. 
The same applies to the fields. Of course there are some exceptions. If Parse schema name starts from an underscore: `_<class_name>`, the name will be changed to `internal_<class_name>`. That's because Syncano does not support names which start with an 
underscore.

**Created at and updated at**

Syncano classes have fields `created_at` and `updated_at`, which are self explanatory: they store the dates indicating when object was created and last updated. The Parse has fields `createdAt` and `updatedAt` - which are created for the same purpose. 
Syncano `created_at` and `updated_at` fields are read-only, so it's impossible to transfer there values from Parse.
To resolve this, two additional fields are created on Syncano class: `original_createdat` and `original_updatedat` - 
which have filter and order index added to them and can be used to find and sort data easily. 
These fields store the original creation and update date from Parse (but update date will be **NOT** updated automatically next time). 

**objectId field**

Syncano and Parse use different methods of object identification. Syncano uses integer ID field, Parse uses string ID field. 
That means that simple one-to-one conversion isn't possible. When creating the Syncano schema, additional 'objectid' field is made, which stores the Parse string ID. This field has a filter index added to it, so can be used for filtering data in the Syncano class.

**ACL**

The ACL system in both Parse and Syncano is widely different - transferring ACL is **NOT** supported yet. 
Currently we also are not able to provide any deadline when support for it will be added. 

**Field mapping**

For the field types, the following map is used - the key is the Parse field type, the value is the Syncano field type:

```python
class ClassProcessor(object):
    map = {
        'Number': 'integer',
        'Date': 'datetime',
        'Boolean': 'boolean',
        'String': 'string',
        'Array': 'array',
        'Object': 'object',
        'Pointer': 'reference',
        'File': 'file',
        'GeoPoint': 'geopoint',
        'Relation': 'relation',
    }
```

### Data transfer

When Parse schemas are transferred as Syncano classes - the data migration process start. 

Class by class is processed: 
* get the 1000 objects from Parse (max value of `limit` parameter)
* translate Parse objects to Syncano objects (and make a batch call with 10 Syncano Data Object, to avoid throttling); 
 
During this process for each class the reference map is made. This reference map stores the class name and connects Parse Object ID with Syncano Object ID. 
It is possible that this structure will use a lot of your local machine memory.
 
Last step of data transfer is transferring the files. It's impossible to send files using batch in Syncano (and we do 
not want to make query for each object) - so the files are stored and the update is made for data objects with files.

### Relations rebuild

For each Parse object that has a relation field a query is made -- to obtain the related objects. 
Then those related objects are added to the Syncano Data Object. Relations are transformed as a whole. In Syncano, relation fields store IDs of the related objects like this: 
```json
books=[1, 2, 3]
```
which means that related books are those with ids: 1, 2 and 3. This is why the relations rebuilding process is the last one in the queue. 
The information with Syncano IDs must be known - we can't make a relation knowing only Parse IDs. This process can be
very time consuming. First, because there's a need to query each parse object with relations about their related objects and
second, because the Syncano free Builder account will throttles all requests when 15 request per second limit is reached.

## Limitations

The main limitations are:

1. Syncano free Builder account throttling: 15 requests per second.
2. Parse `limit` parameter max value equal to 1000.
3. Parse API calls for obtaining the related objects - can not be obtained as a large set - only one by one.

## Things you should know 

### Parse

The only operations that are made to Parse API are **GET** calls. Your Parse Application is not affected after or 
during the process of the data transfer.

**Master Key**

Your Parse Master Key - which is required by this tool - is stored locally on your machine, under the home directory in 
`.syncano` file. It is used **ONLY** for communication with Parse.  

### Syncano

Each time the transfer is run - data will be duplicated. It's because Syncano does not support the unique constraint - and
thus it's impossible to check if object with particular Parse ID is already present in the Syncano Data Objects. Before
re-running the data import process, it's a good idea to remove your instance or already trasferred classes, or use a new one in our tool configuration.

Syncano credentials are stored in `.syncano` file under your home directory, and are used **ONLY** for communication
with Syncano services.
