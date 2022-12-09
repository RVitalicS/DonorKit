#!/usr/bin/env python

"""
Scene

Implement a Maya scene manager with utility functions.
"""

import re
import os
from typing import Union
from typing import Callable
import maya.OpenMaya as OpenMaya
from toolkit.maya import hypershade


def getUnits () -> str:
    """Get the units name in which Maya currently work

    Returns:
        The units name
    """
    result = OpenMaya.MCommandResult()
    command = "currentUnit -query -linear"
    OpenMaya.MGlobal.executeCommand(command, result)
    value = [""]
    result.getResult(value)
    return value[0]


class Manager (object):
    """A class to get a dictionary data that describes a Maya scene

    Keyword Arguments:
        getshaders: A flag used to get material networks
    """
    def __init__ (self, getshaders: bool = True) -> None:
        self.RMAN_DEFAULTS = dict()
        self.ASSETS = dict()
        self.defaultMeshScheme = "none"
        self.getshaders = getshaders
        data = self.getSceneData()
        data = self.cutUnusedChildren(data)
        if self.getshaders:
            self.shaders=self.collectShaders(data)
        else:
            self.shaders = dict()
        self.root = self.getRootPath(data)
        data = self.extractMaterialNames(data)
        self.tree = self.cutUnusedParents(data)

    def getChildRoot (self, MDagPath: OpenMaya.MDagPath) -> OpenMaya.MDagPath:
        """Get a path of a root node that is a parent of the specified node path

        Arguments:
            MDagPath: The path to a DAG node
        Returns:
            A path to a root DAG node
        """
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
                    return self.getChildRoot(MDagPath)
            else:
                return MDagPath

    def getRootList (self) -> list:
        """Get a list of DAG paths that are roots of a scene
        from currently selected objects

        Returns:
            A list of root paths to a DAG nodes
        """
        rootList = []
        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)
        for index in range(MSelectionList.length()):
            MObject = OpenMaya.MObject()
            MSelectionList.getDependNode(index, MObject)
            if MObject.apiType() in [
                    OpenMaya.MFn.kMesh,
                    OpenMaya.MFn.kTransform ]:
                MDagPath = OpenMaya.MDagPath()
                MSelectionList.getDagPath(index, MDagPath, MObject)
                OpenMaya.MGlobal.selectByName(
                    MDagPath.fullPathName(),
                    OpenMaya.MGlobal.kReplaceList)
                root = self.getChildRoot(MDagPath)
                if root not in rootList:
                    rootList.append(root)
                break
        return rootList

    def getChildren (self, MDagPath: OpenMaya.MDagPath) -> list:
        """Get paths of DAG nodes that are children
        of the specified node path

        Arguments:
            MDagPath: The path to a DAG node
        Returns:
            A list of child paths to a DAG nodes
        """
        childrenList = []
        MFnDagNode = OpenMaya.MFnDagNode(MDagPath)
        for index in range(MFnDagNode.childCount()):
            childMFnDagNode = OpenMaya.MFnDagNode(
                MFnDagNode.child(index))
            childPath = childMFnDagNode.fullPathName()
            MSelectionList = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getSelectionListByName(
                childPath, MSelectionList)
            if not MSelectionList.isEmpty():
                MDagPath = OpenMaya.MDagPath()
                MSelectionList.getDagPath(0, MDagPath)
                childrenList.append(MDagPath)
        return childrenList

    def isDagSelected (self, MDagPath: OpenMaya.MDagPath) -> bool:
        """Check if a DAG node with the specified path is selected

        Arguments:
            MDagPath: The path to a DAG node
        Returns:
            A result of the check
        """
        MSelectionList = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(MSelectionList)
        for index in range(MSelectionList.length()):
            matchMDagPath = OpenMaya.MDagPath()
            MSelectionList.getDagPath(index, matchMDagPath)
            if matchMDagPath == MDagPath:
                return True
        return False

    def getSceneData (self, tree: Union[None, list] = None,
                      collector: Union[None, list] = None,
                      selected: bool = False) -> list:
        """Create a data that describes an attributes,
        material assignments and hierarchy of a Maya scene

        Keyword Arguments:
            tree: The list of root paths to a DAG nodes
            collector: The exchange data object for the iterations
            selected: A flag used to get a data from selected objects only
        Returns:
            A Maya scene description data
        """
        if tree is None:
            tree = self.getRootList()
        if collector is None:
            collector = list()
        for treeDag in tree:
            treeObject = treeDag.node()
            treeName = str(treeDag.partialPathName())
            treeType = str(treeObject.apiTypeStr())
            attributes={}
            materials = []

            # filter
            if treeType not in ["kMesh", "kTransform"]:
                continue
            historyObject =  OpenMaya.MFnDependencyNode(
                treeObject).findPlug("intermediateObject").asBool()
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
                visibility = OpenMaya.MFnDependencyNode(
                    treeObject).findPlug("visibility").asBool()
                attr = {"visibility": visibility}
                attributes.update(attr)

                # get displacement bound
                if treeType == "kMesh":
                    MFnMesh = OpenMaya.MFnMesh(treeDag)
                    if self.getshaders:
                        shaders = OpenMaya.MObjectArray()
                        MFnMesh.getConnectedShaders(
                            0, shaders, OpenMaya.MIntArray())
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
                                treeObject).findPlug(
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
                        treeObject).findPlug("displaySmoothMesh").asInt()
                    rmanSubd = OpenMaya.MFnDependencyNode(
                        treeObject).findPlug("rman_subdivScheme").asInt()
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
                "children": []}
            collector.append(sItem)

            # next
            self.getSceneData(
                tree=self.getChildren(treeDag),
                collector=sItem["children"],
                selected=selectedFlag)

        return collector

    def cutUnusedChildren (self, data: list) -> list:
        """Get rid of children that are not selected in a hierarchy tree

        Arguments:
            data: The Maya scene description data
        Returns:
            A cleaned Maya scene description data
        """
        treeClean=list()
        for item in data:
            selected = item["selected"]
            children = item["children"]
            childClean = self.cutUnusedChildren(children)
            if not children and selected:
                treeClean.append(item)
            elif childClean and children:
                item["children"] = childClean
                treeClean.append(item)
        return treeClean

    def collectShaders (self, data: list, collector: Union[None, dict] = None) -> dict:
        """Get a build scheme data for creating a USD Material
        for all materials used in a Maya scene

        Arguments:
            data: The Maya scene description data
        Keyword Arguments:
            collector: The exchange data object for the iterations
        Returns:
            A list of a build schemes for a USD Material files
        """
        if collector is None:
            collector = dict()
        for item in data:
            materials = item["materials"]
            for Material in materials:
                materialName = str(Material.name())
                if materialName not in collector:
                    HypershadeManager = hypershade.Manager(
                        data=self.RMAN_DEFAULTS, assets=self.ASSETS)
                    scheme = HypershadeManager.getUsdBuildScheme(Material)
                    self.RMAN_DEFAULTS = HypershadeManager.RMAN_DEFAULTS
                    self.ASSETS = HypershadeManager.ASSETS
                    collector[materialName] = scheme
            self.collectShaders(item["children"], collector)
        return collector

    def getRootPath (self, data: list, scope: Union[None, list] = None) -> str:
        """Get the current selection point of a hierarchy tree

        Arguments:
            data: The Maya scene description data
        Keyword Arguments:
            scope: The exchange data object for the iterations
        Returns:
            A hierarchy tree path
        """
        if scope is None:
            scope = list()
        path = str()
        for item in data:
            name = item["name"]
            children = item["children"]
            selected = item["selected"]
            if not selected:
                scope.append(name)
            else:
                return os.path.join("/", *scope, name)
            path = self.getRootPath(children, scope=scope)
        return path

    def cutUnusedParents (self, data: list) -> list:
        """Get rid of roots that are not selected in a hierarchy tree

        Arguments:
            data: The Maya scene description data
        Returns:
            A cleaned Maya scene description data
        """
        treeCut=list()
        for item in data:
            treeCut = self.cutUnusedParents(item["children"])
            if item["selected"]:
                return [item]
        return treeCut

    def extractMaterialNames (self, data: list) -> list:
        """Replace MFnDependencyNode objects
        in the description data with material names

        Arguments:
            data: The Maya scene description data
        Returns:
            An edited Maya scene description data
        """
        for item in data:
            materials = []
            for Material in item["materials"]:
                name = str(Material.name())
                materials.append(name)
                item["materials"] = materials
            children = item["children"]
            item["children"] = self.extractMaterialNames(children)
        return data

    def treeMaterialNaming (self, data: list, rule: Callable) -> list:
        """Rename materials in the scene description data using the specified function

        Arguments:
            data: The Maya scene description data
            rule: The function to change names
        Returns:
            An edited Maya scene description data
        """
        for item in data:
            materials = []
            for name in item["materials"]:
                materials.append(rule(name))
            item["materials"] = materials
            children = item["children"]
            item["children"] = self.treeMaterialNaming(
                children, rule)
        return data

    def applyMaterialNaming (self, rule: Callable) -> None:
        """Rename materials using the specified function in a scene description data
        and in a list of a build schemes for a USD Material files

        Arguments:
            rule: The function to change names
        """
        collector = dict()
        for name, data in self.shaders.items():
            key = rule(name)
            collector[key] = data
        self.shaders = collector
        self.tree = self.treeMaterialNaming(
            self.tree, rule)

    def show (self, data: Union[None, list] = None, iteration: int = 0) -> None:
        """Print the scene description data using an indentation to show a hierarchy

        Keyword Arguments:
            data: The Maya scene description data
            iteration: The iteration number
        """
        if data is None:
            data = self.tree
        for item in data:
            name = item["name"]
            typename = item["type"]
            selected = item["selected"]
            attributes = item["attributes"]
            materials = item["materials"]
            children = item["children"]
            ident = ""
            space = 4
            if iteration:
                ident = " " * space * iteration
            print("\n")
            print(f"{ident}name: {name}")
            print(f"{ident}type: {typename}")
            print(f"{ident}attributes:")
            if attributes:
                for key, value in attributes.items():
                    print(f"{ident}  {key}: {value}")
            print(f"{ident}selected: {selected}")
            if materials:
                print(f"{ident}materials: "+ ", ".join(materials))
            self.show(data=children, iteration=iteration+1)
