# xacro4sdf

![PyPI](https://img.shields.io/pypi/v/xacro4sdf)  ![](https://img.shields.io/pypi/l/xacro4sdf) ![](https://img.shields.io/pypi/dm/xacro4sdf)

`xacro4sdf` is a simple tool to define and parse XML macro for [sdf (sdformat)](http://sdformat.org/), you can use `xacro4sdf` to write modularized SDF xml (not nest model) 

* xacro4sdf is similar, but different from  [ros/xacro](https://github.com/ros/xacro) which is desiged for urdf. 
* xacro4sdf is more simple, but it's also more easy to use.

> Reference: [ros/xacro](https://github.com/ros/xacro)
>
> * With Xacro, you can construct shorter and more readable XML files by using macros that expand to larger XML expressions. 

**Attention:**

* `<xacro_include_model>` is departed after version2.0.0,  you can use  the tag with version1.2.6.

## 1. Usage

**Installation**

```bash
#install by pip
pip install xacro4sdf 
# or install from source code
# git clone https://github.com/gezp/xacro4sdf.git
# cd xacro4sdf && sudo python3 setup.py install
```

**create model.sdf.xmacro file**

* refer to files in `test/`  (for example `test/model.sdf.xmacro`)

**generate  model.sdf**

```bash
#cd test
xacro4sdf model.sdf.xmacro
```

* it will generate model.sdf (the result should be same as test/model.sdf)
* more examples can be found `test` folder.

**summary of XML Tags**

* definition of property and macro : core function
  * `<xacro_define_property>` and `<xacro_define_macro>`
* include 
  * `<xacro_include_definition>` :include definition of property and macro from other xmacro file
* use of property and macro:
  * `${xxx}` : use of property ,it's very useful to use math expressions.
  * `<xacro_macro>` : use of macro, it's very useful for modular modeling.

> Tip:
>
> * the xacro defination (`<xacro_define_property>` , `<xacro_define_macro>` and  `<xacro_include_definition>`) must be child node of root node `<sdf>` .

## 2. Features

* Properties	
* Macros
* Math expressions
* Include

### 2.1. Properties

Properties are named values that can be inserted anywhere into the XML document

**xacro definition**

```xml
<!--definition of properties -->
<xacro_define_property name="radius" value="4.3" />
<!--use of properties-->
<circle diameter="${2 * radius}" />
```

**generated xml**

```xml
<circle diameter="8.6" />
```

### 2.2. Macros

The main feature of `xacro4sdf` is macros.

Define macros with the macro tag `<xacro_define_property>`, then specify the macro name and a list of parameters. The list of parameters should be whitespace separated. 

The  usage of Macros is to define `<xacro_macro>` which will be replaced with `<xacro_define_property>`  block  according to the param `name`.

**xacro definition**

```xml
<!--definition of macro-->
	<xacro_define_property name="mass" value="0.2" />
	<xacro_define_macro macro_name="box_inertia" params="m x y z">
        <mass>${m}</mass>
        <inertia>
            <ixx>${m*(y*y+z*z)/12}</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>${m*(x*x+z*z)/12}</iyy>
            <iyz>0</iyz>
            <izz>${m*(x*x+z*z)/12}</izz>
        </inertia>
    </xacro_macro_define>
<!--use of macro-->
            <inertial>
                <pose>0 0 0.02 0 0 0</pose>
                <xacro_macro name="box_inertia" m="${mass}" x="0.3" y="0.1" z="0.2"/>
            </inertial>
```

**generated xml**

```xml
			<inertial>
				<pose>0 0 0.02 0 0 0</pose>
				<mass>0.2</mass>
				<inertia>
					<ixx>0.0008333333333333335</ixx>
					<ixy>0</ixy>
					<ixz>0</ixz>
					<iyy>0.002166666666666667</iyy>
					<iyz>0</iyz>
					<izz>0.002166666666666667</izz>
				</inertia>
			</inertial>
```

* only support simple parameters (string and number),but block parameters isn't supported.
* it's supported to use other  `xacro_macro`  in `xacro_define_macro` which is recursive definition.

> it's not recommended to define macro recursively (only support <=5).

### 2.3. Math expressions

* within dollared-braces `${xxxx}`, you can also write simple math expressions.
* refer to examples of  **Properties** and **Macros** 
* it's implemented by calling `eval()` in python, so it's unsafe for some cases.

### 2.4. Including other xmacro files

**definition include**

You can include other xmacro files using the `<xacro_include_definition>` tag ,include other xmacro files according to param `uri`.

*  it will only include the definition of properties with tag `<xacro_define_property>` and macros with tag `<xacro_define_macro>`.

```xml
<xacro_include_definition uri="model://simple_car/model.sdf.xmacro"/>
<xacro_include_definition uri="file://simple_car/model.sdf.xmacro"/>
```

* The uri for `model` means to search file in a list of folders which are defined by  environment variable `IGN_GAZEBO_RESOURCE_PATH` and `GAZEBO_MODEL_PATH`
* The uri for `file` means to open the file directly.
  *  it try to open the file with relative path `simple_car/model.sdf.xmacro` . 
  * you can also try to open file with absolute path `/simple_car/model.sdf.xmacro` with uri `file:///simple_car/model.sdf.xmacro`.

>  Tips: 
>
>  *   `<xacro_include_definition>`  supports  to include  recursively.  
>  *  Don't use same name for  xacro definition (the param `name` of  `<xacro_define_property>`  and `<xacro_define_macro>`) , otherwise the priority of xacro definition need be considered.
>  * Be carefully when using  `<xacro_include_definition>`  and `<xacro_include_model>`

### 2.5 pre-defined common.xmacro

```xml
<!--macro defination:inertia-->
<xacro_define_macro name="inertia_cylinder" params="m r l">
<xacro_define_macro name="inertia_box" params="m x y z">
<xacro_define_macro name="inertia_sphere" params="m r">
<!--macro defination:geometry-->
<xacro_define_macro name="geometry_cylinder" params="r l">
<xacro_define_macro name="geometry_box" params="x y z">
<xacro_define_macro name="geometry_sphere" params="r">
<xacro_define_macro name="geometry_mesh" params="uri">
<!--macro defination:visual_collision_with_mesh-->
<xacro_define_macro name="visual_collision_with_mesh" params="prefix uri">
```

* you can directly use the  macro in your xmacro file.

## 3. Custom usage in python

you can use xacro4sdf  in python easily

```python
from xacro4sdf.xacro4sdf import XMLMacro

xmacro=XMLMacro()
#case1 parse from file
xmacro.set_xml_file(inputfile)
xmacro.generate()
xmacro.to_file(outputfile)

#case2 parse from xml string
xmacro.set_xml_string(xml_str)
xmacro.generate()
xmacro.to_file(outputfile)

#case3 generate to string
xmacro.set_xml_file(inputfile)
xmacro.generate()
xmacro.to_string()
```

## 4. Maintainer and License 

maintainer : Zhenpeng Ge, zhenpeng.ge@qq.com

`xacro4sdf` is provided under MIT License.