from setuptools import setup

setup(
    name='mdt_parser',
    version='0.1',
    py_modules=['mdt_parser', 'mdt_render', 'plain_render'],
    install_requires=[
        'ansiwrap',
        'Click',
        'Mistletoe',
        'prompt_toolkit',
    ],
    entry_points='''
    [console_scripts]
    mdt=mdt_parser:main
    ''',
)
