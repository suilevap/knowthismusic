from math import sqrt, cos, sin
import PIL
import numpy
from PIL import Image, ImageDraw
from api.vector2 import Vector2
from api.gameinfo import *
from visibility import Wave

from Queue import PriorityQueue 
import math


class MapAnalyzeVisibility(object):
    """description of class"""

    def __init__(self, map):
        self.map = map
        self.w = len(self.map)
        self.h = len(self.map[0])
        self.visibleSectors = self.buildLOS()
      

        self.averageMin = [ [(self.visibleSectors[0][x][y][0]
                                     +self.visibleSectors[1][x][y][0]
                                     +self.visibleSectors[2][x][y][0]
                                     +self.visibleSectors[3][x][y][0]
                                     +self.visibleSectors[4][x][y][0]
                                     +self.visibleSectors[5][x][y][0]
                                     +self.visibleSectors[6][x][y][0]
                                     +self.visibleSectors[7][x][y][0]
                                     +7)/8.0 for y in range(self.h)] for x in range(self.w)] 
        self.distanceField = [ [min([self.visibleSectors[0][x][y][0],
                                     self.visibleSectors[1][x][y][0],
                                     self.visibleSectors[2][x][y][0],
                                     self.visibleSectors[3][x][y][0],
                                     self.visibleSectors[4][x][y][0],
                                     self.visibleSectors[5][x][y][0],
                                     self.visibleSectors[6][x][y][0],
                                     self.visibleSectors[7][x][y][0]])
                                     for y in range(self.h)] for x in range(self.w)]

        self.maxField = [ [max([self.visibleSectors[0][x][y][0],
                                     self.visibleSectors[1][x][y][0],
                                     self.visibleSectors[2][x][y][0],
                                     self.visibleSectors[3][x][y][0],
                                     self.visibleSectors[4][x][y][0],
                                     self.visibleSectors[5][x][y][0],
                                     self.visibleSectors[6][x][y][0],
                                     self.visibleSectors[7][x][y][0]])
                                     for y in range(self.h)] for x in range(self.w)]
      

        self.directions =[Vector2(1,0), Vector2(1,-1).normalized(), Vector2(0,-1), Vector2(-1,-1).normalized(), 
                          Vector2(-1,0), Vector2(-1,1).normalized(), Vector2(0,1), Vector2(1,1).normalized()]
        angle = math.pi/8
        self.directions=[rotateVector2(x,angle) for x in self.directions]

        self.dangerMap =[ [(0) for y in range(self.h)] for x in range(self.w)]
        self.pathMap = self.createMapForPathFinding()
        self.dangerMapStatic =[ [ -1 if self.map[x][y]>0 else 1 for y in range(self.h)] for x in range(self.w)]
        self.visibleSafeToCharge = self.generateVisibleSafeMap()
        self.mergeDangerStaticWith(self.visibleSafeToCharge)
        self.cornerPoints = []
        for y in range(self.h):
            for x in range(self.w):
                if self.isCorner(x,y):
                    self.cornerPoints.append(Vector2(x+0.5,y+0.5))

        #self.possibleEnemyPosMapWithBorder =[ [ False for y in range(self.h+2)] for x in range(self.w+2)]
        #self.possibleEnemyPosMapWithBorderTmp =[ [ False for y in range(self.h+2)] for x in range(self.w+2)]
        self.cells = []
        self.wave = Wave((self.w,self.h), lambda x,y: self.map[x][y]>1, lambda x,y: self.cells.append((x,y)))

    def getNewVisiblePoints(self, pos1, pos2):
        self.cells=[]
        self.wave.compute(pos1)
        visiblePoints=self.cells[:]
        self.cells=[]
        self.wave.compute(pos2)
        result =[]
        for p in self.cells:
            if p not in visiblePoints:
                result.append(p)
        return result

    def updatePossibleEnemyPos(self):
        for y0 in range(self.h):
            for x0 in range(self.w):
                x,y=x0+1,y0+1
                self.possibleEnemyPosMapWithBorderTmp[x][y] = (
                    self.possibleEnemyPosMapWithBorder[x-1][y-1] or
                    self.possibleEnemyPosMapWithBorder[x-0][y-1] or
                    self.possibleEnemyPosMapWithBorder[x+1][y-1] or
                    self.possibleEnemyPosMapWithBorder[x-1][y] or
                    self.possibleEnemyPosMapWithBorder[x-0][y] or
                    self.possibleEnemyPosMapWithBorder[x+1][y] or
                    self.possibleEnemyPosMapWithBorder[x-1][y+1] or
                    self.possibleEnemyPosMapWithBorder[x-0][y+1] or
                    self.possibleEnemyPosMapWithBorder[x+1][y+1] )
        
        
    def pointSafeToCharge(self, x,y):
        sectors=self.getAllSectors(Vector2(x,y), 2)
        return len(sectors)==1 or (len(sectors)==2 and (sectors[1]-sectors[0])<=1) or (len(sectors)==3 and abs(sectors[1]-sectors[0])<=1 and abs(sectors[2]-sectors[1])<=1) 

    def generateVisibleSafeMap(self):
        result=[ [(0) for y in range(self.h)] for x in range(self.w)]
        for y in range(self.h):
            for x in range(self.w):
                result[x][y] = 0 if self.pathMap[x][y]==-1 else  (self.averageMin[x][y]*8-self.maxField[x][y])/2#0 if self.pointSafeToCharge(x,y) else 64
        saveImage('saveMap',result)
        return result


    def getNearestCornerPointInRange(self, pos, r):
        best = r;
        result = None
        for p in self.cornerPoints:
            d  = (p-pos).length()
            if d<best:
                result = p
                best = d
        return result

    def getCornerPointInVisibility(self, pos, r):
        points = self.getAllVisiblePoints(pos,r)
        for p in points:
            x,y = p[0], p[1]
            if self.isCorner(x,y):
                return Vector2(x+0.5, y+0.5)
        return None

    def getAllVisiblePoints(self, pos ,r, targetSector = -1, sectorsCount=0, useMax = False, usePrecise=False ):
        result = []
        x0 = int(pos.x)
        y0 = int(pos.y)

        if usePrecise:
            if targetSector!=-1:
                print 'Error! Use precise visibility only with targetSector -1'
            self.cells=[]
            self.wave.compute(pos)
            for p in self.cells:
                x,y=p
                if ((x0-x)*(x0-x)+(y0-y)*(y0-y))<=r*r:
                    result.append(p)
            return result


        minX, minY = self.clamp(int(pos.x-r), 0, self.w), self.clamp(int(pos.y-r), 0, self.h)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w), self.clamp(int(pos.y+r), 0, self.h) 
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                delta = Vector2(x,y)-pos
                sectorFloat = self.getSectorIndexFloat(delta)
                sector = int(sectorFloat)
                if targetSector==-1 or self.getSectorDiff(targetSector,sectorFloat)<=sectorsCount:
                    r0Min, r0Max = self.visibleSectors[sector][x0][y0]
                    r1Min, r1Max = self.visibleSectors[(sector+4)%8][x][y]

                    d = max(abs(x0-x),abs(y0-y))
                    if (((r0Min>= d or r1Min>=d )
                        or (useMax and r0Max>=d and r1Max>=d)) and ((x0-x)*(x0-x)+(y0-y)*(y0-y))<=r*r):
                        result.append((x,y))
        return result

    
    def updateDangerStatic(self, pos, r, cost = 128):
        self.updateMap(self.dangerMapStatic, pos, Vector2(0,0), 0, r, cost)

    def mergeDangerStaticWith(self, data):
        for y in range(self.h):
            for x in range(self.w):
                if self.dangerMap[x][y] != -1:
                    self.dangerMap[x][y]+=data[x][y]

    def updateDanger(self, pos, dir, n, r, cost = 16):
        self.updateMap(self.dangerMap, pos, dir, n, r, cost)


    def updateMap(self, map, pos, dir, n, r, cost = 16):
        if dir.x != 0 or dir.y!= 0:
            sector = self.getSectorIndexFloat(dir)
        else:
            sector = -1
        x0 = int(pos.x)
        y0 = int(pos.y)
        points = self.getAllVisiblePoints(pos, r, -1, 0, True)
        for visiblePoint in points:
            x,y = visiblePoint
               
            if map[x][y]!=-1 and (x!=x0 or y!=y0):
                delta = Vector2(x,y)-pos
                sectorFloat = self.getSectorIndexFloat(delta)
                if sector==-1 or self.getSectorDiff(sector,sectorFloat)<=n:
                    if cost != -1:
                        map[x][y] += cost
                    else:
                        map[x][y] = cost
                else:
                    if cost != -1:
                        map[x][y] += cost/8

    def updateDangerStep(self, bots, r):
        self.dangerMap =[ [ self.dangerMapStatic[x][y] for y in range(self.h)] for x in range(self.w)]
        for bot in bots:
            if bot.state == BotInfo.STATE_DEFENDING:
                self.updateDanger(bot.position, bot.facingDirection, 1, r, -1)
            else:
                self.updateDanger(bot.position, bot.facingDirection, 1, r, 16)

        saveImage("DangerMap", self.dangerMap) 


    def getPathThroughDanger(self, start, end):
        return getPath(start, end, self.dangerMap)

    def buildDirecionMap(self, dangerPos):
        self.bestDirectionsMap =[ [(0,0) for y in range(self.h)] for x in range(self.w)]
        for x in range(0,self.w):
            for y in range(0,self.h):
                dirs =[(i, self.visibleSectors[i][x][y], self.visibleSectors[(i+7)%8][x][y]) for i in range(8)]
                delta = dangerPos-Vector2(x,y)
                dangerSector = self.getSectorIndex(delta)
                dangerSector2 = (dangerSector+1)%8

                bestI = max(dirs, key=lambda d: (d[1][0]+d[2][0]+ (d[1][1]+d[2][1])/16) * (2 if (d[0]==dangerSector or d[0]==dangerSector2) else 1) )
                bestDirection = bestI[0]
                self.bestDirectionsMap[x][y]=bestDirection


    def getSectorIndex(self, delta):
        x = delta.x
        y = delta.y
        if x >= 0 and y <= 0 and x>=-y:
            return 0
        elif x >= 0 and y <= 0 and x<-y:
            return 1
        elif x <= 0 and y <=0 and -x<-y:
            return 2
        elif x<=0 and y<=0 and -x>=-y:
            return 3
        elif x<=0 and y>=0 and -x>=y:
            return 4
        elif x<=0 and y>=0 and -x<y:
            return 5
        elif x>=0 and y>=0 and x<y:
            return 6
        elif x>=0 and y>=0 and x>=y:
            return 7

    def getSectorIndexFloat(self, delta):
        x = delta.x
        y = delta.y
        if x ==0 and y ==0:
            return 0

        if x > 0 and y <= 0 and x>=-y:
            return 0 + -y/x
        elif x >= 0 and y < 0 and x<-y:
            return 1 + (1-x/-y)
        elif x <= 0 and y <0 and -x<-y:
            return 2 + (-x/-y) 
        elif x<0 and y<=0 and -x>=-y:
            return 3 + (1-(-y/-x))
        elif x<0 and y>=0 and -x>=y:
            return 4 + y/-x
        elif x<=0 and y>0 and -x<y:
            return 5  +(1-(-x/y))
        elif x>=0 and y>0 and x<y:
            return 6 + x/y
        elif x>0 and y>=0 and x>=y:
            return 7 + (1-y/x)
        else:
            return 0
    
    def getInvSector(self, sector):
        return (sector+4)%8

    def isCorner(self, x,y):
        a = 1
        #right = max([self.visibleSectors[0][x][y][1],self.visibleSectors[7][x][y][1]])<=a
        #up = max([self.visibleSectors[1][x][y][1],self.visibleSectors[2][x][y][1]])<=a
        #left = max([self.visibleSectors[3][x][y][1],self.visibleSectors[4][x][y][1]])<=a
        #down = max([self.visibleSectors[5][x][y][1],self.visibleSectors[6][x][y][1]])<=a
        right = self.distanceField[x+1][y]<0 if x<self.w-1 else True
        up = self.distanceField[x][y-1]<0 if y>0 else True
        left = self.distanceField[x-1][y]<0 if x>0 else True
        down = self.distanceField[x][y+1]<0 if y<self.h-1 else True

        return (left and up) or (up and right) or (right and down) or (down and left)
       
    def getBreakingPoints(self, path):
        result = []
        deltaIndex = 1
        for i in range(deltaIndex,len(path)):
            x = int(path[i].x)
            y = int(path[i].y)
            xprev = int(path[i-deltaIndex].x)
            yprev = int(path[i-deltaIndex].y)
            delta = self.averageMin[x][y]-self.averageMin[xprev][yprev];
            
            result.append((path[i], int(delta)))
        savePathWithText('pathDelta',result, self.map)
        return result

    def getBreakingMap(self, paths, r, allPathsData = None,ignorePoints = None):
       
        ranks =[ [(0) for y in range(self.h)] for x in range(self.w)]
        rank = 1.0
        for path in paths:
            i = 0;
            for p in path:
                x,y=int(p.x), int(p.y)
                part = i*1.0/len(path)
                rank = 1.0-abs(0.95-part)
                prevPoint = path[i-1]
                i+=1
                
                if ignorePoints!=None and (x,y) in ignorePoints:
                    continue
                
                points = self.getAllVisiblePoints(p, r, self.getInvSector(self.getSectorIndexFloat(p-prevPoint)), 2)
                for visiblePoint in points:
                    x,y = visiblePoint
                    if (self.distanceField[x][y] >= 0):
                        d = rank/(self.distanceField[x][y]+1)
                        if self.isCorner(x,y):
                            d *= 16
                        ranks[x][y] = max([ranks[x][y] ,d])

        if allPathsData != None:
            for x in range(0,self.w):
                for y in range(0,self.h):
                    if allPathsData[x][y]!=0:
                        ranks[x][y] /= allPathsData[x][y]+1
        #for path in allPaths:
        #    i = 0;
        #    for p in path:
        #        x,y=int(p.x), int(p.y)
        #        part = i*1.0/len(path)
        #        prevPoint = path[i-1]
        #        i+=1

        #        if ignorePoints!=None and (x,y) in ignorePoints:
        #            continue
        #        
        #        points = self.getAllVisiblePoints(p, r, self.getSectorIndexFloat(p-prevPoint), 1)
        #        for visiblePoint in points:
        #            x,y = visiblePoint
        #            if (self.distanceField[x][y] >= 0):
        #                ranks[x][y] /= 1.25

            #rank += 1.0/len(path)

        #for x in range(0,self.w):
        #    for y in range(0,self.h):
        #        if (ranks[x][y]>self.distanceField[x][y]):
        #            ranks[x][y] -= self.distanceField[x][y]
        #        else:
        #            ranks[x][y] = 0
        saveImage("breaking", ranks) 
        return ranks

    def MergeDataOnPath(self, path,r, data, value):
        i = 0;
        for p in path:
            x,y=int(p.x), int(p.y)
            part = i*1.0/len(path)
            prevPoint = path[i-1]
            i+=1
                
            points = self.getAllVisiblePoints(p, r, self.getSectorIndexFloat(p-prevPoint), 1)
            for visiblePoint in points:
                x,y = visiblePoint
                if (self.map[x][y] == 0):
                    data[x][y] += value

    def getTheBestPos(self, data):
        best = 0
        for x in range(0,self.w):
            for y in range(0,self.h):
                if (data[x][y]>best):
                    result = (x,y)
                    best = data[x][y]
        return result

    def createMapForPathFinding(self):
        return [ [(-1 if self.map[x][y]>0 else 1)  for y in range(self.h)] for x in range(self.w)]
   
    def getBestBreakingPoints(self, startPoints, end, rPrefered, rControl, n):
        pathMaxLength = 50
        tmpMap = self.createMapForPathFinding()
        result = []
        allpaths = []
        allPathData = [ [0  for y in range(self.h)] for x in range(self.w)]

        for i in range(n):
            start = startPoints[i%len(startPoints)]
            path = getPath(start, end, tmpMap)
            savePath("path_iteration"+str(i), path, tmpMap)
            if len(path)<1:
                break

            allpaths.append(path[-pathMaxLength:])

            self.MergeDataOnPath(path, rPrefered, allPathData, 1)
            breakingMap = self.getBreakingMap([path], rPrefered, allPathData)
            x,y = self.getTheBestPos(breakingMap)
            bestPoint = Vector2(x+0.5,y+0.5)

            pathMap = [ [tmpMap[x][y]  for y in range(self.h)] for x in range(self.w)]
            
            for p in path:
                if self.checkVisibility(bestPoint, p):
                    bestPair = (bestPoint,[p], path, pathMap, i)
                    break
            result.append(bestPair)
            sector = self.getSectorIndexFloat(bestPair[1][0]-bestPair[0])

            visiblePoints = self.getAllVisiblePoints(bestPoint, rControl, sector, 1)
            #for p in path:
            #    x,y=int(p.x), int(p.y)               
            #    if  tmpMap[x][y] > 0:
            #        tmpMap[x][y] += 128
            #        if tmpMap[x][y]>255:
            #            tmpMap[x][y] = 255
            for x,y in visiblePoints:
                if  tmpMap[x][y] > 0:
                    tmpMap[x][y] += 128
                    if tmpMap[x][y]>255:
                        tmpMap[x][y] = 255
        savePath("allBreakingPoints", result, self.createMapForPathFinding())
        saveImage('corners', [ [ 0 if self.distanceField[x][y]<0 else 124 if self.isCorner(x,y) else 255 for x in range(self.w)] for y in range(self.h)] )
        saveImage('allPathData', allPathData)
        return result

    def getMaxD(self, pos1, pos2):
        x1,y1 = int(pos1.x),int(pos1.y)
        #x2,y2 = int(pos2.x),int(pos2.y)
        sector = self.getSectorIndex(pos2-pos1)
        r0Min = self.visibleSectors[sector][x1][y1][0]
        return r0Min

    def checkVisibility(self, pos1, pos2):
        result = False
        x1,y1 = int(pos1.x),int(pos1.y)
        x2,y2 = int(pos2.x),int(pos2.y)
        sector = self.getSectorIndex(pos2-pos1)
        sector2 = (sector+4)%8
        r0Min = self.visibleSectors[sector][x1][y1][0]
        r1Min = self.visibleSectors[sector2][x2][y2][0]
        d = max(abs(x2-x1),abs(y2-y1))
        if (r0Min>= d or r1Min>=d ):
            result = True
        return result


    def getBestDirection(self, pos):
        x = int(pos.x)
        y = int(pos.y)
        return self.directions[self.bestDirectionsMap[x][y]]

    def getSectorDiff(self, sector1, sector2):
        diff = abs(sector2 - sector1)
        if diff>4:
            diff = 8 - diff
        return diff

    def getAllDirections(self, pos, dmin, targetSector = -1, targetSectorCount = 1):
        return [self.directions[i] for i in self.getAllSectors(pos, dmin, targetSector, targetSectorCount)]

    def getAllSectors(self, pos, dmin, targetSector = -1, targetSectorCount = 1):
        x = int(pos.x)
        y = int(pos.y)
        return [i for i in range(0,8)
                if (targetSector == -1 or self.getSectorDiff(targetSector,i)<=targetSectorCount) and self.visibleSectors[i][x][y][0]>=dmin]

    def getBestPosition(self, pos, r):
        minX, minY = self.clamp(int(pos.x-r), 0, self.w), self.clamp(int(pos.y-r), 0, self.h)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w), self.clamp(int(pos.y+r), 0, self.h)    
        rangeX, rangeY = maxX - minX, maxY - minY

        if (rangeX == 0.0) or (rangeY == 0.0):
            return None 
        bestPos = None
        bestResult = 255
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                if (self.averageMin[x][y]<bestResult):
                    bestPos = Vector2(x,y)
                    bestResult = self.averageMin[x][y]

        return bestPos

    def getMin(self, pos,r,data, key):
        minX, minY = self.clamp(int(pos.x-r), 0, self.w), self.clamp(int(pos.y-r), 0, self.h)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w), self.clamp(int(pos.y+r), 0, self.h)    
        rangeX, rangeY = maxX - minX, maxY - minY

        if (rangeX == 0.0) or (rangeY == 0.0):
            return None 
        bestPos = None
        bestResult = 0
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                if (bestPos == None or data[x][y]<bestResult):
                    bestPos = Vector2(x+0.5,y+0.5)
                    bestResult = data[x][y]
        return bestPos

    def getBestPositionSector(self, pos, r, sector):
        minX, minY = self.clamp(int(pos.x-r), 0, self.w), self.clamp(int(pos.y-r), 0, self.h)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w), self.clamp(int(pos.y+r), 0, self.h)    
        rangeX, rangeY = maxX - minX, maxY - minY

        if (rangeX == 0.0) or (rangeY == 0.0):
            return None 
        bestPos = None
        bestResult = 255
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                currentResult = self.visibleSectors[sector][x][y][0] - self.averageMin[x][y]
                if (currentResult<bestResult):
                    bestPos = Vector2(x,y)
                    bestResult = currentResult

        return bestPos

    def buildLOS(self):

        def buildLosDir(rangeX, rangeY, dx1, dy1, dx2, dy2):

            result =[ [(0,0) for y in range(-1, self.h+1)] for x in range(-1,self.w+1)]
            for y in rangeY:
                for x in rangeX:
                    #to take into account borders
                    xWithBorder = x +1
                    yWithBorder = y + 1
                    if (self.map[x][y] <= 1):
                        result[xWithBorder][yWithBorder] = (
                                        min([
                                             result[xWithBorder + dx1][yWithBorder + dy1][0]+1,
                                             result[xWithBorder + dx2][yWithBorder + dy2][0]+1]),
                                        max([
                                             result[xWithBorder + dx1][yWithBorder + dy1][1]+1,
                                             result[xWithBorder + dx2][yWithBorder + dy2][1]+1]))
                    else:
                        result[xWithBorder][yWithBorder] = (-1,-1)
            return [ result[x][1:self.h+1] for x in range(1,self.w+1)]
       
        finalResult =[
                buildLosDir(range(self.w-1, -1, -1), range(0,self.h), 1, 0, 1, -1),
                buildLosDir(range(0,self.w), range(0,self.h), 0, -1, 1, -1),
                buildLosDir(range(0,self.w), range(0,self.h), 0, -1, -1, -1),
                buildLosDir(range(0,self.w), range(0,self.h), -1, 0, -1, -1),

                buildLosDir(range(0,self.w), range(self.h-1,-1,-1), -1, 0, -1, 1),
                buildLosDir(range(0,self.w), range(self.h-1,-1,-1), 0, 1, -1, 1),
                buildLosDir(range(0,self.w), range(self.h-1,-1,-1), 0, 1, 1, 1),
                buildLosDir(range(self.w-1, -1, -1), range(self.h-1,-1,-1), 1, 0, 1, 1)]


        return finalResult

    #def getDistPathStraight(self, path)

    def debug(self):
        i=0
        #for d in self.visibleSectors:
        #    saveImage('min_'+str(i), [ [(d[x][y][0])for x in range(self.w)] for y in range(self.h)] )
        #    saveImage('max_'+str(i), [ [(d[x][y][1])for x in range(self.w)] for y in range(self.h)] )
        #    i+=1
        #saveImage('all_min', self.averageMin )

        #saveImage('all_max', [ [(self.visibleSectors[0][x][y][1]
        #                             +self.visibleSectors[1][x][y][1]
        #                             +self.visibleSectors[2][x][y][1]
        #                             +self.visibleSectors[3][x][y][1]
        #                             +self.visibleSectors[4][x][y][1]
        #                             +self.visibleSectors[5][x][y][1]
        #                             +self.visibleSectors[6][x][y][1]
        #                             +self.visibleSectors[7][x][y][1]
        #                             +7)/8 for x in range(self.w)] for y in range(self.h)] )

        #tmpbestDirectionsMap =[ [self.directions[self.bestDirectionsMap[x][y]] if self.map[x][y]==0 else None 
        #                        for y in range(self.h)] for x in range(self.w) ]
        #saveImageVector('Dir', tmpbestDirectionsMap)


    def clamp(self, x, minValue, maxValue):
        return max(minValue, min(x, maxValue))

