from setuptools import setup


setup(
    name='dj-obj-update',
    version='0.4.0',
    author="Chris Chang",
    author_email='c@crccheck.com',
    url="https://github.com/crccheck/dj-obj-update",
    py_modules=['obj_update'],
    license='Apache License, Version 2.0',
    description='A Django app for adding object tools for models in the admin',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
)
