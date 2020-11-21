#!/usr/bin/python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='xacro4sdf',  
    version='1.0.0',  
    author='Ge Zhenpeng',  
    author_email='zhenpeng.ge@qq.com', 
    url='https://github.com/robomaster-oss/xacro4sdf', 
    description='a simple XML macro script for sdf, like ros/xacro which is desiged for urdf.',  
    license='MIT',
    keywords=['sdf', 'xacro', 'gazebo', 'ignition'],
    include_package_data=True,
    packages=find_packages(),
    entry_points={ 
        'console_scripts': [
            'xacro4sdf=xacro4sdf:main',
        ]
    }
)