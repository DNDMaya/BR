from maya import cmds

naming = {"spineJointName" : "spine",
          "jointSuffix" : "J",
          "hipName" : "hip",
          "shoulderName" : "shldr",
          "locatorSuffix" : "loc",
          "controlSuffix" : "ctrl",
          "sdkNodeSuffix" : "SDK",
          "constraintNodeSuffix" : "CON",
          "positionNodeSuffix" : "POS",
          "ikHandle" : "hndl",
          "curve" : "crv",
          "effector" : "efftr",
          "parentConstraint" : "parCon",
          "curveInfo" : "crvInfo",
          "stretch" : "stch",
          "squash" : "sqsh"}

class NamingAgreementHandler:

    assetName = None
    side = None
    base = None
    suffix = None
    nodeName = None

    def __init__(self, assetName = "RIG", side = "center", base = "", suffix = ""):

        self.side = side
        self.base = base
        self.suffix = suffix
        self.assetName = assetName
        self.resolveSide()
        self.resolveAssetName()
        self.resolveSuffix()
        self.createName()

    def resolveSide(self):

        if self.side.lower() == "left":
            self.side = "L_"
        elif self.side.lower() == "right":
            self.side = "R_"
        elif self.side.lower() == "center":
            self.side = ""

    def resolveAssetName(self):

        if self.assetName != "":
            self.assetName += "_"

    def resolveSuffix(self):

        if self.suffix != "":
            self.suffix = "_" + self.suffix

    def createName(self):

        if(self.base):
            self.nodeName = self.assetName + self.side + self.base + self.suffix

