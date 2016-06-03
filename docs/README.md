# How the data transfer from the Parse to Syncano works?

## Overview

The provided tool using an API on both sides. 

Firstly the Parse schemas are fetched and transferred to Syncano as classes.
All fields types are supported - with limitations of Array of Pointers - the Syncano does not support this. In such
case the array is written with parse object id as values. More about this step can be found below.

Secondly the data is transfer for each schema/class. This can be slitted to following steps:

1. The call to the Parse API is made - to obtain 1000 objects of particular class;
2. The conversion is made - the Object from Parse is transformed to the Syncano Data Object;
3. The batch API call is made to the Syncano API - with 50 elements (API limitations);

More on that step can be found in section below.

Thirdly the relations are restored. This is the most challenging task. During the first and second step the 
information about relations are stored. The map of references are build - which bind the Parse object with Syncano 
Data Object - and based on that the relations are restored. It's time consuming process - due to Parse API limitations
and Syncano throttling functionality. More information can be found in section below. 

### Schemas to classes transfer

**Name normalization**

For each Parse schema the Syncano Class schema is created. The class name is normalized - the same applies to the 
fields. The normalization process usually is just make a lowercase name. So when you transfer schema from Parse, 
which name is `SomeOutstandingClass` in Syncano it will be called: `someoutstandingclass`. The same applies to fields. 
Of course there're some exceptions. If Parse schema name starts from an underscore: `_<class_name>`, the name will 
be changed to `internal_<class_name>`, that's because the Syncano does not supports names which starts from an 
underscore.

**Created at and updated at**

The Syncano classes has fields `created_at` and `updated_at`, which are self explanatory: just stores the dates with 
creation of the object and update of the object. The Parse has fields `createdAt` and `updatedAt` - which are created
for the same purpose. The Syncano fields are read-only, so it's impossible to write there values from Parse - using API. 
To resolve this the two additional fields are created on Syncano class: `original_createdat` and `original_updatedat` - 
which has filter and order index enabled and can be used easily. This fields stores the original creation and update 
date (but update date will be **NOT** updated automatically) from Parse. 

**objectId field**

The Syncano and Parse use different methods of object identification. In Syncano the integer ID is used, in Parse the
string ID is used. That means that simple one-to-one conversion isn't possible. When creating the Syncano schema 
the additional field is made `objectid`, which stores the Parse string ID. This field has a filter index - so can be 
used for filtering in Syncano.

**ACL**

The ACL system in both Parse and Syncano is widely different - this is **NOT** supported yet. 
And it's hard to say that it will ever be. 

**Field mapping**

For the field types the following map is used - the key is the Parse field type, the value is the Syncano field type:

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

When Parse schemas are transferred as Syncano classes - the data migration process start. Class by class is processed: 
get the 1000 objects from Parse (the `limit` parameter limit) - then translate Parse object to the Syncano object, and 
make a batch call with 10 Syncano Data Object (to avoid throttling); During this process for each class the reference 
map is made. This reference map stores the class name and attach the Parse Object ID with Syncano Object ID. 
It can happen that this structure will use a lot of local machine memory.
 
Last step of data transfer is transferring the files. It's impossible to send files using batch in Syncano (and we do 
not want to make query for each object) - so the files are stored and the update is made for data objects with files.

### Relations rebuild

For each Parse object that has a relation field - the query is made - to obtain the related objects. 
Then those related objects are added to the Syncano Data Object. The relation are transformed as a whole. In 
Syncano the relation field stores IDs of the related objects, like this: `books=[1, 2, 3]`, which means that related
books are those with ids: 1, 2 and 3. This is why the relations rebuild process is last in queue. 
The information with Syncano IDs must be known - can't make a relation knowing only the Parse IDs. This process can be
very time consuming - first because there's a need to query each parse object with relations about related objects, 
secondly because the Syncano free account will throttles the requests when 15 request per second is reached.

## Limitations

The main limitations are:

1. Syncano free account throttling: 15 requests per second.
2. Parse `limit` get parameter equal to 1000.
3. Parse API calls for obtaining the related objects - can not be obtained as a large set - only one by one.


## Things you should know 

### Parse

The only operations that is made to the Parse API are **GET** calls. The Parse Application is not affected after or 
during the process of the data transfer.

**Master Key**

Your Parse Master Key - which is required by this tool is stored locally on your machine - under the home directory in 
`.syncano` file - and is used **ONLY** for communication with Parse.  

### Syncano

Each time the transfer is run - the data is doubled. It's because Syncano does not support the unique constraint - and
thus it's impossible to check if object with particular Parse ID is already present in the Syncano Data Objects. To
re-run data import process it's good to remove your instance or use new one in tool configuration.

The Syncano credentials are stored in `.syncano` file under your home directory and is used **ONLY** for communication
with Syncano services.