def getPath(start, end, mapData):
    path,distmap, parent = getPathWithPathDistanceMap(start, end, mapData, True)
    return path

def getPathDistanceMap(start, end, mapData):
    path,distmap, parent = getPathWithPathDistanceMap(start, end, mapData, False)
    return distmap


def getPathWithPathDistanceMap(start, end, mapData, finishWhenFoundPath = True):
    sq2 = math.sqrt(2)
    w = len(mapData)
    h = len(mapData[0])
    distance =[ [(0) for y in range(h)] for x in range(w)]
    parent =[ [None for y in range(h)] for x in range(w)]
    queue = PriorityQueue()
    xstart = int(start.x)
    ystart = int(start.y)
    xend = int(end.x)
    yend = int(end.y)

    def heuristic(x0,y0, x1,y1):
        return math.sqrt((x0-x1)*(x0-x1)+(y0-y1)*(y0-y1))

    def checkPos(d, x, y, dx ,dy, delta):
        x1 =x+dx
        y1 = y+dy
        result = False
        if (x1<0  or x1>=w or y1<0 or y1>=h):
            return False
        fullDistance = d+delta*(mapData[x][y])
        if (mapData[x1][y1]!=-1) and (parent[x1][y1]==None or distance[x1][y1]>fullDistance):
            parent[x1][y1] = (x,y)
            distance[x1][y1] = fullDistance
            heursticD = fullDistance+heuristic(x,y,x1,y1)
            queue._put((heursticD, (x1,y1)))

            if ((x1==xend) and (y1==yend)):
                result = True
        return result

    pathFounded = False
    if checkPos(0, xstart,ystart, 0,0, 0) and finishWhenFoundPath:
        return [Vector2(x+0.5,y+0.5)], distance, parent
    while queue._qsize()>0:
        prior,pos = queue._get()
        x,y=pos
        d = distance[x][y]
        if (checkPos(d, x,y, 1,0, 1) or checkPos(d, x,y, -1,0, 1) or checkPos(d, x,y, 0,1, 1) or checkPos(d, x,y, 0,-1, 1) or
            checkPos(d, x,y, 1,1, sq2) or checkPos(d, x,y, -1,1, sq2) or checkPos(d, x,y, 1,-1, sq2) or checkPos(d, x,y, -1,-1, sq2)):
            pathFounded = True
            if (finishWhenFoundPath):
                break
    result = []
    if pathFounded:
        x = xend
        y = yend
            
        while (parent[x][y]!=(x,y)):
            result.append(Vector2(x+0.5,y+0.5))
            x,y = parent[x][y]
        result.reverse()

    savePath('path',result, mapData)
    return result, distance, parent



