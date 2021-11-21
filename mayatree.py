

import os
import pymel.core as PyMELcore


from pymel.core import select as PyMelSelect
from pymel.core import selected as PyMelSelected
from pymel.core import getAttr as PyMelGetAttr


import mayashader
reload(mayashader)


encModel = os.getenv("PYTHONIOENCODING")





def keydata (dictionary, keyname):
    if isinstance(dictionary, dict):

        for key, value in dictionary.items():
            
            if key == keyname:
                return value





def getCildRoot(child):

    parentNode = child.getParent()

    if parentNode:
        return getCildRoot(parentNode)
    else:
        return child


def getRootList ():
    
    rootList = []

    nodeList = PyMelSelected()
    if nodeList:
        nodeList = [nodeList[0]]
    PyMelSelect(nodeList)

    for child in PyMelSelected():
        root = getCildRoot(child)
        
        if root not in rootList:
            rootList.append(root)
    
    return rootList









def scan (tree=getRootList(), collector=[], selected=False):


    for treeItem in tree:

        flag = False
        if not selected:

            for item in PyMelSelected():
                if item == treeItem:
                    flag = True
        else:
            flag = True


        attributes={}
        material = None


        visibility = PyMelGetAttr( "{}.visibility".format(treeItem.name()) )
        attr = {"visibility": visibility}
        attributes.update(attr)


        if treeItem.type().encode(encModel)=="mesh":


            vertex = treeItem.verts[0]
            color = vertex.getColor()
            color = list(color)

            hasColor = True
            for index in range(len(color)):
                value = color[index]
                if value < 0.0: hasColor = False
                color[index] = round(value, 4)

            if hasColor:
                if len(color) > 3: color = color[:3]
                attr = {"displayColor": color}
                attributes.update(attr)


            shGroups = treeItem.shadingGroups()
            for shGroup in shGroups:

                material = shGroup.getName().encode(encModel)

                prmanDisplacement = shGroup.attr("rman__displacement")
                if prmanDisplacement.inputs():
                    
                    boundValue = PyMelGetAttr( "{}.rman_displacementBound".format(treeItem.name()) )
                    attr = {"rman_displacementBound": boundValue}
                    attributes.update(attr)


            subdivScheme = "none"
                    
            mayaSubd = PyMelGetAttr( "{}.displaySmoothMesh".format(treeItem.name()) )
            rmanSubd = PyMelGetAttr( "{}.rman_subdivScheme".format(treeItem.name()) )

            if rmanSubd==1:
                subdivScheme = "catmullClark"
            elif rmanSubd==2:
                subdivScheme = "loop"
            elif rmanSubd==3:
                subdivScheme = "bilinear"
            elif mayaSubd>=1:
                subdivScheme = "catmullClark"

            attr = {"subdivScheme": subdivScheme}
            attributes.update(attr)



        sItem = {
            "name": treeItem.name().encode(encModel),
            "type": treeItem.type().encode(encModel),
            "selected": flag,
            "attributes": attributes,
            "material": material,
            "children": []
        }

        collector.append(sItem)

        scan(
            tree=treeItem.getChildren(),
            collector=sItem["children"],
            selected=flag)


    return collector









def clean (tree):

    treeClean=list()

    for item in tree:

        selected = item["selected"]
        children = item["children"]
            
        childClean = clean(children)

        if not children and selected:
            treeClean.append(item)

        elif childClean and children:
            item["children"] = childClean
            treeClean.append(item)

    return treeClean





def cut (tree):

    treeCut=list()

    for item in tree:

        treeCut = cut(item["children"])

        if item["selected"] :
            return [item]

    return treeCut







def mergeshapes (tree):

    for item in tree:

        name = item["name"]
        selected = item["selected"]
        children = item["children"]

        buffer = []
        for child in children:

            if child["type"] == "mesh":

                item["type"]       = child["type"]
                item["material"]   = child["material"]

                visibility = keydata(
                    item["attributes"],
                    "visibility")

                if isinstance(visibility, type(True)):
                    if not visibility:
                        child["attributes"]["visibility"] = False

                item["attributes"] = child["attributes"]

            else:
                buffer.append(child)
        
        item["children"] = mergeshapes(buffer)

    return tree









def collectshaders (tree, collector={}):

    for item in tree:

        material = item["material"]
        if material:

            engine = mayashader.getShadingEngine(material)

            render  = mayashader.getPrmanNetwork(engine)
            preview = mayashader.getPreviewNetwork(engine)

            collector[material] = dict(
                render=render,
                preview=preview )
        
        collectshaders(
            item["children"],
            collector)

    return collector







def getroot (tree, scope=[], path=None):

    for item in tree:

        _scope = [i for i in scope]

        name = item["name"]
        children = item["children"]
        selected = item["selected"]

        if not selected:
            _scope.append( name )

        else:
            root = os.path.join("/", *_scope)
            return os.path.join(root, name)

        path = getroot(children, scope=_scope)


    return path







def get (merge=False):

    data = scan()
    data = clean(data)

    if merge:
        data = mergeshapes(data)

    shaders = collectshaders(data)
    root = getroot(data)

    data = cut(data)

    return dict(
        data=data,
        root=root,
        shaders=shaders)








def show (treeItem, iteration=0):

    for item in treeItem:

        name = item["name"]
        typename = item["type"]
        selected = item["selected"]
        attributes = item["attributes"]
        material = item["material"]
        children = item["children"]

        ident = ""
        if iteration:
            ident = "    " * iteration

        print("{}name: {}".format(ident, name) )
        print("{}type: {}".format(ident, typename) )
        print("{}selected: {}".format(ident, selected) )

        print("{}attributes:".format(ident) )
        if attributes:
            for key, value in attributes.items():
                print("{}  {} >> {}".format(ident, key, value))

        print("{}material: {}".format(ident, material) )
        print("\n")


        show(children, iteration=iteration+1)

