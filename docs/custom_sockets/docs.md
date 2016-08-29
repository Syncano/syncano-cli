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

* `name` is the name of your new Custom Socket - this should be unique;
* `description` is a description of your Custom Socket - it allows to easily identify what your custom socket does;
* `author` is a metadata information about Custom Socket author; Under the hood: all fields that are not 
    * `name`, 
    * `description`, 
    * `endpoints`, 
    * `dependencies` 
    * can be found in `metadata` field on Custom Socket in Syncano Dasboard.
* `icon` is a metadata information about your Custom Socket - it stores the icon name used and its color for (used in Syncano Dashboard)
* `endpoints` - definition of the endpoints in Custom Socket; Currently supported endpoints can be only of `script` type.

    Consider this example:
    
        my_endpoint_1:
          script: script_endpoint_1

    In the YAML snippet:
    * `my_endpoint_1` is an endpoint name - it will be used in the url path; 
        * `script` is a type of the endpoint; 
        * `script_endpoint_1` is the dependency name which will be called when endpoint 
    `my_endpoint_1` will be requested; 
    
    In example above we didn't specify HTTP method - so no matter what HTTP method 
    will be used to call `my_endpoint_1` (can be PATCH, POST, GET, etc.), script endpoint `script_endpoint_1` will be called;
    
    Consider yet another example:
    
        my_endpoint_2:
          POST:
            script: script_endpoint_2
          GET:
            script: script_endpoint_3

    In the above YAML snippet:
    * `my_endpoint_2` is an endpoint name. 
    * GET, POST - define HTTP method type used to call our endpoint
    
    The difference is that we now define what happens for different HTTP methods. When GET HTTP method will be used, 
    `script_endpoint_3` script endpoint will be ran. When POST HTTP method will be used - `script_endpoint_2` endpoint will be executed. 
    
    Currently only supported endpoint types are Script Endpoints, which run scripts under the hood. But don't worry, 
    we are working on adding more options!

* `dependencies` - it's the definition of your Custom Socket dependencies. They define all dependency objects
which will be called when endpoint is requested. 

    Consider the example:
    
        dependencies:
         scripts:
          script_endpoint_1:
           runtime_name: python_library_v5.0
           file: scripts/script1.py

    Above YAML snippet defines one dependency:
    * `script` - type of the dependency (defined using `scripts` keyword). 
        * `script_endpoint_1` - name of the dependency is; it's an important element, because that's the place where you connect a dependency to an endpoint. 
            * `runtime_name` is name of the runtime used in a script; 
            * `file` stores the source code that will be executed.
    
    It should be noted that when defining Custom Scripts, we suggest following some basic directory structure- for
    better work organization. We recommend storing scripts under `scripts` directory - this is why filename 
    is a relative path: `scripts/script1.py`. Of course your can also follow your own rules,  e.g. by using a flat file structure.


## Custom Socket directory structure

Below is a sample Custom Socket structure for the above YAML definition:

![](images/tree_socket.png)

`socket.yml` file stores the YAML definition mentioned above; `scripts` directory stores all scripts source
code used in `script` dependency type. 


## Custom Socket examples

* ['HelloWorld' example](examples/hello_world.md)
* [Advanced example: provide title here](examples/advanced.md)
