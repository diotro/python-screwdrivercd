# Copyright 2019, Oath Inc.
# Licensed under the terms of the Apache 2.0 license.  See the LICENSE file in the project root for terms
import os
import tempfile
import unittest
from pathlib import Path
import screwdrivercd.documentation.exceptions
import screwdrivercd.documentation.plugin
import screwdrivercd.documentation.mkdocs.plugin
import screwdrivercd.documentation.sphinx.plugin

from . import ScrewdriverTestCase


class PluginsTestCase(ScrewdriverTestCase):

    def test__documentation_plugins__present(self):
        names = [_.name for _ in screwdrivercd.documentation.plugin.documentation_plugins()]
        self.assertIn('mkdocs', names)
        self.assertIn('sphinx', names)


class DocumentationPluginTestCase(ScrewdriverTestCase):
    plugin_class = screwdrivercd.documentation.plugin.DocumentationPlugin

    def _create_test_repo_contents(self):
        pass

    def _init_test_repo(self):
        os.system('git init')
        os.system('git config user.email "foo@bar.com"')
        os.system('git config user.name "foo the bar"')
        os.system('git remote add origin https://github.com/yahoo/python-screwdrivercd.git')

    def test__get_clone_url(self):
        self._init_test_repo()
        p = screwdrivercd.documentation.plugin.DocumentationPlugin()
        result = p.get_clone_url()
        self.assertEqual(result, 'https://github.com/yahoo/python-screwdrivercd.git')

    def test__get_clone_dir(self):
        self._init_test_repo()
        p = screwdrivercd.documentation.plugin.DocumentationPlugin()
        result = p.get_clone_dir()
        self.assertEqual(result, 'python-screwdrivercd')

    def test__clone_url(self):
        self._init_test_repo()
        p = screwdrivercd.documentation.plugin.DocumentationPlugin()
        result = p.clone_url
        self.assertEqual(result, 'https://github.com/yahoo/python-screwdrivercd.git')

    def test__clone_dir(self):
        self._init_test_repo()
        p = screwdrivercd.documentation.plugin.DocumentationPlugin()
        result = p.clone_dir
        self.assertEqual(result, 'python-screwdrivercd')

    def test_documentation_base_plugin_is_present(self):
        p = screwdrivercd.documentation.plugin.DocumentationPlugin()
        self.assertFalse(p.documentation_is_present)

    def test_documentation_base__log_message(self):
        p = self.plugin_class()
        p.build_log_filename = 'foo.log'
        p._log_message('foo', p.build_log_filename)
        self.assertTrue(os.path.exists('foo.log'))
        with open('foo.log') as log:
            self.assertEqual('foo\n', log.read())

    def test_documentation__base__run_command(self):
        p = self.plugin_class()
        p.build_log_filename = 'foo.log'
        p._run_command(['echo', 'hello'], log_filename=p.build_log_filename)
        self.assertTrue(os.path.exists('foo.log'))
        with open('foo.log') as log:
            self.assertEqual('hello\n', log.read())

    def test_documentation__base__run_command__error(self):
        p = self.plugin_class()
        p.build_log_filename = 'foo.log'
        with self.assertRaises(screwdrivercd.documentation.exceptions.DocBuildError):
            p._run_command(['./exit', '1'], log_filename=p.build_log_filename)

    def test__documentation__build(self):
        self._create_test_repo_contents()
        p = self.plugin_class()
        p.build_documentation()
        self.assertTrue(os.path.exists(f'{p.log_dir}/{p.name}.build.log'))

    def test__remove_build_log(self):
        p = self.plugin_class()
        p.build_log_filename = os.path.join(self.tempdir.name, 'build.log')
        Path(p.build_log_filename).touch()
        self.assertTrue(os.path.exists(p.build_log_filename))
        p.remove_build_log()
        self.assertFalse(os.path.exists(p.build_log_filename))

    def test__remove_publish_log(self):
        p = self.plugin_class()
        p.publish_log_filename = os.path.join(self.tempdir.name, 'publish.log')
        Path(p.publish_log_filename).touch()
        self.assertTrue(os.path.exists(p.publish_log_filename))
        p.remove_publish_log()
        self.assertFalse(os.path.exists(p.publish_log_filename))

    def test__clean_directory(self):
        p = self.plugin_class()
        testdir = Path(self.tempdir.name) / 'testdir'
        testdir.mkdir(exist_ok=True)
        testfile = testdir / 'testfile'
        testfile.touch()
        p.clean_directory(str(testdir))
        self.assertFalse(testfile.exists())

    def test__copy_contents(self):
        dir1 = Path(self.tempdir.name) / 'dir1'
        dir2 = Path(self.tempdir.name) / 'dir2'
        srctestfile = dir1 / 'testfile'
        srctestdotfile = dir1 / '.testfile'
        dsttestfile = dir2 / 'testfile'
        dsttestdotfile = dir2 / '.testfile'

        dir1.mkdir(exist_ok=True)
        dir2.mkdir(exist_ok=True)
        srctestfile.touch()
        srctestdotfile.touch()

        p = self.plugin_class()
        p.copy_contents(str(dir1), str(dir2))

        self.assertTrue(dsttestfile.exists())
        self.assertTrue(dsttestdotfile.exists())


class SphinxDocumentationPluginTestCase(DocumentationPluginTestCase):
    plugin_class = screwdrivercd.documentation.sphinx.plugin.SphinxDocumentationPlugin

    def _create_test_repo_contents(self):
        os.makedirs('doc/source')

    def test__documentation__build(self):
        pass


class MkdocsDocumentationPluginTestCase(DocumentationPluginTestCase):
    plugin_class = screwdrivercd.documentation.mkdocs.plugin.MkDocsDocumentationPlugin

    def _create_test_repo_contents(self):
        os.makedirs('docs')

    def test__documentation__build(self):
        pass