class ControllerAgreementHandler:

    controlName = None
    sdkNode = None
    conNode = None
    posNode = None
    driven = None


    ROTATE_ORDER = {"xyz" : 0, "yzx" : 1, "zxy" : 2, "xzy"  : 3, "yxz" : 4, "zyx" : 5}
    ATTRIB = {"tx":"translateX","ty":"translateY","tz":"translateZ","rx":"rotateX","ry":"rotateY","rz":"rotateZ","sx":"scaleX","sy":"scaleY","sz":"scaleZ", "vis":"visibility"}

    CONTROL_LIB = {"cube":
                      {"cvsList": [(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                                   (-0.5, 0.5, 0.5), (-0.5,-0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
                                   (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
                                   (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5)],
                       "degree": 1}}

    def __init__(self, name = "control", shape = "cube", driven = None, scale = 1,
                 sdk = False, con = False):
        self.driven = driven
        self.createControl(shape = shape, name = name)
        self.resolveotherNodes(sdk = sdk, con = con)
        self.setPosition()
        self.setScale(scale)

    def createControl(self, shape, name):

        self.controlName = cmds.curve(name =  NamingAgreementHandler(assetName = "", side = "", base = name,
                                                                    suffix = naming["controlSuffix"]).nodeName,
                                      point = self.CONTROL_LIB[shape]["cvsList"],
                                      degree = self.CONTROL_LIB[shape]["degree"])

    def setPosition(self):

        if self.driven != None:
            cmds.delete(cmds.parentConstraint(self.driven, self.posNode, maintainOffset = False))
            #cmds.makeIdentity(self.posNode, apply=True, translate=True, rotate=True)

    def setScale(self, scale):

        if scale > 0:
            cmds.setAttr("{}.scale".format(self.posNode), scale, scale, scale)
            cmds.makeIdentity(self.posNode, apply=True, scale=True)

    def setRotateOrder(self, rotateOrder):

        if rotateOrder != None:
            cmds.setAttr("{}.rotateOrder".format(self.controlName), self.ROTATE_ORDER[rotateOrder])
            if self.driven != None:
                cmds.setAttr("{}.rotateOrder".format(self.driven), self.ROTATE_ORDER[rotateOrder])

    def setLimitedKeyability(self, *parm):

        for item in parm:
            cmds.setAttr("{}.{}".format(self.controlName, self.ATTRIB[item]), keyable = False, lock = True)

    def resolveotherNodes(self, sdk, con):

        if sdk:
            self.sdkNode = cmds.createNode("transform",
                                           name = NamingAgreementHandler(assetName = "", side = "", base = self.controlName,
                                                                                 suffix = naming["sdkNodeSuffix"]).nodeName)
            cmds.parent(self.controlName, self.sdkNode)
        if con:
            self.conNode = cmds.createNode("transform",
                                           name=NamingAgreementHandler(assetName="", side="", base=self.controlName,
                                                                       suffix=naming["constraintNodeSuffix"]).nodeName)
            if sdk:
                cmds.parent(self.sdkNode, self.conNode)
            else:
                cmds.parent(self.controlName, self.conNode)


        self.posNode = cmds.createNode("transform",
                                        name=NamingAgreementHandler(assetName="", side="", base=self.controlName,
                                                                       suffix=naming["positionNodeSuffix"]).nodeName)
        if con:
            cmds.parent(self.conNode, self.posNode)
        elif sdk:
            cmds.parent(self.sdkNode, self.posNode)
        else:
            cmds.parent(self.controlName, self.posNode)


class TorsoRig:

    LOCATORS = {"neckRoot":[0, 152, 0], "hip":[0, 102, 0]}
    LOCK_SCALE = 20
    ROTATE_ORDER = "zxy"
    CONTROL_SCALE = 30
    J_RADIUS = 3

    joints = []
    bindJoints = []
    neckRootPosition = []
    ikControls = []
    ikSystemObjs = []
    arclenNode = ""
    baseStretch = ""
    baseSquash = ""

    # def __init__(self):


    def clearSelection(self):

        cmds.select(clear=True)

    def createLocators(self):

        locators = {}
        for item in self.LOCATORS:
            locators[cmds.spaceLocator(name = NamingAgreementHandler(base = item, suffix=naming["locatorSuffix"]).nodeName)[0]] = self.LOCATORS[item]
        self.LOCATORS = locators
        for item in self.LOCATORS:
            cmds.setAttr("{}.scale".format(item), self.LOCK_SCALE, self.LOCK_SCALE, self.LOCK_SCALE)
            cmds.setAttr("{}.overrideEnabled".format(item), 1)
            cmds.setAttr("{}.overrideColor".format(item), 17)
            cmds.setAttr("{}.translate".format(item), self.LOCATORS[item][0], self.LOCATORS[item][1], self.LOCATORS[item][2])
            self.clearSelection()

    def updateLocators(self):

        for item in self.LOCATORS:
            self.LOCATORS[item] = cmds.xform(item, query = True, translation = True, worldSpace = True)

    def delLocators(self):

        for item in self.LOCATORS:
            cmds.delete(item)

    def createPositionJoints(self, num = 2):

        self.delLocators()
        self.clearSelection()
        delta = [(self.LOCATORS[self.LOCATORS.keys()[0]][z] - self.LOCATORS[self.LOCATORS.keys()[1]][z]) / (num - 1 ) for z in range(0,3)]
        for n in range(0, num):
            self.joints.append(cmds.joint(position = (delta[x] * n  + self.LOCATORS[self.LOCATORS.keys()[1]][x] for x in range(0,3) ),
                                          radius = self.J_RADIUS,
                                          name = NamingAgreementHandler(base = "joint_" + str(n + 1),
                                                                         suffix = naming["jointSuffix"]).nodeName))
            cmds.setAttr("{}.overrideEnabled".format(self.joints[n]), 1)
            cmds.setAttr("{}.overrideColor".format(self.joints[n]), 17)
            self.clearSelection()

    def resetPositionJoints(self):

        for n in self.joints:
            cmds.setAttr("{}.overrideEnabled".format(n), 0)
            cmds.setAttr("{}.radius".format(n) , self.J_RADIUS)

    def connectPositionJoints(self):

        for n in range(0,len(self.joints) - 1):
            cmds.parent(self.joints[n + 1], self.joints[n], absolute = True)

    def createSpineJoints(self):

        self.resetPositionJoints()
        self.connectPositionJoints()

        for n in range(0, len(self.joints) - 1):
            self.joints[n] = cmds.rename(self.joints[n], NamingAgreementHandler(base = naming["spineJointName"] + "_" + str(n + 1),
                                                                                 suffix=naming["jointSuffix"]).nodeName)

        cmds.makeIdentity(self.joints[0], rotate = True)
        cmds.joint(self.joints[0], edit=True, orientJoint = "xzy", secondaryAxisOrient = "xup",
                   children = True, zeroScaleOrient = True);

        self.neckRootPosition = cmds.xform(self.joints[-1], query=True, translation=True, worldSpace=True)
        cmds.delete(self.joints.pop())

    def createbindJoints(self):

        self.bindJoints.append(cmds.duplicate(self.joints[0], parentOnly=True,
                                                   name=NamingAgreementHandler(base=naming["hipName"],
                                                                               suffix=naming["jointSuffix"]).nodeName)[0])
        self.bindJoints.append(cmds.duplicate(self.joints[-1], parentOnly=True,
                                                   name=NamingAgreementHandler(base=naming["shoulderName"],
                                                                               suffix=naming["jointSuffix"]).nodeName)[0])
        cmds.parent(self.bindJoints[1], world=True)

        for x in self.bindJoints:
            cmds.joint(x, edit = True,  orientJoint = "none", zeroScaleOrient = True)


    def createIkControls(self):

        for n in self.bindJoints:
            num = -len(naming["jointSuffix"]) - 1
            self.ikControls.append(ControllerAgreementHandler(name = n[:num], driven = n,
                                                              scale = self.CONTROL_SCALE, sdk = True, con = True))
        for x in self.ikControls:
            x.setRotateOrder(self.ROTATE_ORDER)
            x.setLimitedKeyability("vis","sx","sy","sz")
            conName = cmds.parentConstraint(x.controlName, x.driven)[0]
            cmds.rename(conName, NamingAgreementHandler(assetName="", side="", base = x.driven,
                                                                       suffix = naming["parentConstraint"]).nodeName)


    def createIkSplineSystem(self):

        self.clearSelection()
        cmds.select(self.joints[0], self.joints[-1], add = True)
        self.ikSystemObjs = cmds.ikHandle(solver = "ikSplineSolver")
        newObjs = []
        for x in range(len(self.ikSystemObjs)):
            if x == 0:
                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=naming["spineJointName"],
                                                                   suffix=naming["ikHandle"]).nodeName))
            elif x == 2:

                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=naming["spineJointName"],
                                                      suffix=naming["curve"]).nodeName))

                self.clearSelection()

                cmds.skinCluster(self.bindJoints, newObjs[-1], bindMethod = 0, normalizeWeights = 1, weightDistribution = 0,
                                 maximumInfluences =  2, obeyMaxInfluences = True, dropoffRate = 4,
                                 removeUnusedInfluence = True )

            if x == 1:
                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=naming["spineJointName"],
                                                      suffix=naming["effector"]).nodeName))
        self.ikSystemObjs = newObjs

    def setupStretch(self):

        self.arclenNode = cmds.arclen(self.ikSystemObjs[2], constructionHistory = True)
        self.arclenNode = cmds.rename(self.arclenNode, NamingAgreementHandler(base=naming["spineJointName"],
                                                      suffix=naming["curveInfo"]).nodeName)

        curveLength = cmds.getAttr("{}.arcLength".format(self.arclenNode))

        self.baseStretch = cmds.createNode("multiplyDivide", name = NamingAgreementHandler(base=naming["spineJointName"],
                                                      suffix=naming["stretch"]).nodeName)
        cmds.setAttr("{}.operation".format(self.baseStretch), 2)
        cmds.setAttr("{}.input2X".format(self.baseStretch), curveLength)
        cmds.connectAttr("{}.arcLength".format(self.arclenNode), "{}.input1X".format(self.baseStretch))

        for x in range(len(self.joints) - 1):
            cmds.connectAttr("{}.outputX".format(self.baseStretch),"{}.scaleX".format(self.joints[x]))

    def setupSquash(self):
        self.baseSquash = cmds.createNode("multiplyDivide", name = NamingAgreementHandler(base=naming["spineJointName"],
                                                      suffix=naming["squash"]).nodeName)
        cmds.setAttr("{}.operation".format(self.baseSquash), 3)
        cmds.connectAttr("{}.outputX".format(self.baseStretch),"{}.input1X".format(self.baseSquash))
        cmds.setAttr("{}.input2X".format(self.baseSquash),-0.5)

        self.createSqshStchCont()

    def setupTwist(self):

        ikHndl = self.ikSystemObjs[0]
        cmds.setAttr("{}.dTwistControlEnable".format(ikHndl), 1)
        cmds.setAttr("{}.dWorldUpType".format(ikHndl), 4)
        cmds.setAttr("{}.dForwardAxis".format(ikHndl), 0)
        cmds.setAttr("{}.dWorldUpAxis".format(ikHndl), 4)
        cmds.setAttr("{}.dWorldUpVector".format(ikHndl), 0, 0, -1)
        cmds.setAttr("{}.dWorldUpVectorEnd".format(ikHndl), 0, 0, -1)
        cmds.connectAttr("{}.worldMatrix".format(self.bindJoints[0]), "{}.dWorldUpMatrix".format(ikHndl))
        cmds.connectAttr("{}.worldMatrix".format(self.bindJoints[1]), "{}.dWorldUpMatrixEnd".format(ikHndl))

    def createSqshStchCont(self):
        attName = "splineStretch"
        #cmds.select(self.ikControls[1].controlName)
        cmds.addAttr(self.ikControls[1].controlName, longName = attName , attributeType = "float", keyable = True)
        self.clearSelection()
        joints_num = len(self.joints) - 1
        cmds.setKeyframe(self.ikControls[1].controlName, time = [1,joints_num], value = 1, attribute = attName)
        curveControl = cmds.keyframe(self.ikControls[1].controlName, attribute = attName, name = True, query = True)[0]

        for x in range(joints_num):
            jointFrCache = cmds.createNode("frameCache", name=NamingAgreementHandler(assetName="", side="", base=self.joints[x],
                                                                          suffix="frameCache").nodeName)
            cmds.setAttr("{}.varyTime".format(jointFrCache), x + 1)
            cmds.connectAttr("{}.output".format(curveControl), "{}.stream".format(jointFrCache))

            jointPow = cmds.createNode("multiplyDivide", name=NamingAgreementHandler(assetName="", side="", base=self.joints[x],
                                                                          suffix="pow").nodeName)

            cmds.setAttr("{}.operation".format(jointPow), 3)
            cmds.connectAttr("{}.varying".format(jointFrCache), "{}.input2X".format(jointPow))
            cmds.connectAttr("{}.outputX".format(self.baseSquash), "{}.input1X".format(jointPow))

            cmds.connectAttr("{}.outputX".format(jointPow), "{}.scaleY".format(self.joints[x]))
            cmds.connectAttr("{}.outputX".format(jointPow), "{}.scaleZ".format(self.joints[x]))


    def getNeckRootPosition(self):
        return self.neckRootPosition






