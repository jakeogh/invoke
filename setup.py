from setuptools import setup

setup(
    name='click-example-invoke',
    version='1.0',
    py_modules=['invoke'],
    include_package_data=True,
    install_requires=['click'],
    entry_points='''
        [console_scripts]
        invoke=invoke:cli
    ''',
)
