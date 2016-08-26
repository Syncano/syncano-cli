# Adanced Custom Socket example
 
## Abstract

In this advanced example the integration with Mailgun will be made (https://mailgun.com/). The mailgun sandbox environment
will be used. It allows to send 300 mails per day - so it should be enough. In this example two endpoints in Custom Socket
will be implemented - one for sending emails, and second - to obtain some basic statistics.

## Repository link

The whole example can be found under: [Syncano/custom-socket-advanced-example](https://github.com/Syncano/custom-socket-advanced-example)
This can be installed in Syncano instance using the install from url functionality in CLI. The url is: url here

## Prerequisites

1. Syncano Account - Create one [here](https://www.syncano.io/). 
2. GIT - for repository clone: `git clone git@github.com:Syncano/custom-socket-hello-world.git`. If you want to edit
    files locally.
3. Syncano [CLI tool](https://pypi.python.org/pypi/syncano-cli/0.5) in version 0.5 or higher.

    > Note:
    > It is nice to use virtualenv to separate your tools: `sudo pip install virtualenv`
    > Then create virtual env: `virtualenv cli` and active it: `source cli/bin/activate`
    > Install Syncano CLI: `pip install syncano_cli>=0.5`

4. Your favourite text editor.

## YML definition

    name: mailgun_integration
    description: An advanced example of Custom Socket - mailgun integration.
    author:
      name: Info at Syncano
      email: info@syncano.com
    endpoints:
      send_mail:
        POST:
          script: send_mail
    
      get_stats:
        GET:
          script: get_stats
    
    dependencies:
      scripts:
        send_mail:
          runtime_name: python_library_v5.0
          file: scripts/send_mail.py
    
        get_stats:
          runtime_name: python_library_v5.0
          file: scripts/get_stats.py

The above YAML definition defines a one Custom Socket with two endpoints: one for send email: `send_mail` with POST 
http method (we want to pass here some basic information about email: to who it should be send, what subject should be used
and what text should be in the email itself). The second endpoint is for obtaining basic stats from Mailgun service.

There're also two `script` dependencies defined.

## Scripts definition

### scripts/send_mail.py

    import requests
    import json
    
    api_key = CONFIG.get('mailgun_api_key')
    
    to_email = ARGS.get('to_email')
    subject = ARGS.get('subject')
    email_body = ARGS.get('email_body')
    
    response = requests.post(
        "https://api.mailgun.net/v3/sandboxa8ccfb01296d4b19bace47fb8102d130.mailgun.org/messages",
        auth=("api", api_key),
        data={
            "from": "Mailgun Sandbox <postmaster@sandboxa8ccfb01296d4b19bace47fb8102d130.mailgun.org>",
            "to": to_email,
            "subject": subject,
            "text": email_body
        }
    )
    
    if response.status_code == 200:
        success_content = json.dumps(
            {
                'status_code': 200,
                'info': u'Mail successfully send to {}'.format(to_email)
            }
        )
        set_response(HttpResponse(status_code=200, content=success_content, content_type='application/json'))
    else:
        fail_content = json.dumps(
            {
                'status_code': response.status_code,
                'info': response.text
            }
        )
        set_response(HttpResponse(status_code=400, content=fail_content, content_type='application/json'))

The above script will send a request to the Mailgun service - and this service will send an email to user.
It's worth to note the `CONFIG` variable - it's a Instance global config map - you can define its content in the
Syncano Dasboard under the `Global Config` menu or using Syncano Libraries - more can be found at 
[docs.](http://docs.syncano.io/docs/snippets-scripts#section-global-config-dictionary)

### scripts/get_stats.py

    import requests

    api_key = CONFIG.get('mailgun_api_key')
    
    response = requests.get(
        "https://api.mailgun.net/v3/sandboxa8ccfb01296d4b19bace47fb8102d130.mailgun.org/stats/total",
        auth=("api", api_key),
        params={
            "event": ["accepted", "delivered", "failed"],
            "duration": "1m"}
    )
    
    if response.status_code == 200:
        set_response(HttpResponse(status_code=200, content=response.text, content_type='application/json'))
    else:
        set_response(HttpResponse(status_code=400, content=response.text, content_type='application/json'))

Above script will work as a proxy to the Mailgun service - will send a request about stats and passes the results as
a response.


## Custom Socket directory structure

The directory structure in my favourite editors looks like this:

![](../images/project_struct_adv.png)

or in tree format:
    
    .
    ├── scripts
    │   ├── get_stats.py
    │   └── send_mail.py
    └── socket.yml


## Pulling everything together

### Steps:

1. Assuming that you have Syncano CLI installed, do a login: `syncano login --instance-name your-instance-name`
    In my case it is:
    
        syncano login --instance-name patient-resonance-4283

    Next you will see the prompt for `username` and `password`; Provide it.

2. There are two ways of installing Custom Socket - one is using your local files and the second is to use a url.

    To install Custom Socket from url do:
    
        syncano sockets install https://raw.githubusercontent.com/Syncano/custom-socket-advanced-example/master/socket.yml --name mailgun_integration

    In such scenario - you do not need even clone the repository to your local machine. The name here is needed - because
    under the hood empty Custom Socket is created - and code fetch from repository is done asynchronously in second
    step.
    
    To install Custom Socket from local files do:
    
        syncano sockets install <path_to_files>

    In my case it is:
    
        syncano sockets install ../syncano_scripts/repos/custom-socket-advanced-example/
        
3. Try a newly created Custom Socket:

    To list a Custom Sockets, do:
    
        syncano sockets list

    In the output you should find:
    
        - socket:
            info: ''
            name: mailgun_integration
            status: ok

    This mean that Custom Socket hello_world was created successfuly - the status is `ok`. In any other case you will see
    here and `error` and detailed information in `info` - what was wrong.
    
    Now list the defined endpoints:
    
        syncano sockets list endpoints

    In the output you should find:
    
        - endpoint:
            methods:
            - GET
            name: mailgun_integration/get_stats
            path: /v1.1/instances/patient-resonance-4283/endpoints/sockets/mailgun_integration/get_stats/
        - endpoint:
            methods:
            - POST
            name: mailgun_integration/send_mail
            path: /v1.1/instances/patient-resonance-4283/endpoints/sockets/mailgun_integration/send_mail/

4. Before you run an endpoints - be sure that you have a Mailgun `api_key` in your instance Global Config. See the 
`send_mail.py` description for more details. My config looks like this:

        {"mailgun_api_key": "key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}


5. Run the endpoint defined in Custom Socket:

    First run the stats endpoint - as it is easier, because it is simple GET and no arguments are required.
    
        syncano sockets run mailgun_integration/get_stats

    In the output you should see something like this (probably not formatted):
    
        {
            "stats": [
                {
                    "delivered": {
                        "smtp": 5, 
                        "total": 5, 
                        "http": 0
                    }, 
                    "accepted": {
                        "outgoing": 5, 
                        "total": 5, 
                        "incoming": 0
                    }, 
                    "time": "Mon, 01 Aug 2016 00:00:00 UTC", 
                    "failed": {
                        "permanent": {
                            "suppress-complaint": 0, 
                            "suppress-bounce": 0, 
                            "total": 0, 
                            "bounce": 0, 
                            "suppress-unsubscribe": 0
                        }, 
                        "temporary": {
                            "espblock": 0
                        }
                    }
                }
            ], 
            "end": "Mon, 01 Aug 2016 00:00:00 UTC", 
            "resolution": "month", 
            "start": "Mon, 01 Aug 2016 00:00:00 UTC"
        }

    The above response is one-to-one to the response provided by Mailgun.
    
    **Let send a mail now**
    
    Run:
    
        syncano sockets run mailgun_integration/send_mail POST --data '{"subject": "CustomSocket MailGun test", "to_email": "FirstName LastName <your_email>", "email_body": "It is nice to create Custom Sockets!"}'

    Do not forget to change email in JSON data.
    
    This should return:
    
        {
            u'info': u'Mail successfully send to {to_email_value}', 
            u'status_code': 200
        }
        
    You can now call stats again and see if any changes appeared. 

6. To delete Custom Socket do:

        syncano sockets delete mailgun_integration

## Summary

Hope this will help. If you have any question or problems do no hesitate to contact me: sebastian.opalczynski@syncano.com
Also I am available on the Syncano slack community: http://syncano-community.github.io/slack-invite/
