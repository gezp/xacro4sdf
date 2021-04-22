#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import xml.dom.minidom
import xacro4sdf.xml_format


def try2number(str):
    try:
        return float(str)
    except ValueError:
        return str

class XMLMacro:
    def __init__(self):
        # variables for xml parse
        self.local_property_dict={} 
        self.global_property_dict={}
        self.macro_params_dict={}
        self.macro_content_dict={}
        self.xmacro_paths=[]
        # variables for xml info
        self.filename=""
        self.dirname=""
        self.in_doc=None
        self.out_doc=None
        self.parse_flag=False
        #init
        if os.getenv("IGN_GAZEBO_RESOURCE_PATH") is not None:
            self.xmacro_paths=self.xmacro_paths+os.getenv("IGN_GAZEBO_RESOURCE_PATH").split(":")
        if os.getenv("GAZEBO_MODEL_PATH") is not None:
            self.xmacro_paths=self.xmacro_paths+os.getenv("GAZEBO_MODEL_PATH").split(":")
        if os.getenv("XACRO4SDF_MODEL_PATH") is not None:
            self.xmacro_paths=self.xmacro_paths+os.getenv("XACRO4SDF_MODEL_PATH").split(":")

####private funtion 
    # returh a absolute path.
    def __parse_uri(self,uri,current_dirname):
        #current_dirname is needed for 'file://'
        result = ""
        splited_str=uri.split("://")
        if len(splited_str)!=2:
            return result
        #get absolute path according to uri
        if splited_str[0] == "file":
            #to absolute path
            if(not os.path.isabs(splited_str[1])):
                splited_str[1]=os.path.join(current_dirname,splited_str[1])
            if os.path.isfile(splited_str[1]):
                result = os.path.abspath(splited_str[1])
        elif splited_str[0] == "model":
            for tmp_path in self.xmacro_paths:
                tmp_path = os.path.join(tmp_path,splited_str[1])
                if(os.path.isfile(tmp_path)):
                    result = tmp_path
                    break
        return result

    def __get_xacro(self,doc):
        # only find in <sdf>...</sdf>
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xacro_define_property':
                    name = node.getAttribute("name")
                    self.global_property_dict[name] = try2number(node.getAttribute("value"))
                elif node.tagName == 'xacro_define_macro':
                    name = node.getAttribute("name")
                    self.macro_params_dict[name] = node.getAttribute("params").split(' ')
                    self.macro_content_dict[name] = node.toxml()

    def __get_include_xacro_recursively(self,doc,dirname):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xacro_include_definition':
                    uri = node.getAttribute("uri")
                    filepath = self.__parse_uri(uri,dirname)
                    if filepath != "":
                        tmp_doc = xml.dom.minidom.parse(filepath)
                        #get xacro from child recursively
                        self.__get_include_xacro_recursively(tmp_doc,os.path.dirname(filepath))
                        #get xacro from file
                        self.__get_xacro(tmp_doc)
                    else:
                        print("Error: not find xacro_include_definition uri",uri)
                        sys.exit(1)
        
    def __remove_definition_xacro_node(self,doc):
        root = doc.documentElement
        for node in root.childNodes:
            if node.nodeType == xml.dom.Node.ELEMENT_NODE:
                if node.tagName == 'xacro_define_property' \
                    or node.tagName == 'xacro_define_macro' \
                    or node.tagName == 'xacro_include_definition':
                    root.removeChild(node)

    def __re_eval_fn(self,obj):
        result = eval(obj.group(1), self.global_property_dict, self.local_property_dict)
        return str(result)

    def __eval_text(self,xml_str):
        pattern = re.compile(r'[$][{](.*?)[}]', re.S)
        return re.sub(pattern, self.__re_eval_fn, xml_str)
            
    def __replace_macro_node(self,node):
        parent = node.parentNode
        if not node.hasAttribute("name"):
            print("Error: check <xacro_macro> block,not find parameter name!")
            sys.exit(1)
        name = node.getAttribute("name")
        # get xml string
        xml_str = self.macro_content_dict[name]
        # get local table
        self.local_property_dict.clear()
        for param in self.macro_params_dict[name]:
            self.local_property_dict[param] = try2number(node.getAttribute(param))
        # replace macro(insert and remove)
        xml_str = self.__eval_text(xml_str)
        new_node = xml.dom.minidom.parseString(xml_str).documentElement
        for cc in list(new_node.childNodes):
            parent.insertBefore(cc, node)
        parent.removeChild(node)



