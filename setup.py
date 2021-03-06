"""
Install portal via setuptools
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as testcommand

with open('test_requirements.txt') as test_reqs:
    TESTS_REQUIRE = test_reqs.readlines()

with open('README.rst') as readme_file:
    README = readme_file.read()


class PyTest(testcommand):
    """PyTest class to enable running `python setup.py test`"""
    user_options = testcommand.user_options[:]
    user_options += [
        ('coverage', 'C', 'Produce a coverage report for portal'),
        ('pep8', 'P', 'Produce a pep8 report for portal'),
        ('pylint', 'l', 'Produce a pylint report for portal'),
    ]
    coverage = None
    pep8 = None
    lint = None
    test_suite = False
    test_args = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.test_suite = True
        self.test_args = []
        if self.coverage:
            self.test_args.extend(['--cov', 'portal'])
        if self.pep8:
            self.test_args.append('--pep8')
        if self.lint:
            self.test_args.append('--lint')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        # Needed in order for pytest_cache to load properly
        # Alternate fix: import pytest_cache and pass to pytest.main
        import _pytest.config

        plugin_manager = _pytest.config.get_plugin_manager()
        plugin_manager.consider_setuptools_entrypoints()
        sys.exit(pytest.main(self.test_args))

setup(
    name='portal',
    version='0.3.0',
    license='AGPLv3',
    author='MIT ODL Engineering',
    author_email='odl-engineering@mit.edu',
    url='http://github.com/mitodl/portal',
    description="Teacher's Portal",
    long_description=README,
    packages=find_packages(),
    install_requires=[
        'Django',
        'PyYAML',
        'dj-database-url',
        'dj-static',
        'uwsgi',
        'psycopg2',
        'tox',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python',
    ],
    test_suite="portal.tests",
    tests_require=TESTS_REQUIRE,
    cmdclass={"test": PyTest},
    include_package_data=True,
    zip_safe=False,
)
