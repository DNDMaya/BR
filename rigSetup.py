    # coding=utf-8
from maya import cmds

    # Глобальный словарь наименования различных элементов сетапа
NAMING = {"spineJointName" : "spine",
          "bodyCtrlName" : "torso",
          "ctrlGroupName" : "ctrl",
          "groupSuffix" : "grp",
          "jointSuffix" : "J",
          "hipName" : "hip",
          "shoulderName" : "shldr",
          "locatorSuffix" : "loc",
          "controlSuffix" : "ctrl",
          "sdkNodeSuffix" : "SDK",
          "constraintNodeSuffix" : "CON",
          "positionNodeSuffix" : "POS",
          "ikHandleSuffix" : "hndl",
          "curveSuffix" : "crv",
          "effectorSuffix" : "efftr",
          "parentConstraintSuffix" : "parCon",
          "curveInfoSuffix" : "crvInfo",
          "stretchSuffix" : "stch",
          "squashSuffix" : "sqsh",
          "DNTName" : "DoNotTouch",
          "allGrpName" : "rootTransform",
          "layer" : "LYR"}

    # Словарь сокращений принятых для блокировки аттрибутов
ATTRIB = {"rad":"radius", "tx":"translateX","ty":"translateY","tz":"translateZ","rx":"rotateX","ry":"rotateY","rz":"rotateZ","sx":"scaleX","sy":"scaleY","sz":"scaleZ", "vis":"visibility"}

    # Функция для блокировки аттрибутов
def setLimitedKeyability(name, parm):
    for item in parm:
        cmds.setAttr("{}.{}".format(name, ATTRIB[item]), keyable=False, lock=True, channelBox = False)

    # Класс генерации имени
class NamingAgreementHandler:

    assetName = None
    side = None
    base = None
    suffix = None
    nodeName = None

    def __init__(self, assetName = "AFrig", side = "center", base = "", suffix = ""):

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

    # Класс генерации контроллера
