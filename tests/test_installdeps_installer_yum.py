#!/usr/bin/env python
# Copyright 2019, Oath Inc.
# Licensed under the terms of the Apache 2.0 license.  See the LICENSE file in the project root for terms
import os
import tempfile
import unittest.mock

import distro
from screwdrivercd.installdeps.installers.yum import YumInstaller
from screwdrivercd.utility.contextmanagers import InTemporaryDirectory


CONFIG_FILE = 'pyproject.toml'
TEST_CONFIG = f'''[build-system]
# Minimum requirements for the build system to execute.
requires = ["setuptools", "wheel"]  # PEP 508 specifications.

[tool.sdv4_installdeps]
    install = ['apk', 'apt-get', 'yinst', 'yum', 'pip3']

    [tool.sdv4_installdeps.yum]
        repos.verizon_python_rpms = "https://edge.artifactory.yahoo.com:4443/artifactory/python_rpms/python_rpms.repo"
        deps = [
            'yahoo_python36;distro_version=="{distro.version()}"',
            'yahoo_python37;distro_version>="7.5"',
            'mysql;distro_version<"7"',
            'mariadb;distro_version>="7"'
        ]

'''


class TestYum(unittest.TestCase):
    original_environ = None

    def setUp(self):
        self._cwd = os.getcwd()
        super().setUp()
        self.original_environ = os.environ
        self.tempdir = tempfile.TemporaryDirectory()
        os.chdir(self.tempdir.name)
        with open(CONFIG_FILE, 'w') as config_handle:
            config_handle.write(TEST_CONFIG)

    def tearDown(self):
        super().tearDown()
        if self.original_environ:
            os.environ = self.original_environ
            self.original_environ = None
        os.chdir(self._cwd)
        self.tempdir.cleanup()

    @unittest.skipUnless(os.path.exists('/bin/yum'), 'No yum binary present on system')
    def test__install__default(self):
        installer = YumInstaller(dry_run=True)
        result = installer.install_dependencies()
        self.assertIn('yahoo_python36', result)
