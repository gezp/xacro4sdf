#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import xml.dom.minidom
import xacro4sdf.xml_format

#model paths list
g_model_paths=[]
if os.getenv("IGN_GAZEBO_RESOURCE_PATH") is not None:
    g_model_paths=g_model_paths+os.getenv("IGN_GAZEBO_RESOURCE_PATH").split(":")
if os.getenv("GAZEBO_MODEL_PATH") is not None:
    g_model_paths=g_model_paths+os.getenv("GAZEBO_MODEL_PATH").split(":")
if os.getenv("XACRO4SDF_MODEL_PATH") is not None:
    g_model_paths=g_model_paths+os.getenv("XACRO4SDF_MODEL_PATH").split(":")

#global vaiables
g_property_table = {}
l_property_table = {}
g_macro_params_table = {}
g_macro_node_table = {}

def try2number(str):
    try:
        return float(str)
    except ValueError:
        return str

# returh a absolute path.
# current_dirname is needed for 'file://'
def parse_uri(uri,current_dirname):
    path = ""
    result=uri.split("://")
    if len(result)!=2:
        return path
    #get absolute path according to uri
    if result[0] == "file":
        #to absolute path
        if(not os.path.isabs(result[1])):
            result[1]=os.path.join(current_dirname,result[1])
        if os.path.isfile(result[1]):
            path = os.path.abspath(result[1])
    elif result[0] == "model":
        for path in g_model_paths:
            file_path = os.path.join(path,result[1])
            if(os.path.isfile(file_path)):
                path = file_path
                break
    return path

def get_xacro(root):
    # only find in <sdf>...</sdf>
    for node in root.childNodes:
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            if node.tagName == 'xacro_define_property':
                name = node.getAttribute("name")
                g_property_table[name] = try2number(node.getAttribute("value"))
            elif node.tagName == 'xacro_define_macro':
                name = node.getAttribute("name")
                g_macro_params_table[name] = node.getAttribute("params").split(' ')
                g_macro_node_table[name] = node.toxml()

def get_include_xacro_recursively(root,abs_dirname):
    for node in root.childNodes:
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            if node.tagName == 'xacro_include_definition':
                uri = node.getAttribute("uri")
                path = parse_uri(uri,abs_dirname)
                if path != "":
                    tmp_doc = xml.dom.minidom.parse(path)
                    tmp_root=tmp_doc.documentElement
                    #get xacro from child recursively
                    get_include_xacro_recursively(tmp_root,os.path.dirname(path))
                    #get xacro from file
                    get_xacro(tmp_doc.documentElement)
                else:
                    print("not find xacro_include_definition uri",uri)
            
def remove_definition_xacro_node(root):
    for node in root.childNodes:
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            if node.tagName == 'xacro_define_property' or node.tagName == 'xacro_define_macro' or node.tagName == 'xacro_include_definition':
                root.removeChild(node)


def replace_inlcude_model_node(node,abs_dirname):
    uri = node.getAttribute("uri")
    path = parse_uri(uri,abs_dirname)
    #get xacro from file
    if path != "":
        parent = node.parentNode
        new_doc = xml.dom.minidom.parse(path).documentElement
        new_nodes = new_doc.getElementsByTagName("model")
        new_node=new_nodes[0]
        for cc in list(new_node.childNodes):
            parent.insertBefore(cc, node)
    else:
        print("not find xacro_include_define uri",uri)
    parent.removeChild(node)

############################################################replace <xacro_macro>
def re_eval_fn(obj):
    result = eval(obj.group(1), g_property_table, l_property_table)
    return str(result)

def eval_text(xml_str):
    pattern = re.compile(r'[$][{](.*?)[}]', re.S)
    return re.sub(pattern, re_eval_fn, xml_str)

def replace_macro_node(node):
    parent = node.parentNode
    if not node.hasAttribute("name"):
        print("check <xacro_macro> block,not find parameter name!")
        sys.exit(1)
    name = node.getAttribute("name")
    # get xml string
    xml_str = g_macro_node_table[name]
    # get local table
    l_property_table.clear()
    for param in g_macro_params_table[name]:
        l_property_table[param] = try2number(node.getAttribute(param))
    # replace macro(insert and remove)
    xml_str = eval_text(xml_str)
    new_node = xml.dom.minidom.parseString(xml_str).documentElement
    for cc in list(new_node.childNodes):
        parent.insertBefore(cc, node)
    parent.removeChild(node)
##############################################################################

#reference: https://github.com/ros/xacro/blob/noetic-devel/src/xacro/__init__.py
def addbanner(doc,input_file_name):
    # add xacro auto-generated banner
    banner = [xml.dom.minidom.Comment(c) for c in
              [" %s " % ('=' * 83),
               " |    This document was autogenerated by xacro4sdf from %-26s | " % input_file_name,
               " |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED  %-30s | " % "",
               " %s " % ('=' * 83)]]
    first = doc.firstChild
    for comment in banner:
        doc.insertBefore(comment, first)

def xacro4sdf(inputfile, outputfile):
    inputfile_dir_path=os.path.dirname(os.path.abspath(inputfile))
    doc = xml.dom.minidom.parse(inputfile)
    root = doc.documentElement
    ################# get xacro defination(store macro defination to dictionary)
    # get common xacro (lowest priority,it can be overwrited)
    common_xacro_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'common.xacro')
    get_xacro(xml.dom.minidom.parse(common_xacro_path).documentElement)
    # get inlcude xacro recursively (the priority depends on the order of tag<xacro_include_definition>)
    get_include_xacro_recursively(root,inputfile_dir_path)
    # get current xacro (highest priority)
    get_xacro(root)
    # remove xacro defination (<xacro_define_property>,<xacro_define_macro>,<xacro_include_definition>)
    remove_definition_xacro_node(root)
    ################# relapce xacro
    # replace xacro include model 
    nodes = doc.getElementsByTagName("xacro_include_model")
    if nodes.length != 0:
        for node in list(nodes):
            replace_inlcude_model_node(node,inputfile_dir_path)
    if doc.getElementsByTagName("xacro_inlcude_model").length != 0:
        print("Error:The nesting of xacro_include_model is not supported!")
        sys.exit(1)
    # replace xacro property (doc -> doc, process by string regular expression operations)
    l_property_table.clear()
    xml_str = root.toxml()
    xml_str = eval_text(xml_str)
    doc = xml.dom.minidom.parseString(xml_str)
    # replace xacro macro
    for _ in range(5):
        nodes = doc.getElementsByTagName("xacro_macro")
        if nodes.length == 0:
            break
        else:
            for node in list(nodes):
                replace_macro_node(node)
    #check
    if doc.getElementsByTagName("xacro_macro").length != 0:
        print("Error:The nesting of macro defination is much deep! only support <=5")
        sys.exit(1)
    ################## output
    addbanner(doc,inputfile)
    try:
        with open(outputfile, 'w', encoding='UTF-8') as f:
            doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='UTF-8')
    except Exception as err:
        print('output error:{0}'.format(err))


def main():
    if(len(sys.argv) >= 2):
        inputfile = sys.argv[1]
        outputfile = os.path.splitext(inputfile)[0]
        if os.path.splitext(inputfile)[1] == '.xacro':
            # run xacro4sdf
            xacro4sdf(inputfile, outputfile)
            return 0
    #error
    print("usage: xacro4sdf <inputfile> (the name of inputfile must be xxx.xacro)")

if __name__ == '__main__':
    main()