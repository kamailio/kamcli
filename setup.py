from setuptools import setup

setup(
    name='kamcli',
    version='1.2.0-dev0',
    packages=['kamcli', 'kamcli.commands'],
    include_package_data=True,
    install_requires=[
        'click',
        'pyaml',
        'sqlalchemy',
        'tabulate',
    ],
    entry_points='''
        [console_scripts]
        kamcli=kamcli.cli:cli
    ''',
)
