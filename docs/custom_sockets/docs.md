# Syncano Custom Sockets

## YAML file structure (socket.yml)

    name: my_integration
    description: Example integration  
    author:
      name: Sebastian
      email: sebastian@syncano.com
    icon:
      name: icon_name
      color: red
    endpoints:
      my_endpoint_1:
        script: script_endpoint_1
    
      my_endpoint_2:
        POST:
          script: script_endpoint_2
        GET:
          script: script_endpoint_3
    
    dependencies:
      scripts:
        script_endpoint_1:
          runtime_name: python_library_v5.0
          file: scripts/script1.py
    
        script_endpoint_2:
          runtime_name: python_library_v5.0
          file: scripts/script2.py
    
        script_endpoint_3:
          runtime_name: python_library_v5.0
          file: scripts/script3.py

### YAML file structure explanation

* `name` is the name of the new Custom Socket - this should be unique;
* `description` is the description of the Custom Socket - allows to easily tell what custom socket do;
* `author` is a metadata information about Custom Socket author; Under the hood: all fields that are not in list: 
`name`, `description`, `endpoints`, `dependencies` can be found in `metadata` field on Custom Socket in Syncano Dasboard.
* `icon` is a metadata information about Custom Socket - just stores the used icon name and its color - for display in 
Syncano Dasboard.
* `endpoints` - definition of the endpoints in Custom Socket; Currently supported endpoints can be of type `script`.

    Consider the example:
    
        my_endpoint_1:
          script: script_endpoint_1

    In above YAML snippet - the `my_endpoint_1` is an endpoint name - this will be used in url path; the `script` is 
    a type of the endpoint; and `script_endpoint_1` is a dependency name which will be called when endpoint 
    `my_endpoint_1` will be requested; In above example the http methods use wildcard - so no matter what http method 
    will be used - the script endpoints `script_endpoint_1` will be called;
    
    Consider yet another example:
    
        my_endpoint_2:
          POST:
            script: script_endpoint_2
          GET:
            script: script_endpoint_3

    In above YAML snippet - the `my_endpoint_2` is an endpoint name. The difference is that - when GET http method will
    be used the script endpoint `script_endpoint_3` will be ran. When POST http method will be used - the script
    endpoint `script_endpoint_2` will be ran. 
    
    Currently supported type of endpoint are only `script` - which run script endpoints under the hood, 
    but we are working to add more integrations.

* `dependencies` - definition of the dependencies for the Custom Socket. Dependencies define the dependency object
which will be called when endpoint will be requested. 

    Consider the example:
    
        scripts:
          script_endpoint_1:
            runtime_name: python_library_v5.0
            file: scripts/script1.py

    The above YML snippet defines one dependency of type script (under the `scripts` special word). The name of the
    dependency is `script_endpoint_1` - and this is important, because it is a connecting point with an endpoint. 
    the `runtime_name` is a runtime used in a script, and the `file` stores the source code that will be executed.
    It should be `noted` that when defining Custom Script some basic directory structure should be fulfilled - for
    better work organization. It's desired to store scripts under the scripts directory - this is why filename 
    is a relative path: `scripts/script1.py`. Of course this can be omitted - and flat structure can be used.


## Custom Socket directory structure

Below is a sample Custom Socket structure for the above YAML definition:

![](images/tree_socket.png)

The `socket.yml` file stores the YAML definition mentioned above; The `scripts` directory stores all scripts source
code used in `script` dependency type. 


## Custom Socket examples

* ['HelloWorld' example](examples/hello_world.md)
* [Advanced example: provide title here](examples/advanced.md)
