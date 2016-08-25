# Syncano Custom Sockets

## YML file structure

    name: my_tweet
    description: Twitter integration  
    author:
      name: Maciek
      email: maciek@synano.com
    icon:
      name: icon_name
      color: red
    endpoints:
      my_endpoint_1:
        script: script_endpoint_1
    
      my_endpoint_2:
        template: template_name
        cache: cache_key
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