class ControllerAgreementHandler:

    controlName = None
    sdkNode = None
    conNode = None
    posNode = None
    driven = None
    lastNode = None

    ROTATE_ORDER = {"xyz" : 0, "yzx" : 1, "zxy" : 2, "xzy"  : 3, "yxz" : 4, "zyx" : 5}

    CONTROL_LIB = {"cube":
                      {"cvsList": [(-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                                   (-0.5, 0.5, 0.5), (-0.5,-0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
                                   (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
                                   (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5)],
                       "degree": 1},
                   "square":
                       {"cvsList": [(-1, 0, 1), (1 , 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)],
                        "degree": 1},
                   "circleX" : {"normal" : (1, 0, 0)},
                   "circleY": {"normal": (0, 1, 0)},
                   "circleZ": {"normal": (0, 0, 1)}
                   }

    def __init__(self, name = "control", shape = "cube", driven = None, scale = 1, pos = True,
                 sdk = False, con = False, suffix = NAMING["controlSuffix"], toOrign = False):
        self.driven = driven
        self.createControl(shape = shape, name = name, suffix = suffix)
        self.resolveotherNodes(sdk = sdk, con = con, pos = pos)
        self.setPosition()
        self.setScale(scale,toOrign)

    def createControl(self, shape, name,suffix):

        name = NamingAgreementHandler(assetName = "", side = "", base = name,
                                                                    suffix = suffix).nodeName
        if(not "circle" in shape):
            self.controlName = cmds.curve(name =  name,
                                      point = self.CONTROL_LIB[shape]["cvsList"],
                                      degree = self.CONTROL_LIB[shape]["degree"])
        else:
            self.controlName = cmds.circle(normal = self.CONTROL_LIB[shape]["normal"], name = name)[0]

        self.lastNode = self.controlName

    def setPosition(self):

        if self.driven != None:
            cmds.delete(cmds.parentConstraint(self.driven, self.lastNode, maintainOffset = False))

    def setScale(self, scale, toOrign):

        if scale > 0:
            cmds.setAttr("{}.scale".format(self.lastNode), scale, scale, scale)
            if toOrign == True:
                cmds.setAttr("{}.translate".format(self.lastNode), 0,0,0,)
            cmds.makeIdentity(self.lastNode, apply=True, translate=True, scale=True, rotate=True)

    def setRotateOrder(self, rotateOrder):

        if rotateOrder != None:
            cmds.setAttr("{}.rotateOrder".format(self.controlName), self.ROTATE_ORDER[rotateOrder])
            if self.driven != None:
                cmds.setAttr("{}.rotateOrder".format(self.driven), self.ROTATE_ORDER[rotateOrder])

    def setLimitedKeyability(self, parm):

        setLimitedKeyability(self.controlName, parm)

    def resolveotherNodes(self, sdk, con, pos):

        if sdk:
            self.sdkNode = cmds.createNode("transform",
                                           name = NamingAgreementHandler(assetName = "", side = "", base = self.controlName,
                                                                                 suffix = NAMING["sdkNodeSuffix"]).nodeName)
            cmds.parent(self.controlName, self.sdkNode)
            self.lastNode = self.sdkNode
        if con:
            self.conNode = cmds.createNode("transform",
                                           name=NamingAgreementHandler(assetName="", side="", base=self.controlName,
                                                                       suffix=NAMING["constraintNodeSuffix"]).nodeName)
            if sdk:
                cmds.parent(self.sdkNode, self.conNode)
            else:
                cmds.parent(self.controlName, self.conNode)

            self.lastNode = self.conNode

        if pos:
            self.posNode = cmds.createNode("transform",
                                        name=NamingAgreementHandler(assetName="", side="", base=self.controlName,
                                                                       suffix=NAMING["positionNodeSuffix"]).nodeName)
            if con:
                cmds.parent(self.conNode, self.posNode)
            elif sdk:
                cmds.parent(self.sdkNode, self.posNode)
            else:
                cmds.parent(self.controlName, self.posNode)

            self.lastNode = self.posNode


    def deleteAll(self):
        if(self.controlName != None):
            cmds.delete(self.controlName)
        if(self.sdkNode != None):
            cmds.delete(self.sdkNode)
        if(self.conNode != None):
            cmds.delete(self.conNode)
        if(self.posNode != None):
            cmds.delete(self.posNode)

    # Класс для создания экземпляра сетапа спины
class TorsoRig:

    # Внутренние переменные определяющие систему
    LOCATORS = {}
    LOCK_SCALE = 20
    ROTATE_ORDER = ""
    ROTATE_FK_ORDER = ""
    CONTROL_SCALE = 30
    J_RADIUS = 3
    twistUp =()

    # Основные составляющие сетапа спины
    # Основные джоинты спины
    joints = []
    # Джоинты для FK системы
    fkJoints = []
    # Джоинты для управления IK системой через кривую
    bindJoints = []
    # Контроллеры IK системы
    ikControls = []
    # Список из ikHandle, effector, curve системы IK spline
    ikSystemObjs = []
    # Нода рассчета длины кривой
    arclenNode = ""
    # Нода расчета маштабирования системы джоинтов вдоль основоного направления
    baseStretch = ""
    # Нода расчета маштабирования системы джоинтов вдоль второстепенных осей
    baseSquash = ""

    # Выходные данные для других частей сетапа
    # Позиция основания шеи
    neckRootPosition = []
    # Контроллер спины целиком
    bodyCtrl = ""
    # Группа для объектов, которые не нужно трогать
    DNTGrp = ""
    # Группа для bodyCtrl, DNTGrp
    torsoGrp = ""
    # Группа позиционирования всей системы рига
    rootGrp = ""

    # Визуальные слои для сетапа спины
    # FK слой
    fkLayer = ""
    # IK слой
    ikLayer = ""
    # Слой для контроллера спины
    torsoBaseLayer = ""

    # Инициализация определяющих переменных в зависимости от типа рига
    def __init__(self, type = "biped"):
        self.ROTATE_ORDER = "zxy"

        if type == "biped":
            self.LOCATORS = {"neckRoot": [0, 150, 0], "hip": [0, 90, 0]}
            self.twistUp =(0,0,-1)
            self.ROTATE_FK_ORDER = "yzx"
        elif type == "quadruped":
            self.LOCATORS = {"neckRoot": [0, 30, 30], "hip": [0, 30, -30]}
            self.twistUp = (0, 1, 0)
            self.ROTATE_FK_ORDER = "zxy"

    # Функция для быстрой очистки выделения
    def clearSelection(self):
        cmds.select(clear=True)

    # Создает локатор в области таза и в области начала шеи
    def createLocators(self):
        locators = {}

        for item in self.LOCATORS:
            locators[cmds.spaceLocator(name = NamingAgreementHandler(base = item, suffix=NAMING["locatorSuffix"]).nodeName)[0]] = self.LOCATORS[item]
        self.LOCATORS = locators
        for item in self.LOCATORS:
            cmds.setAttr("{}.scale".format(item), self.LOCK_SCALE, self.LOCK_SCALE, self.LOCK_SCALE)
            cmds.setAttr("{}.overrideEnabled".format(item), 1)
            cmds.setAttr("{}.overrideColor".format(item), 17)
            cmds.setAttr("{}.translate".format(item), self.LOCATORS[item][0], self.LOCATORS[item][1], self.LOCATORS[item][2])
            self.clearSelection()

    # Сохраняет новые позиции локатора после модификации пользователем их во Вьюпорте
    def updateLocators(self):
        for item in self.LOCATORS:
            self.LOCATORS[item] = cmds.xform(item, query = True, translation = True, worldSpace = True)

    # Удаляет локаторы
    def delLocators(self):
        for item in self.LOCATORS:
            cmds.delete(item)

    # Согласно позициям локаторов создает джоинты для позиционирования их пользователем
    def createPositionJoints(self, num = 2):
        self.delLocators()
        self.clearSelection()
        delta = [(self.LOCATORS[self.LOCATORS.keys()[0]][z] - self.LOCATORS[self.LOCATORS.keys()[1]][z]) / (num - 1 ) for z in range(0,3)]
        for n in range(num):
            self.joints.append(cmds.joint(position = (delta[x] * n  + self.LOCATORS[self.LOCATORS.keys()[1]][x] for x in range(0,3) ),
                                          radius = self.J_RADIUS,
                                          name = NamingAgreementHandler(base = "joint_" + str(n + 1),
                                                                         suffix = NAMING["jointSuffix"]).nodeName))
            cmds.setAttr("{}.overrideEnabled".format(self.joints[n]), 1)
            cmds.setAttr("{}.overrideColor".format(self.joints[n]), 17)
            self.clearSelection()

    # Сброс изменений, выполненных пользователем над управляющими джоинтами
    def resetPositionJoints(self):
        for n in self.joints:
            cmds.setAttr("{}.overrideEnabled".format(n), 0)
            cmds.setAttr("{}.radius".format(n) , self.J_RADIUS)

    # Соединяет джоинты
    def connectJoints(self, joints):
        for n in range(len(joints) - 1):
            cmds.parent(joints[n + 1], joints[n])

    # Создает рабочие джоинты по джоинтам позиционирования
    def createSpineJoints(self):
        self.resetPositionJoints()
        self.connectJoints(self.joints)

        for n in range(0, len(self.joints) - 1):
            self.joints[n] = cmds.rename(self.joints[n], NamingAgreementHandler(base = NAMING["spineJointName"] + "_" + str(n + 1),
                                                                                 suffix=NAMING["jointSuffix"]).nodeName)

        cmds.makeIdentity(self.joints[0], rotate = True)

        # Установка ориентации джоинтов спины
        cmds.joint(self.joints[0], edit=True, orientJoint = "xzy", secondaryAxisOrient = "xup",
                   children = True, zeroScaleOrient = True)

        # Удаляем последний джоинт и возвращаем его позицию как позицию начала шеи
        self.neckRootPosition = cmds.xform(self.joints[-1], query=True, translation=True, worldSpace=True)
        cmds.delete(self.joints.pop())

    # Создает 2 джоинта, контролирующие кривую IK spline системы
    def createBindJoints(self):
        self.bindJoints.append(cmds.duplicate(self.joints[0], parentOnly=True,
                                                   name=NamingAgreementHandler(base=NAMING["hipName"],
                                                                               suffix=NAMING["jointSuffix"]).nodeName)[0])
        self.bindJoints.append(cmds.duplicate(self.joints[-1], parentOnly=True,
                                                   name=NamingAgreementHandler(base=NAMING["shoulderName"],
                                                                               suffix=NAMING["jointSuffix"]).nodeName)[0])
        cmds.parent(self.bindJoints[1], world=True)

        # Сброс ориентации джоинтов
        for x in self.bindJoints:
            cmds.joint(x, edit = True,  orientJoint = "none", zeroScaleOrient = True)

    # Создает IK Spline систему, для управления джоинтами спины
    def createIkControls(self):
        for n in self.bindJoints:
            num = -len(NAMING["jointSuffix"]) - 1
            self.ikControls.append(ControllerAgreementHandler(name = n[:num], driven = n,
                                                              scale = self.CONTROL_SCALE))
        for x in self.ikControls:
            x.setRotateOrder(self.ROTATE_ORDER)
            x.setLimitedKeyability(("vis","sx","sy","sz"))
            conName = cmds.parentConstraint(x.controlName, x.driven)[0]
            cmds.rename(conName, NamingAgreementHandler(assetName="", side="", base = x.driven,
                                                                       suffix = NAMING["parentConstraintSuffix"]).nodeName)

    # Создает Ik Spline систему
    def createIkSpineSystem(self):
        self.clearSelection()
        cmds.select(self.joints[0], self.joints[-1], add = True)
        self.ikSystemObjs = cmds.ikHandle(solver = "ikSplineSolver", simplifyCurve = False)
        newObjs = []
        for x in range(len(self.ikSystemObjs)):
            if x == 0:
                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=NAMING["spineJointName"],
                                                                   suffix=NAMING["ikHandleSuffix"]).nodeName))
            elif x == 2:

                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=NAMING["spineJointName"],
                                                      suffix=NAMING["curveSuffix"]).nodeName))

                self.clearSelection()

                cmds.skinCluster(self.bindJoints, newObjs[-1], bindMethod = 0, normalizeWeights = 1, weightDistribution = 0,
                                 maximumInfluences =  2, obeyMaxInfluences = True, dropoffRate = 4,
                                 removeUnusedInfluence = True )

            if x == 1:
                newObjs.append(cmds.rename(self.ikSystemObjs[x], NamingAgreementHandler(base=NAMING["spineJointName"],
                                                      suffix=NAMING["effectorSuffix"]).nodeName))
        self.ikSystemObjs = newObjs

    # Создает систему маштабирования основных джоинтов вдоль оси X
    def setupStretch(self):

        # Создаем ноду для вычисления длины управляющей кривой
        self.arclenNode = cmds.arclen(self.ikSystemObjs[2], constructionHistory = True)
        self.arclenNode = cmds.rename(self.arclenNode, NamingAgreementHandler(base=NAMING["spineJointName"],
                                                      suffix=NAMING["curveInfoSuffix"]).nodeName)

        # Сохраняем исходную длину кривой для дальнейших вычислений
        curveLength = cmds.getAttr("{}.arcLength".format(self.arclenNode))

        # Создаем ноду, где вычисляем во сколько раз изменилась длина кривой по сравнению с исходным значением
        self.baseStretch = cmds.createNode("multiplyDivide", name = NamingAgreementHandler(base=NAMING["spineJointName"],
                                                                            suffix=NAMING["stretchSuffix"]).nodeName)
        # Соединяем нужные атрибуты, выставляем еужную операции
        cmds.setAttr("{}.operation".format(self.baseStretch), 2)
        cmds.setAttr("{}.input2X".format(self.baseStretch), curveLength)
        cmds.connectAttr("{}.arcLength".format(self.arclenNode), "{}.input1X".format(self.baseStretch))
        # Возвращаем маштаб каждому джоинту спины вдоль оси Х
        for x in range(len(self.joints) - 1):
            cmds.connectAttr("{}.outputX".format(self.baseStretch),"{}.scaleX".format(self.joints[x]))

    # Создает систему маштабирования основных джоинтов вдоль побочных осей
    def setupSquash(self):
        self.baseSquash = cmds.createNode("multiplyDivide", name = NamingAgreementHandler(base=NAMING["spineJointName"],
                                                      suffix=NAMING["squashSuffix"]).nodeName)
        cmds.setAttr("{}.operation".format(self.baseSquash), 3)
        cmds.connectAttr("{}.outputX".format(self.baseStretch),"{}.input1X".format(self.baseSquash))
        cmds.setAttr("{}.input2X".format(self.baseSquash),-0.5)

        self.createSqshStchCont()

    # Настраивает скручивание IK spline системы (Advanced Twist Controls)
    def setupTwist(self):
        ikHndl = self.ikSystemObjs[0]

        cmds.setAttr("{}.dTwistControlEnable".format(ikHndl), 1)
        cmds.setAttr("{}.dWorldUpType".format(ikHndl), 4)
        cmds.setAttr("{}.dForwardAxis".format(ikHndl), 0)
        cmds.setAttr("{}.dWorldUpAxis".format(ikHndl), 1)
        cmds.setAttr("{}.dWorldUpVector".format(ikHndl), self.twistUp[0], self.twistUp[1], self.twistUp[2])
        cmds.setAttr("{}.dWorldUpVectorEnd".format(ikHndl), self.twistUp[0], self.twistUp[1], self.twistUp[2])
        cmds.connectAttr("{}.worldMatrix".format(self.bindJoints[0]), "{}.dWorldUpMatrix".format(ikHndl))
        cmds.connectAttr("{}.worldMatrix".format(self.bindJoints[1]), "{}.dWorldUpMatrixEnd".format(ikHndl))

    # Создает кривую для артистичного контролирования эффекта растяжения/сжатия
    def createSqshStchCont(self):
        attName = "splineStretch"

        cmds.addAttr(self.ikControls[1].controlName, longName = attName , attributeType = "float", keyable = True)
        self.clearSelection()
        joints_num = len(self.joints) - 1
        cmds.setKeyframe(self.ikControls[1].controlName, time = [1,joints_num], value = 1, attribute = attName)
        curveControl = cmds.keyframe(self.ikControls[1].controlName, attribute = attName, name = True, query = True)[0]

        # Для каждого джоинта создаем систему считывания значения из кривой, соединяем соответсвующие аттрибуты,
        # выставляем нужные операции нодам
        for x in range(joints_num):
            jointFrCache = cmds.createNode("frameCache", name=NamingAgreementHandler(assetName="", side="",
                                                                                     base=self.joints[x],
                                                                                     suffix="frameCache").nodeName)
            cmds.setAttr("{}.varyTime".format(jointFrCache), x + 1)
            cmds.connectAttr("{}.output".format(curveControl), "{}.stream".format(jointFrCache))

            jointPow = cmds.createNode("multiplyDivide", name=NamingAgreementHandler(assetName="", side="",
                                                                                     base=self.joints[x],
                                                                                     suffix="pow").nodeName)
            cmds.setAttr("{}.operation".format(jointPow), 3)
            cmds.connectAttr("{}.varying".format(jointFrCache), "{}.input2X".format(jointPow))
            cmds.connectAttr("{}.outputX".format(self.baseSquash), "{}.input1X".format(jointPow))

            cmds.connectAttr("{}.outputX".format(jointPow), "{}.scaleY".format(self.joints[x]))
            cmds.connectAttr("{}.outputX".format(jointPow), "{}.scaleZ".format(self.joints[x]))

    # Создание FK джоинтов и настройка их контроллеров
    def createFkCtrlJoints(self, num = 4):
        fkControls = []

        self.clearSelection()
        delta = [(cmds.xform(self.joints[-1], query = True, translation = True, worldSpace = True)[z] -
                  self.LOCATORS[self.LOCATORS.keys()[1]][z]) / (num - 1) for z in range(0, 3)]
        # Создаем джоинты
        for n in range(num):
            if(n == 0):
                self.fkJoints.append(
                    cmds.joint(position=(delta[x] * n + self.LOCATORS[self.LOCATORS.keys()[1]][x] for x in range(0, 3)),
                               radius=self.J_RADIUS,
                               name=NamingAgreementHandler(base=NAMING["hipName"] + "_FK",
                                                           suffix=NAMING["jointSuffix"]).nodeName))
            elif(n == num - 1):
                self.fkJoints.append(
                    cmds.joint(position=(delta[x] * n + self.LOCATORS[self.LOCATORS.keys()[1]][x] for x in range(0, 3)),
                               radius=self.J_RADIUS,
                               name=NamingAgreementHandler(base=NAMING["shoulderName"] + "_FK",
                                                           suffix=NAMING["jointSuffix"]).nodeName))

            else:
                self.fkJoints.append(
                    cmds.joint(position=(delta[x] * n + self.LOCATORS[self.LOCATORS.keys()[1]][x] for x in range(0, 3)),
                               radius=self.J_RADIUS,
                               name=NamingAgreementHandler(base=NAMING["spineJointName"] + "_" + str(n) + "_"  + "FK",
                                                           suffix=NAMING["controlSuffix"]).nodeName))

        # Выставлем необходимую ориентацию у джоинтов
        cmds.joint(self.fkJoints[0], edit=True, orientJoint="xzy", secondaryAxisOrient="xup",children=True,
                   zeroScaleOrient=True)

        # Создаем контроллеры для FK джоинтов
        for n in range(num):
            if(n > 0 and n < num-1 ):
                fkCtrlName = self.fkJoints[n][:-5]
                fkControls.append(ControllerAgreementHandler(name=NamingAgreementHandler(assetName="", side="",
                                                                                         base=fkCtrlName).nodeName,
                                                             shape="circleZ",
                                                             driven=self.fkJoints[n], scale=self.CONTROL_SCALE,
                                                             suffix="", toOrign = True))

                fkControls[-1].setRotateOrder(self.ROTATE_FK_ORDER)
                cmds.parent("{}Shape".format(fkControls[-1].controlName), self.fkJoints[n], shape = True, relative = True)
                fkControls[-1].deleteAll()

    # Создание общего контроллера торса
    def createBodyControl(self):
        self.bodyCtrl = ControllerAgreementHandler(shape = "square", name = NamingAgreementHandler(base = NAMING["bodyCtrlName"]).nodeName, driven = self.fkJoints[0],
                                                              scale = self.CONTROL_SCALE, pos = False)
        self.bodyCtrl.setRotateOrder(self.ROTATE_ORDER)
        self.bodyCtrl.setLimitedKeyability(("vis","sx","sy","sz"))
        cmds.setAttr("{}.rotateX".format(self.bodyCtrl.controlName),-90)
        cmds.makeIdentity(self.bodyCtrl.controlName, apply=True, rotate=True)

        # Заносим необходимые элементы под управление данного контролера
        cmds.parent(self.fkJoints[0], self.bodyCtrl.controlName)
        cmds.parent(self.ikControls[0].lastNode, self.fkJoints[0])
        cmds.parent(self.ikControls[1].lastNode, self.fkJoints[-1])

    # Чистит сцену
    def cleanScene(self):
        self.cleanOutliner()
        self.setupRigRelocation()
        self.setLayers()

    # Разделяет элементы рига по слоям, отключает визуализацию лишних элементов сетапа
    def setLayers(self):
        self.clearSelection()
        self.fkLayer = cmds.createDisplayLayer(name = NamingAgreementHandler(base=NAMING["bodyCtrlName"] + "_FK",
                                                                             suffix=NAMING["layer"]).nodeName, empty = True)
        cmds.setAttr("{}.color".format(self.fkLayer),6)
        self.ikLayer = cmds.createDisplayLayer(name=NamingAgreementHandler(base=NAMING["bodyCtrlName"] + "_IK",
                                                                           suffix=NAMING["layer"]).nodeName, empty=True)
        cmds.setAttr("{}.color".format(self.ikLayer), 17)
        self.torsoBaseLayer = cmds.createDisplayLayer(name=NamingAgreementHandler(base=NAMING["bodyCtrlName"] + "_BASE",
                                                                           suffix=NAMING["layer"]).nodeName, empty=True)
        cmds.setAttr("{}.color".format(self.torsoBaseLayer), 13)

        cmds.editDisplayLayerMembers(self.torsoBaseLayer,self.rootGrp, self.bodyCtrl.controlName, noRecurse=True)
        cmds.editDisplayLayerMembers(self.ikLayer, [self.ikControls[x].controlName for x in range(2)], noRecurse=True)
        cmds.editDisplayLayerMembers(self.fkLayer, self.fkJoints, noRecurse=True)

    # Группирует элементы сетапа в Outliner
    def cleanOutliner(self):
        self.DNTGrp = cmds.group(self.bindJoints[:], self.ikSystemObjs[0], self.ikSystemObjs[2], self.joints[0],
                                 name=NamingAgreementHandler(base=NAMING["bodyCtrlName"] + "_" + NAMING["DNTName"],
                                                             suffix=NAMING["groupSuffix"]).nodeName)
        cmds.xform(self.DNTGrp, objectSpace=True, pivots=(0, 0, 0))

        self.torsoGrp = cmds.group(self.DNTGrp, self.bodyCtrl.lastNode,
                                 name=NamingAgreementHandler(base=NAMING["bodyCtrlName"],
                                                             suffix=NAMING["groupSuffix"]).nodeName)
        cmds.xform(self.torsoGrp, objectSpace=True, pivots=(0, 0, 0))
        self.cleanKAttr()

    # Отключает лишние аттрибуты элементов сетапа
    def cleanKAttr(self):
        setLimitedKeyability(self.DNTGrp, ("sx", "sy", "sz", "tx", "ty", "tz", "rx", "ry", "rz"))
        cmds.setAttr("{}.visibility".format(self.DNTGrp),0)
        setLimitedKeyability(self.torsoGrp, ("vis", "sx", "sy", "sz", "tx", "ty", "tz", "rx", "ry", "rz"))

        for x in self.ikControls:
            setLimitedKeyability(x.lastNode,
                                 ("vis", "sx", "sy", "sz", "tx", "ty", "tz", "rx", "ry", "rz"))

        fLen = len(self.fkJoints)
        for n in range(fLen):
            if (n == 0):
                setLimitedKeyability(self.fkJoints[n],
                                     ("vis", "sx", "sy", "sz", "tx", "ty", "tz", "rx", "ry", "rz", "rad"))
            elif (n == fLen - 1):
                setLimitedKeyability(self.fkJoints[n],
                                     ("vis", "sx", "sy", "sz", "tx", "ty", "tz", "rx", "ry", "rz", "rad"))
            else:
                setLimitedKeyability(self.fkJoints[n],
                                     ("vis", "sx", "sy", "sz", "tx", "ty", "tz", "rad"))

    # Создает глобальный контроллер над всем сетапом
    def setupRigRelocation(self):
        self.rootGrp = ControllerAgreementHandler( name=NamingAgreementHandler(base=NAMING["allGrpName"],
                                                              suffix=NAMING["groupSuffix"]).nodeName, shape = "circleY",
                                                pos = False, scale=self.CONTROL_SCALE).lastNode
        cmds.parent(self.torsoGrp, self.rootGrp)
        cmds.setAttr("{}.inheritsTransform".format(self.ikSystemObjs[2]), 0)

        # Создаем систему компенсации маштабирования глобального контроллера системы рига для кривой IK Spline
        newScaleName = "globalScale"
        cmds.connectAttr("{}.scaleY".format(self.rootGrp), "{}.scaleX".format(self.rootGrp))
        cmds.connectAttr("{}.scaleY".format(self.rootGrp), "{}.scaleZ".format(self.rootGrp))
        setLimitedKeyability(self.rootGrp, ("sx", "sz"))
        cmds.aliasAttr(newScaleName, "{}.scaleY".format(self.rootGrp))
        scaleCompNode = cmds.createNode("multiplyDivide", name=NamingAgreementHandler(base = newScaleName,
                                                               suffix="mult").nodeName)
        cmds.connectAttr("{}.{}".format(self.rootGrp, newScaleName), "{}.input2X".format(scaleCompNode), force =True)
        cmds.connectAttr("{}.arcLength".format(self.arclenNode), "{}.input1X".format(scaleCompNode), force =True)
        cmds.connectAttr("{}.outputX".format(scaleCompNode), "{}.input1X".format(self.baseStretch), force =True)
        cmds.setAttr("{}.operation".format(scaleCompNode), 2)

    def getNeckRootPosition(self):
        return self.neckRootPosition

    def getRootNode(self):
        return self.rootGrp

class HeadRig:
    

