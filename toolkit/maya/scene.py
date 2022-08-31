#!/usr/bin/env python


import re
import os
import importlib


import toolkit.core.naming

from . import hypershade
importlib.reload(hypershade)


import maya.OpenMaya as OpenMaya





def getUnits ():

    result = OpenMaya.MCommandResult()

    command = "currentUnit -query -linear"
    OpenMaya.MGlobal.executeCommand(command, result)

    value = [""]
    result.getResult(value)

    return value[0]







class Manager (object):


    def __init__ (self, getshaders=True):
        
        self.RMAN_DEFAULTS = dict()

        self.tree    = list()
        self.shaders = dict()
        self.root    = str()

        self.defaultMeshScheme = "none"
        self.getshaders = getshaders

        self.get()



    def getCildRoot (self, MDagPath):

        MFnDagNode = OpenMaya.MFnDagNode(MDagPath)
        if MFnDagNode.parentCount() > 0:

            parentMFnDagNode = OpenMaya.MFnDagNode(
                MFnDagNode.parent(0))
            parentPath = parentMFnDagNode.fullPathName()

            if len(parentPath) > 0:

                MSelectionList = OpenMaya.MSelectionList()
                OpenMaya.MGlobal.getSelectionListByName(
                    parentPath,
                    MSelectionList)

                if not MSelectionList.isEmpty():

                    MDagPath = OpenMaya.MDagPath()
                    MSelectionList.getDagPath(0, MDagPath)

                    return self.getCildRoot( MDagPath )

            else:
                return MDagPath



    def getRootList (self):

        rootList = []

        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

        for index in range( MSelectionList.length() ):
            MObject = OpenMaya.MObject()
            MSelectionList.getDependNode(index, MObject)

            if MObject.apiType() in [
                OpenMaya.MFn.kMesh,
                OpenMaya.MFn.kTransform ]:

                MDagPath = OpenMaya.MDagPath()
                MSelectionList.getDagPath(index, MDagPath, MObject)

                OpenMaya.MGlobal.selectByName(
                    MDagPath.fullPathName(),
                    OpenMaya.MGlobal.kReplaceList )

                root = self.getCildRoot(MDagPath)
                if root not in rootList:
                    rootList.append(root)

                break

        return rootList



    def getChildren (self, MDagPath):

        childrenList = []

        MFnDagNode = OpenMaya.MFnDagNode(MDagPath)
        for index in range(MFnDagNode.childCount()):

            childMFnDagNode = OpenMaya.MFnDagNode(
                MFnDagNode.child(index))
            childPath = childMFnDagNode.fullPathName()

            MSelectionList = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getSelectionListByName(
                childPath,
                MSelectionList)

            if not MSelectionList.isEmpty():

                MDagPath = OpenMaya.MDagPath()
                MSelectionList.getDagPath(0, MDagPath)

                childrenList.append(MDagPath)
        
        return childrenList



    def isDagSelected (self, MDagPath):

        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)

        for index in range(MSelectionList.length()):
          
            matchMDagPath = OpenMaya.MDagPath()
            MSelectionList.getDagPath(index, matchMDagPath)

            if matchMDagPath == MDagPath:
                return True

        return False



    def scan (self, tree=None,
            collector=[],
            selected=False):


        if tree is None:
            tree = self.getRootList()


        for treeDag in tree:

            treeObject = treeDag.node()

            treeName = str(treeDag.partialPathName())
            treeType = str(treeObject.apiTypeStr())

            attributes={}
            materials = []

            
            # main filter
            if treeType not in ["kMesh", "kTransform"]:
                continue

            # get attribute to filter history objects
            historyObject =  OpenMaya.MFnDependencyNode(
                treeObject ).findPlug(
                    "intermediateObject").asBool()
                
            if historyObject:
                continue


            # mark selected tree
            selectedFlag = False
            if not selected:
                selectedFlag = self.isDagSelected(treeDag)

            else:
                selectedFlag = True


            if selectedFlag:

                # get visibility attribute
                visibility =  OpenMaya.MFnDependencyNode(
                    treeObject ).findPlug(
                        "visibility").asBool()
                attr = {"visibility": visibility}
                attributes.update(attr)


                
                if treeType == "kMesh":
                    
                    MFnMesh = OpenMaya.MFnMesh(treeDag)


                    # get displacement bound
                    if self.getshaders:
                        shaders = OpenMaya.MObjectArray()
                        MFnMesh.getConnectedShaders(0,
                            shaders, OpenMaya.MIntArray() )

                        hasDisplacement = False
                        if shaders.length() > 0:
                            for i in range(shaders.length()):
                                material = OpenMaya.MFnDependencyNode(shaders[i])
                                if str(material.name()) != "initialShadingGroup":
                                    materials.append(material)

                                shaderPlug = material.findPlug("rman__displacement")
                                if shaderPlug.isConnected():
                                    hasDisplacement = True

                        if hasDisplacement:
                            boundValue =  OpenMaya.MFnDependencyNode(
                                treeObject ).findPlug(
                                    "rman_displacementBound").asFloat()
                            attr = {"rman_displacementBound": boundValue}
                            attributes.update(attr)


                    # check crease sets
                    if self.defaultMeshScheme == "none":
                        try:
                            MUintArray = OpenMaya.MUintArray()
                            MDoubleArray = OpenMaya.MDoubleArray()
                            MFnMesh.getCreaseEdges(MUintArray, MDoubleArray)
                            self.defaultMeshScheme = "catmullClark"
                        except:
                            pass


                    # get subdivision scheme
                    subdivScheme = "none"
                       
                    mayaSubd = OpenMaya.MFnDependencyNode(
                        treeObject ).findPlug(
                            "displaySmoothMesh").asInt()
                    rmanSubd = OpenMaya.MFnDependencyNode(
                        treeObject ).findPlug(
                            "rman_subdivScheme").asInt()

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

            

            # item description
            sItem = {
                "name": treeName,
                "type": re.sub(r"^k", "", treeType),
                "selected": selectedFlag,
                "attributes": attributes,
                "materials": materials,
                "children": []
            }

            collector.append(sItem)


            # next
            self.scan(
                tree=self.getChildren(treeDag),
                collector=sItem["children"],
                selected=selectedFlag )



        return collector



    def clean (self, tree):

        treeClean=list()

        for item in tree:

            selected = item["selected"]
            children = item["children"]
                
            childClean = self.clean(children)

            if not children and selected:
                treeClean.append(item)

            elif childClean and children:
                item["children"] = childClean
                treeClean.append(item)

        return treeClean



    def collectshaders (self, tree, collector={}):

        for item in tree:

            materials = item["materials"]
            for Material in materials:

                materialName = str(Material.name())
                if materialName not in collector:

                    HypershadeManager = hypershade.Manager(self.RMAN_DEFAULTS)

                    render  = HypershadeManager.getPrmanNetwork(Material)
                    preview = HypershadeManager.getPreviewNetwork(Material)

                    self.RMAN_DEFAULTS = HypershadeManager.RMAN_DEFAULTS

                    collector[materialName] = dict(
                        render=render,
                        preview=preview )

            self.collectshaders(
                item["children"],
                collector )

        return collector



    def getroot (self, tree, scope=[]):

        path = str()
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

            path = self.getroot(children, scope=_scope)
            path = str(path)


        return path



    def cut (self, tree):

        treeCut=list()

        for item in tree:

            treeCut = self.cut(item["children"])

            if item["selected"] :
                return [item]

        return treeCut



    def extractMaterialNames (self, tree):

        for item in tree:

            materials = []
            for Material in item["materials"]:
                name = str(Material.name())
                materials.append(name)
                item["materials"] = materials

            children = item["children"]
            item["children"] = self.extractMaterialNames(children)

        return tree



    def treeMaterialNaming (self, tree, rule):

        for item in tree:

            materials = []
            for name in item["materials"]:
                materials.append(rule(name))
            item["materials"] = materials

            children = item["children"]
            item["children"] = self.treeMaterialNaming(
                children, rule)

        return tree



    def applyMaterialNaming (self, rule):

        collector = dict()
        for name, data in self.shaders.items():
            key = rule(name)
            collector[key] = data
        self.shaders = collector

        self.tree = self.treeMaterialNaming(
            self.tree, rule)



    def get (self):

        data = self.scan()
        data = self.clean(data)

        if self.getshaders:
            self.shaders=self.collectshaders(data)
        else:
            self.shaders = {}

        self.root = self.getroot(data)

        data = self.extractMaterialNames(data)
        self.tree = self.cut(data)



    def show (self, root=None, iteration=0):

        if root == None:
            root = self.tree

        for item in root:

            name = item["name"]
            typename = item["type"]
            selected = item["selected"]
            attributes = item["attributes"]
            materials = item["materials"]
            children = item["children"]

            ident = ""
            if iteration:
                ident = "    " * iteration

            print("\n")
            print("{}name: {}".format(ident, name) )
            print("{}type: {}".format(ident, typename) )

            print("{}attributes:".format(ident) )
            if attributes:
                for key, value in attributes.items():
                    print("{}  {}: {}".format(ident, key, value))

            print("{}selected: {}".format(ident, selected) )

            if materials:
                print("{}materials: {}".format(
                    ident, ", ".join(materials) ))


            self.show(root=children, iteration=iteration+1)
