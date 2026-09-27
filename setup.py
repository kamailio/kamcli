from setuptools import setup

setup(
    name="kamcli",
    version="3.0.0",
    packages=["kamcli", "kamcli.commands"],
    include_package_data=True,
    setup_requires=[
        "setuptools",
        "wheel",
    ],
    install_requires=[
        "click",
        "prompt-toolkit",
        "pyaml",
        "pygments",
        "sqlalchemy>=2.0",
        "tabulate",
    ],
    entry_points="""
        [console_scripts]
        kamcli=kamcli.cli:cli
    """,
)
