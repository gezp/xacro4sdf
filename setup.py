#!/usr/bin/python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='xacro4sdf',  
    version='2.0.0',  
    author='Zhenpeng Ge',  
    author_email='zhenpeng.ge@qq.com', 
    url='https://github.com/gezp/xacro4sdf', 
    description='a simple XML macro script for sdf, like ros/xacro which is desiged for urdf.',  
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords=['sdf','sdformat','xacro', 'gazebo', 'ignition'],
    include_package_data=True,
    packages=find_packages(),
    entry_points={ 
        'console_scripts': [
            'xacro4sdf=xacro4sdf:xacro4sdf_main',
        ]
    }
)
