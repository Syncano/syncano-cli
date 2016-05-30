import os

import six
import syncano
from syncano_cli import LOG
from watchdog.events import FileSystemEventHandler

from .project import Project


class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, context):
        con = syncano.connect(api_key=context.key)
        self.instance = con.instances.get(name=context.instance)
        self.project = context.project
        self.context = context
        self.project_file = os.path.relpath(context.file)

    def normalize_path(self, path):
        return os.path.relpath(path)

    def on_change(self, event):
        LOG.debug(event)
        path = self.normalize_path(event.src_path)
        if path == self.project_file:
            try:
                project = Project.from_config(path)
                self.update_changes(project)
            except Exception as e:
                LOG.warning('There was a problem parsing configuration file:'
                            '%s', e)
        else:
            changed_scripts = []
            for script in self.project.scripts:
                if path == self.normalize_path(script['script']):
                    changed_scripts.append(script)
            if changed_scripts:
                self.project.push_to_instance(self.instance,
                                              scripts=changed_scripts,
                                              classes=[])

    def on_modified(self, event):
        self.on_change(event)

    def on_created(self, event):
        self.on_change(event)

    def update_changes(self, new_project):
        LOG.info('checking for changes')

        old_scripts = {s['label']: s for s in self.project.scripts}
        changed_scripts = []
        for script in new_project.scripts:
            label = script['label']
            if label not in old_scripts or script != old_scripts[label]:
                changed_scripts.append(script)

        changed_clasess = []
        old_classes = self.project.classes
        for name, klass in six.iteritems(new_project.classes):
            if name not in old_classes or klass != old_classes[name]:
                changed_clasess.append(klass)
        LOG.debug('changed_clasess: %s', changed_clasess)
        LOG.debug('changed_scripts: %s', changed_scripts)
        new_project.push_to_instance(self.instance, classes=changed_clasess,
                                     scripts=changed_scripts)
        self.project = new_project
