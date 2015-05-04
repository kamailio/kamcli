from setuptools import setup

setup(
    name='kamcli',
    version='1.0',
    packages=['kamcli', 'kamcli.commands'],
    include_package_data=True,
    install_requires=[
        'click',
        'sqlalchemy',
    ],
    entry_points='''
        [console_scripts]
        kamcli=kamcli.cli:cli
    ''',
)