def computeMap(mapData, selector):
    w = len(mapData)
    h = len(mapData[0]) 
    result = [[ selector(mapData[x][y], x,y) for y in range(h)] for x in range(w)]
    return result

def rotateVector2(v, angle):
    c = cos(-angle)
    s = sin(-angle)
    result = Vector2(v.x*c-v.y*s,v.x*s+v.y*c)
    return result

def transpose(m):
    w = len(m)
    h = len(m[0])
    result = [[ 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            result[y][x] = m[x][y]
    return result


def saveImage(name, data):
    pass
    #data = transpose(data)
    #arr = numpy.array(data, dtype='byte')
    #
    #img = PIL.Image.fromarray(arr, mode ='L')
    ##img.transpose(FLIP_LEFT_RIGHT)
    #img.save('D:\\tmp\\'+name+'.png') 
    ##img.show()

def saveImageVector(name, data):
    pass
    #s = 16;
    #w = len(data)
    #h = len(data[0])
    #img = PIL.Image.new(mode="L", size=(w*s, h*s), color = 255)
    #draw = ImageDraw.Draw(img)
    #for y in range(h):
    #    for x in range(w):
    #        if data[x][y]!=None:
    #            draw.line([(x*s,y*s),((x+data[x][y].x/2)*s,(y+data[x][y].y/2)*s) ], fill=0)
    #            draw.ellipse([(x*s-s/8,y*s-s/8),(x*s+s/8,y*s+s/8) ], fill=0)

    #img.save('D:\\tmp\\'+name+'.png') 

def savePath(name, path,data):
    pass
    #s = 16;
    #w = len(data)
    #h = len(data[0])
    #img = PIL.Image.new(mode="RGB", size=(w*s, h*s), color = 0xFFFFFF)
    #draw = ImageDraw.Draw(img)
    #
    #for y in range(h):
    #    for x in range(w):
    #        color = 0xFFFFFF-data[x][y] if data[x][y]>0 else 0
    #        draw.rectangle([(x*s,y*s),((x+1)*s,(y+1)*s)], fill = color)
    #i = 1
    #for p in path:
    #    if isinstance(p, tuple):
    #        p1 = p[0]
    #        if isinstance(p[1], list):
    #            p2 = p[1]
    #        else:
    #            p2 = [p[1]]
    #    else:
    #        p1 = p
    #        p2 = None

    #    draw.ellipse([(p1.x*s-s/4,p1.y*s-s/4),(p1.x*s+s/4,p1.y*s+s/4) ], fill=0x00FF00)
    #    draw.text((p1.x*s-s/8,p1.y*s-s/8), str(i), fill=0xFF0000)
    #    if p2!=None:
    #        for p3 in p2:
    #            draw.line([(p1.x*s,p1.y*s),(p3.x*s,p3.y*s)], fill=0x00FF00)
    #    i+=1
    #                
    #img.save('D:\\tmp\\'+name+'.png') 
    

def savePathWithText(name, path,data):
    pass
    #s = 16;
    #w = len(data)
    #h = len(data[0])
    #img = PIL.Image.new(mode="L", size=(w*s, h*s), color = 255)
    #draw = ImageDraw.Draw(img)
    #for p in path:
    #    #draw.ellipse([(p.x*s-s/8,p.y*s-s/8),(p.x*s+s/8,p.y*s+s/8) ], fill=0)
    #    draw.text((p[0].x*s-s/8,p[0].y*s-s/8), str(p[1]))

    #for y in range(h):
    #    for x in range(w):
    #        if data[x][y]>0:
    #            draw.rectangle([(x*s,y*s),((x+1)*s,(y+1)*s)], fill = 64)
    #img.save('D:\\tmp\\'+name+'.png') 
    
#if __name__ == '__main__':
#    image_array=[0]
#    
#    #scipy.misc.imsave('outfile.jpg', image_array)
#    
#    map = [[0, 0, 0, 0, 0], 
#           [0, 255, 255, 0, 0], 
#           [0, 0, 0, 0, 0], 
#           [0, 0, 0, 0, 0]]
#    
#    map2 = [0, 0, 0, 0, 0, 
#           0, 2, 2, 0, 0, 
#           0, 0, 0, 0, 0, 
#           0, 0, 0, 0, 0]
#    

#    an = MapAnalyzeVisibility(transpose(map))
#    
#    #arr = numpy.array(map, dtype="byte")
#    #img = PIL.Image.fromarray(arr, mode ="L")
#    #img.save('new_name.png') 
#    result = an.buildLOS()
#    r2 = [transpose(x) for x in result]

#    print r2

