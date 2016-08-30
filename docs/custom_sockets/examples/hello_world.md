# HelloWorld example

## Abstract

In this example we will create a simple Custom Socket. The idea here is to create an endpoint which will return
a `Hello world` message. 

## Repository link

The whole example can be found under: [Syncano/custom-socket-hello-world](https://github.com/Syncano/custom-socket-hello-world)
It's possible to install it to Syncano Instance using `install from url` functionality in CLI. The URL is:

`https://github.com/Syncano/custom-socket-hello-world/blob/master/socket.yml`

## Prerequisites

* Syncano Account - [Create one here](https://www.syncano.io/).  
* GIT - If you want to edit files locally, clone our repository using: 
```bash
git clone git@github.com:Syncano/custom-socket-hello-world.git
````
* Syncano [CLI tool](https://pypi.python.org/pypi/syncano-cli/0.5) in version 0.5 or higher.

    > Note:
    > It is nice to use virtualenv to separate your tools: `sudo pip install virtualenv`
    > Then create virtual env: `virtualenv cli` and active it: `source cli/bin/activate`
    > Install Syncano CLI: `pip install syncano_cli>=0.5`

4. Your favorite text editor.
  
## YML definition

    name: hello_world
    author:
      name: Info
      email: info@synano.com
    description: Hello World example
    endpoints:
      hello_endpoint:
        script: hello_world
    
    dependencies:
      scripts:
        hello_world:
          runtime_name: python_library_v5.0
          file: scripts/hello_world.py
          
Above YAML file defines one Custom Socket with one endpoint: 
* `hello_endpoint` for printing hello world on every HTTP method call.

There is also one `script` dependency defined, to `hello_world` script.

In my favorite editor the project look as follows:

![](../images/project_struct.png)

## Scripts definition

The script (`scripts/hello_world.py`) consists of a few lines:

    content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Hello world!</title>
        </head>
    
        <body>
            Hello World!
        </body>
    </html>
    """
    
    set_response(HttpResponse(status_code=200, content=content, content_type='text/html'))

The above code executed in Syncano will return a valid HTML response with the `Hello World!` message inside. 
The `set_response` is a function which returns a custom response (e.g. in JSON, CSV or HTML format) from the script. 

## Custom Socket directory structure

As can be seen in the example above, the basic structure of this Custom Socket is:

    .
    ├── scripts
    │   └── hello_world.py
    └── socket.yml

`socket.yml` file stores YAML definition of the Custom Socket, and under `scripts` directory there is a definition
of Custom Socket dependencies (currently of type `script`).

## Putting everything together

### Steps:

1. Assuming that you have Syncano CLI installed, log in using: `syncano login --instance-name your-instance-name`
    In my case it is:
    
        syncano login --instance-name patient-resonance-4283

    Next you will see a prompt for `username` and `password`; provide both and confirm with `enter`.
    
2. There are two ways of installing a Custom Socket - one is using your local files and the second one is by using a URL.

    To install the Custom Socket from url do:
    
        syncano sockets install https://raw.githubusercontent.com/Syncano/custom-socket-hello-world/master/socket.yml --name hello_world

    In this scenario - you do not even need to clone the repository to your local machine. The `--name` parameter and name here are needed - because under the hood, an empty Custom Socket is created - and fetching code from the repository is done asynchronously in the second step.
    
    To install Custom Socket from local files do:
    
        syncano sockets install <path_to_files>

    In my case it is:
    
        syncano sockets install ../syncano_scripts/repos/custom-socket-hello-world/

    So you need to point to the parent directory of your `socket.yml` definition.
     
3. Try a newly created Custom Socket:

    To list Custom Sockets, do:
    
        syncano sockets list

    In the output you should find:
    
        - socket:
            info: ''
            name: hello_world
            status: ok

    This means that Custom Socket `hello_world` was created successfuly - the status is `ok`. In any other case you will see here an `error` and detailed information in `info` about what went wrong.
    
    Now, list all defined endpoints:
    
        syncano sockets list endpoints

    In the output you should find:
    
        - endpoint:
            methods:
            - POST
            - PUT
            - PATCH
            - GET
            - DELETE
            name: hello_world/hello_endpoint
            path: /v1.1/instances/your-instance-name/endpoints/sockets/hello_world/hello_endpoint/

4. Run the endpoint defined in Custom Socket:

        syncano sockets run hello_world/hello_endpoint

    You should see in the output raw html file:
    
        <!DOCTYPE html>
        <html>
            <head>
                <title>Hello world!</title>
            </head>
        
            <body>
                Hello World!
            </body>   
        </html>

    Lets see if output can be seen in the browser:
    Go to: `https://api.syncano.io/v1.1/instances/your-instance-name/endpoints/sockets/hello_world/hello_endpoint/?api_key=your_api_key`
    We defined the endpoint to handle GET HTTP method. 
    
    In my case:
    
    ![](../images/hello_world.png)

5. To delete Custom Socket do:

        syncano sockets delete hello_world

## Summary

Hope this was helpful! If you have any question or issues, do no hesitate to contact me directly: sebastian.opalczynski@syncano.com
I am also available on the [Syncano Slack community](http://syncano-community.github.io/slack-invite/). See you there!
