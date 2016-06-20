# -*- coding: utf-8 -*-
from syncano.models import RuntimeChoices
from syncano_cli.config import ACCOUNT_CONFIG
from syncano_cli.main import cli
from tests.base import BaseCLITest


class ExecuteCommandsTest(BaseCLITest):

    def setUp(self):
        self.runner.invoke(cli, args=['login'], obj={})
        self.assert_config_variable_exists(ACCOUNT_CONFIG, 'DEFAULT', 'key')

    def _create_script_endpoint(self, source, name_prefix):
        script = self.instance.scripts.create(
            label='test_script',
            source=source,
            runtime_name=RuntimeChoices.PYTHON_V5_0,
        )

        self.instance.script_endpoints.create(
            name='{}_test_script_endpoint'.format(name_prefix),
            script=script.id
        )

    def test_script_endpoint_error(self):
        name_prefix = 'error_response'
        self._create_script_endpoint(
            source='print(12/0)',
            name_prefix=name_prefix
        )

        result = self.runner.invoke(cli, args=[
            'execute', self.instance.name, '{}_test_script_endpoint'.format(name_prefix)
        ], obj={})

        self.assertIn('ZeroDivisionError', result.output)

    def test_script_endpoint(self):
        name_prefix = 'normal_response'
        self._create_script_endpoint(
            source='print(12)',
            name_prefix=name_prefix
        )

        result = self.runner.invoke(cli, args=[
            'execute', self.instance.name, '{}_test_script_endpoint'.format(name_prefix)
        ], obj={})

        self.assertEqual(result.output, '12\n')

    def test_script_endpoint_with_payload(self):
        name_prefix = 'payload_response'

        self._create_script_endpoint(
            source="print(ARGS['POST']['data'])",
            name_prefix=name_prefix
        )

        result = self.runner.invoke(cli, args=[
            'execute', self.instance.name, '{}_test_script_endpoint'.format(name_prefix),
            '--payload', '{"data": "some nice string"}'
        ], obj={})
        print(result.exception)
        self.assertEqual(result.output, 'some nice string\n')

    def test_script_endpoint_custom_response(self):
        name_prefix = 'custom_response'

        self._create_script_endpoint(
            source="""set_response(
            HttpResponse(
                status_code=200,
                content='{"test": "amazing thing"}',
                content_type='application/json'
                )
            )
            """,
            name_prefix=name_prefix
        )

        result = self.runner.invoke(cli, args=[
            'execute', self.instance.name, '{}_test_script_endpoint'.format(name_prefix)
        ], obj={})

        self.assertEqual(result.output, """{\n    "test": "amazing thing"\n}\n""")
