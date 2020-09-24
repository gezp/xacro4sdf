# xacro4sdf
a simple XML macro tool with python script for sdf, like [ros/xacro](https://github.com/ros/xacro) which is desiged for urdf.

> Reference: [ros/xacro](https://github.com/ros/xacro)
>
> With Xacro, you can construct shorter and more readable XML files by using macros that expand to larger XML expressions. 
>
> * xacro4sdf

**now, it's only a simple script for SDF macro and it's also incompatible with xacro API(ros/xacro)**

## Feature

* Properties	
* Macros
* Math expressions

### Properties

Properties are named values that can be inserted anywhere into the XML document

**xacro definfe**

```xml
<!--defination of macro-->
<xacro_property name="radius" value="4.3" />
<!--use of macro-->
<circle diameter="${2 * radius}" />
```

**generated xml**

```xml
<circle diameter="8.6" />
```

### Macros

The main feature of xacro4sdf is its support for macros,Define macros with the macro tag, and specify the macro name and the list of parameters. The list of parameters should be whitespace separated

**xacro definfe**

```xml
<!--defination of macro-->
	<xacro_property name="mass" value="0.2" />
	<xacro_macro_define macro_name="box_inertia" params="m x y z">
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
                <xacro_macro macro_name="box_inertia" m="${mass}" x="0.3" y="0.1" z="0.2"/>
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

### Math expressions

* within dollared-braces `${xxxx}`, you can also write simple math expressions.
* refer to examples of  **Properties** and **Macros** 
* it's implemented by calling eval() in python, so it's unsafe for some cases.

## usage

**model.sdf.xacro file**

* the xacro defination (`<xacro_property>` and `<xacro_macro_define>`) must be child node of  root node `<sdf>` .

**run example**

```bash
python xacro4sdf.py test/model.sdf.xacro
```

* it will generate test/model.sdf



