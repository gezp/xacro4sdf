# xacro4sdf
a simple XML macro tool with python script for sdf, like [ros/xacro](https://github.com/ros/xacro) which is desiged for urdf.

> Reference: [ros/xacro](https://github.com/ros/xacro)
>
> With Xacro, you can construct shorter and more readable XML files by using macros that expand to larger XML expressions. 
>
> * xacro4sdf

**now, it's only a simple script for SDF macro and it's incompatible with xacro API(ros/xacro)**

## 1. Features:

* Properties	
* Macros
* Math expressions
* Include

### 1.1.Properties

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

### 1.2.Macros

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

> it's not recommended to define macro recursively (only support <=5 ).

### 1.3.Math expressions

* within dollared-braces `${xxxx}`, you can also write simple math expressions.
* refer to examples of  **Properties** and **Macros** 
* it's implemented by calling `eval()` in python, so it's unsafe for some cases.

### 1.4.Including other xacro files

**definition include**

You can include other xacro files using the `<xacro_include_definition>` tag .

*  it will only include the definition of properties with tag `<xacro_define_property>` and macros with tag `<xacro_define_macro>`.

```xml
<xacro_include_definition url="model://simple_car/model.sdf.xacro"/>
```

**model include**

You can include other xacro files using the `<xacro_model_definition>` tag.

* it will only include the content  between `<model>...<model/>` in other xacro file.

```xml
<xacro_include_definition url="model://simple_car/model.sdf.xacro"/>
```

>  it's not recommended include xacro file recursively (only support <=5 ).

## 2.Example and Usage

Install

```bash
#install by pip
pip install xacro4sdf #TODO
# or install by source code
# git clone https://github.com/robomaster-oss/xacro4sdf.git
# cd xacro4sdf && sudo python3 setup.py install
```

create model.sdf.xacro file

```xml
<?xml version="1.0"?>
<sdf version="1.7">
    <xacro_define_property name="h" value="0.2" />
    <!--rplidar a2-->
    <model name='rplidar_a2'>
        <link name="link">
            <inertial>
                <pose>0 0 0.02 0 0 0</pose>
                <xacro_macro name="inertia_box" m="0.5" x="${h}" y="${h+0.1}" z="${2*h}"/>
            </inertial>
            <collision name="collision">
                <geometry>
                    <mesh filename="model://rplidar_a2/meshes/rplidar_a2.dae"/>
                </geometry>
            </collision>
            <visual name="visual">
                <geometry>
                    <mesh filename="model://rplidar_a2/meshes/rplidar_a2.dae"/>
                </geometry>
            </visual>
        </link>
    </model>
</sdf>

```

run

```bash
xacro4sdf model.sdf.xacro
```

* it will generate  model.sdf

## 3.Extra Explanation

**the Tag In model.sdf.xacro**

* definition of property and macro： `<xacro_define_property>` and `<xacro_define_macro>`
  * the xacro defination (`<xacro_define_property>` and `<xacro_define_macro>`) must be child node of  root node `<sdf>` .
* use of property and macro：`${xxx}` and `<xacro_macro>` 

* include : `<xacro_include_definition>` and  `<xacro_model_definition>`

**Steps of  prcessing xml** (without include) 

* use dictionary to store the definitions, property dictionary (`<param,value>`) and macro dictionary (`<macro_name,xml_string>`, `<macro_name,params>`) , and remove nodes with these tag.
* process global property `${xxx}` between `<model>...</model>` by using   `eval()`  
* process tag  `<xacro_macro>` , and replace `<xacro_macro>` with macro dictionary `<macro_name,xml_string>`  according to the param `name` of  `<xacro_macro>` , and use `eval()`  to replace `${xxx}` in `<xacro_define_property>`  by using global property  dictionary  and  local property  dictionary.
  * the params of `<xacro_define_property>` make up global property dictionary , the params of  `<xacro_macro>` make up  local property  dictionary.
  * it will recursively process 5 times.