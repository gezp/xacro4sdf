#!/bin/python3
from xacro4sdf.xacro4sdf import XMLMacro

xmacro=XMLMacro()
#case1 parse from file
xmacro.set_xml_file("model.sdf.xmacro")
custom_property={"rplidar_a2_h":0.8}
xmacro.generate(custom_property)
xmacro.to_file("custom.sdf",banner_info="test_custom_usage.py")