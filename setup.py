import os
from setuptools import setup

# variables used in buildout
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'attrs==16.0.0',
    'py==1.4.31',
    'python-magic==0.4.12',
    'requests==2.11.0',
    'wheel==0.24.0',
    'xlrd==1.0.0',
    'xlwt==1.1.2',
    'awscli==1.10.62',
    'Pillow==3.3.0',
]

tests_require = [
    'pytest>=3.0.1',
    'pytest-mock',
    'pytest-cov',
]

setup(
    name='Submit4DN',
    version=open("wranglertools/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description='Tools for data wrangling and submission to data.4dnucleome.org',
    packages=['wranglertools'],
    zip_safe=False,
    author='4DN Team at Harvard Medical School',
    author_email='jeremy_johnson@hms.harvard.edu',
    url='http://data.4dnucleome.org',
    license='MIT',
    install_requires=requires,
    include_package_data=True,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    setup_requires=['pytest-runner', ],
    entry_points='''
        [console_scripts]
        import_data  = wranglertools.import_data:main
        get_field_info = wranglertools.get_field_info:main
        ''',
)
