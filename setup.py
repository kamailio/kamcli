from setuptools import setup

setup(
    name="kamcli",
    version="3.0.0",
    packages=["kamcli", "kamcli.commands"],
    include_package_data=True,
    install_requires=[
        "setuptools",
        "click",
        "prompt-toolkit",
        "pyaml",
        "pygments",
        "sqlalchemy",
        "tabulate",
        "wheel",
    ],
    entry_points="""
        [console_scripts]
        kamcli=kamcli.cli:cli
    """,
)
