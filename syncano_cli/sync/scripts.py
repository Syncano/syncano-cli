# coding=UTF8
from __future__ import print_function, unicode_literals

import os
import re
from collections import defaultdict

import click
import six
from syncano.exceptions import SyncanoRequestError

ALLOWED_RUNTIMES = {
    'golang': '.go',
    'nodejs': '.js',
    'nodejs_library_v0.4': '.js',
    'nodejs_library_v1.0': '.js',
    'php': '.php',
    'python': '.py',
    'python3': '.py',
    'python_library_v4.2': '.py',
    'python_library_v5.0': '.py',
    'ruby': '.rb',
    'swift': '.swift',
}


def get_runtime_extension(runtime):
    try:
        return ALLOWED_RUNTIMES[runtime]
    except KeyError:
        raise ValueError('Runtime name "%s" not recognized' % runtime)


def filename_for_script(script):
    ext = get_runtime_extension(script.runtime_name)
    filename = re.sub(r'[\s/\\]', '_', script.label)

    if not filename.endswith(ext):
        filename += ext
    return filename


def pull_scripts(instance, include):
    """
    Pull scripts from instance and store them in scripts directory.
    If scripts is empty list all scripts are pulled, otherwise script
    label has to be in a list. Script labels are changed to be compatibile with
    file names. All whitespaces, slashes and backslashes are replaced with '_'.
    """
    pulled = []
    seen_names = {}
    seen_labels = set()

    if not os.path.exists('scripts'):
        click.echo("INFO: Creating scripts directory")
        os.makedirs('scripts')

    script_endpoints = defaultdict(list)
    for endpoint in instance.script_endpoints.all():
        script_endpoints[endpoint.script].append(endpoint.name)

    for script in instance.scripts.all():

        if include and script.label not in include:
            continue

        if script.label in seen_labels:
            raise ValueError('There is more than 1 script with label {0.label}'
                             .format(script))
        seen_labels.add(script.label)

        filename = filename_for_script(script)

        if filename in seen_names:
            click.echo("WARN: Script {0.label}({0.id}) label clashes with"
                       " script {1.label}({1.id}). Skipping."
                       .format(script, seen_names[filename]))
            continue
        seen_names[filename] = script

        if filename != script.label:
            click.echo('WARN: Saving script "{0}" as "{1}"'.format(script.label,
                                                                   filename))

        path = os.path.join('scripts', filename)

        with open(path, 'wt') as script_file:
            script_file.write(script.source)

        script_info = {
            'label': script.label,
            'script': path,
            'runtime': script.runtime_name
        }
        if script.id in script_endpoints:
            script_info['endpoints'] = script_endpoints[script.id]

        if script.config:
            script_info['config'] = script.config

        pulled.append(script_info)
    return pulled


def push_scripts(instance, scripts, config_only=True):
    """
    Push selected scripts to instance.
        - instance - instance object to push scripts to
        - scripts - a list of dictionaries containing configurations for
                    scripts
    """
    click.echo('INFO: Pushing scripts')
    click.echo('INFO: Pulling remote scripts')

    endpoints = {}
    remote_scripts_mapping = defaultdict(list)
    for remote_script in instance.scripts.all():
        remote_scripts_mapping[remote_script.label].append(remote_script)

    existing_endpoints = defaultdict(list)

    for endpoint in instance.script_endpoints.all():
        existing_endpoints[endpoint.script].append(endpoint.name)
        endpoints[endpoint.name] = endpoint

    click.echo('INFO: Pushing local scripts')
    for s in scripts:
        if s['label'] in remote_scripts_mapping:
            remote_count = len(remote_scripts_mapping[s['label']])
            if remote_count > 1:
                click.error('ERROR: You have {0} scripts with label {1} on'
                            ' syncano. Skipping'.format(remote_count, s['label']))
                continue
            remote_script = remote_scripts_mapping[s['label']][0]
        else:
            remote_script = instance.scripts.model(
                label=s['label'],
                runtime_name=s['runtime'],
                instance_name=instance.name,
                config={}
            )
        with open(s['script'], 'rb') as source:
            remote_script.source = source.read()

        config = s.get('config', {})
        remote_script.config.update(config)

        click.echo('INFO: Pushing script {label}'.format(**s))
        remote_script.save()

        existing_set = {name for name in existing_endpoints[remote_script.id]}
        script_endpoints = set(s.get('endpoints', []))
        new_endpoints = script_endpoints - existing_set
        old_endpoints = existing_set - script_endpoints

        for name in old_endpoints:
            endpoints[name].delete()

        for name in new_endpoints:
            endpoint = instance.script_endpoints.model(
                instance_name=instance.instance_name,
                name=name,
                script=remote_script.id
            )
            try:
                endpoint.save()
            except SyncanoRequestError as e:
                raise ValueError(
                    'Error when saving endpoint "{0}" for script "{1}": {2}.'
                    .format(name, remote_script.label, e.message)
                )


def validate_script(script):
    if not script.get('label'):
        raise ValueError('You have to provide script label.')

    source = script.get('script')
    if source is None:
        raise ValueError('You have to provide script source for script '
                         '"{label}"'.format(**script))

    if not os.path.exists(source):
        raise ValueError(
            'Could not find script "{source}" file'.format(**script)
        )

    runtime = script.get('runtime')
    if not runtime:
        ext = os.path.splitext(source)[1]
        click.echo(
            'WARN: Runtime for script {label} not provided. Guessing runtime basing'
            'on file extension'.format(**script)
        )

        for k, v in six.iteritems(ALLOWED_RUNTIMES):
            if v == ext:
                script['runtime'] = runtime = k
                click.echo(
                    'WARN: Using runtime {runtime} for script {label}'.format(
                        **script
                    )
                )
                break


def validate_scripts(scripts):
    for s in scripts:
        validate_script(s)
