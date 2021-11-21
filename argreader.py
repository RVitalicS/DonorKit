

import os
import xml.etree.ElementTree as ET







def keydata (dictionary, keyname):

    for key, value in dictionary.items():
        
        if key == keyname:
            return value



def typeEditor (paramdefault, paramtype):

    if paramtype in ["color", "normal"]:
        return tuple([float(i) for i in paramdefault.split(" ")])

    elif paramtype == "float":
        paramdefault = paramdefault.replace("f", "")
        return float(paramdefault)

    elif paramtype == "int":
        return int(paramdefault)

    elif paramtype == "string":
        return str(paramdefault)



def treeRunner (function, root, value=None, page=""):

    for child in root:
        if child.tag == "param":


            paramname = keydata(child.attrib, "name")
            if paramname:

                paramtype = keydata(child.attrib, "type")
                if paramtype:

                    paramdefault = keydata(child.attrib, "default")
                    if paramdefault:

                        dynamicArray = keydata(child.attrib, "isDynamicArray")
                        if not dynamicArray:
                            paramdefault = typeEditor(paramdefault, paramtype)
                            value = function(paramname, paramtype, paramdefault)
                            if not isinstance(value, type(None)):
                                return value


        value = treeRunner(function, child, value=value, page=page)
        if not isinstance(value, type(None)):
            return value







# LamaDiffuse = "/opt/pixar/RenderManProServer-24.1/lib/plugins/Args/LamaDiffuse.args"

# if os.path.exists(LamaDiffuse):
#     tree = ET.ElementTree(file=LamaDiffuse)
#     root = tree.getroot()

#     def match (paramname, paramtype, paramdefault):
        
#         if paramname == "lobeName":
#             return paramdefault

#     print( treeRunner(match, root) )