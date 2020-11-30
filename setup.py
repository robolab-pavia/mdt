from setuptools import setup

setup(
    name='mdt_parser',
    version='0.1',
    py_modules=['mdt_parser'],
    install_requires=[
        'Click',
        'Mistletoe',
        'prompt_toolkit',
    ],
    entry_points='''
    [console_scripts]
    mdt=mdt_parser:mdt
    ''',
)