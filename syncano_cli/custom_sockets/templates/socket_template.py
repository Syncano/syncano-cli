
SOCKET_YML = """
name: custom_socket_example
author:
  name: Info
  email: info@synano.com
icon:
  name: icon-name
  color: ffee11
config:
  constants:
    some_key: some_value
  prompt:
    custom_api_key:
      type: sting
      description: an Api Key for third party service
description: Some custom integration
endpoints:
  custom_endpoint:
    script: custom_script

  custom_endpoint_1:
    POST:
      script: custom_script_1
    GET:
      script: custom_script_2

dependencies:
  scripts:
    custom_script:
      runtime_name: python_library_v5.0
      file: scripts/custom_script.py
    custom_script_1:
      runtime_name: python_library_v5.0
      file: scripts/custom_script_1.py
    custom_script_2:
      runtime_name: python_library_v5.0
      file: scripts/custom_script_2.py

  classes:
    country:
      schema:
        - name: name
          type: string
        - name: topLevelDomain
          type: string
        - name: capital
          type: string
        - name: alpha2Code
          type: string
        - name: alpha3Code
          type: string
"""

SCRIPTS = {
    'scripts/custom_script.py': """static_data = {
    'title': 'Hunger games',
    'author': 'Suzzane Collins',
    'publish_year': 2008,
}

set_response(HttpResponse(status_code=200, content=static_data, content_type='application/json'))
""",
    'scripts/custom_script_1.py': "print('1')",
    'scripts/custom_script_2.py': "print('2')"
}
