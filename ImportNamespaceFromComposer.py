import sublime
import sublime_plugin

import os
import re

import json

class ImportNamespaceFromComposerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Filename to namespace
        projectPath = sublime.active_window().project_data()['importNamespaceFromComposer']['project_path']
        filename = self.view.file_name().replace(projectPath, '')
        if filename.startswith('/'):
            filename = filename[1:]

        # Abort if the file is not PHP
        if (not filename.endswith(".php")):
            sublime.error_message("No .php extension")
            return

        # namespace begin at first camelcase dir
        namespaceStmt = os.path.dirname(filename)

        composer = (projectPath + '/composer.json').replace('//', '/')
        with open(composer) as composerFile:
            data = json.load(composerFile)

        for _replace_with, _path in data['autoload']['psr-4'].items():
            if _path.startswith('./'):
                _path = _path[2:]
            if namespaceStmt.startswith(_path):
                namespaceStmt = namespaceStmt.replace(_path, _replace_with)
                namespaceStmt = re.sub('/', '\\\\', namespaceStmt)
                namespaceStmt = namespaceStmt.strip("\\").replace('\\\\', '\\')
                break

        line_contents = '\n\n' + "namespace " + namespaceStmt + ";"

        region = self.view.find(r"^(<\?php){0,1}\s*namespace\s[\w\\]+;", 0)

        if not region.empty():
            self.view.replace(edit, region, '<?php' + line_contents)
            return True

        region = self.view.find(r"<\?php", 0)
        if not region.empty():

            line = self.view.line(region)
            self.view.insert(edit, line.end(), line_contents)
            return True