####public funtion
    def set_xml_file(self,filepath):
        self.filename=filepath
        self.dirname=os.path.dirname(os.path.abspath(filepath))
        self.in_doc = xml.dom.minidom.parse(filepath)
        self.parse_flag=False

    def set_xml_string(self,xml_str):
        self.dirname=os.path.dirname(os.path.abspath(__file__))
        self.in_doc = xml.dom.minidom.parse(xml_str)
        self.parse_flag=False

    def parse(self):
        # get xacro defination from in_doc(store macro's defination to dictionary)
        # get common xacro (lowest priority,it can be overwrited)
        common_xacro_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'common.xmacro')
        self.__get_xacro(xml.dom.minidom.parse(common_xacro_path))
        # get inlcude xacro recursively (the priority depends on the order of tag<xacro_include_definition>)
        self.__get_include_xacro_recursively(self.in_doc,self.dirname)
        # get current xacro (highest priority)
        self.__get_xacro(self.in_doc)
        # remove xacro defination (<xacro_define_property>,<xacro_define_macro>,<xacro_include_definition>)
        self.__remove_definition_xacro_node(self.in_doc)
        self.parse_flag=True

    def generate(self):
        if self.in_doc is None:
            self.out_doc=None
            return
        if not self.parse_flag:
            self.parse()
        # generate out_doc by relapcing xacro macro
        # replace global xacro property (process by string regular expression operations)
        self.local_property_dict.clear()
        xml_str = self.in_doc.documentElement.toxml()
        xml_str = self.__eval_text(xml_str)
        self.out_doc = xml.dom.minidom.parseString(xml_str)
        # replace xacro macro 
        for _ in range(5):
            nodes = self.out_doc.getElementsByTagName("xacro_macro")
            if nodes.length != 0:
                for node in list(nodes):
                    self.__replace_macro_node(node)
            else:
                break
        #check
        if self.out_doc.getElementsByTagName("xacro_macro").length != 0:
            print("Error:The recursive depth of macro defination only support <=5")
            self.out_doc=None
            return

    def to_string(self):
        if self.out_doc is None:
            return None
        return self.out_doc.documentElement.toxml()

    def to_file(self,filepath,banner_info=None):
        # auto-generated banner
        # reference: https://github.com/ros/xacro/blob/noetic-devel/src/xacro/__init__.py
        if self.out_doc is None:
            return None
        src = "python script"
        if self.filename != "":
            src = self.filename 
        if banner_info is not None:
            src=banner_info
        banner = [xml.dom.minidom.Comment(c) for c in
              [" %s " % ('=' * 83),
               " |    This document was autogenerated by xacro4sdf from %-26s | " % src,
               " |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED  %-30s | " % "",
               " %s " % ('=' * 83)]]
        first = self.out_doc.firstChild
        for comment in banner:
            self.out_doc.insertBefore(comment, first)
        #write to file
        try:
            with open(filepath, 'w', encoding='UTF-8') as f:
                self.out_doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='UTF-8')
        except Exception as err:
            print('to_file error:{0}'.format(err))

def xacro4sdf_main():
    if(len(sys.argv) < 2):
        print("Usage: xacro4sdf <inputfile> (the name of inputfile must be xxx.xmacro)")
        return -1
    inputfile = sys.argv[1]
    outputfile = os.path.splitext(inputfile)[0]
    #check
    if os.path.splitext(inputfile)[1] != '.xmacro' and os.path.splitext(inputfile)[1] != '.xacro':
        print("Error: the name of inputfile must be xxx.xmacro")
        return -2
    #warn
    if os.path.splitext(inputfile)[1] == '.xacro':
        print("Warning: inputfile with xxx.xmacro is recommanded to show the difference from ros/xacro")     
    #process 
    xmacro=XMLMacro()
    xmacro.set_xml_file(inputfile)
    xmacro.generate()
    xmacro.to_file(outputfile)
    return 0
    

if __name__ == '__main__':
    xacro4sdf_main()