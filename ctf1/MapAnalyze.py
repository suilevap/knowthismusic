from math import sqrt, cos, sin
import PIL
import numpy
from PIL import Image, ImageDraw
from api.vector2 import Vector2
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
      

        self.directions =[Vector2(1,0), Vector2(1,-1).normalized(), Vector2(0,-1), Vector2(-1,-1).normalized(), 
                          Vector2(-1,0), Vector2(-1,1).normalized(), Vector2(0,1), Vector2(1,1).normalized()]
        angle = math.pi/8
        self.directions=[rotateVector2(x,angle) for x in self.directions]

        self.dangerMap =[ [(0) for y in range(self.h)] for x in range(self.w)]


    def getAllVisiblePoints(self, pos ,r, targetSector = -1, sectorsCount=0, useMax = False ):
        result = []
        x0 = int(pos.x)
        y0 = int(pos.y)

        minX, minY = self.clamp(int(pos.x-r), 0, self.w), self.clamp(int(pos.y-r), 0, self.h)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w), self.clamp(int(pos.y+r), 0, self.h) 
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                delta = Vector2(x,y)-pos
                sector = self.getSectorIndex(delta)
                if targetSector==-1 or self.getSectorDiff(targetSector,sector)<=sectorsCount:
                    r0Min, r0Max = self.visibleSectors[sector][x0][y0]
                    r1Min, r1Max = self.visibleSectors[(sector+4)%8][x][y]

                    d = max(abs(x0-x),abs(y0-y))
                    if (r0Min>= d or r1Min>=d )or (useMax and (r0Min + r0Max)/2>=d and (r1Min + r1Max)/2>=d):
                        result.append((x,y))
        return result

    
     
    def updateDanger(self, pos, dir, r):
        sector = self.getSectorIndex(dir)
        x0 = int(pos.x)
        y0 = int(pos.y)

        points = self.getAllVisiblePoints(pos, r, sector, 1, True)
        for visiblePoint in points:
            x,y = visiblePoint
            self.dangerMap[x][y] += 196

        

    def updateDangerStep(self, bots, r):
        for y in range(0, self.h):
            for x in range(0, self.w):
                if self.map[x][y]>0:
                    self.dangerMap[x][y]=-1
                else:
                    self.dangerMap[x][y]=1
        for bot in bots:
            self.updateDanger(bot.position, bot.facingDirection, r)
        saveImage("DangerMap", self.dangerMap) 


    def getPathThroughDanger(self, start, end):
        return self.getPath(start, end, self.dangerMap)

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
    
    def getPath(self, start, end, mapData):
        sq2 = math.sqrt(2)
        distance =[ [(0) for y in range(self.h)] for x in range(self.w)]
        parent =[ [None for y in range(self.h)] for x in range(self.w)]
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
            if (x1<0  or x1>=self.w or y1<0 or y1>=self.h):
                return False
            fullDistance = d+delta*(mapData[x][y])
            if (mapData[x1][y1]!=-1) and (parent[x1][y1]==None or distance[x1][y1]>fullDistance):
                parent[x1][y1] = (x,y)
                distance[x1][y1] = fullDistance
                queue._put((fullDistance+heuristic(x,y,x1,y1), (x1,y1)))

                if ((x1==xend) and (y1==yend)):
                    result = True
            return result

        pathFounded = False
        if checkPos(0, xstart,ystart, 0,0, 0):
            return [Vector2(x,y)]
        while queue._qsize()>0:
            prior,pos = queue._get()
            x,y=pos
            d = distance[x][y]
            if (checkPos(d, x,y, 1,0, 1) or checkPos(d, x,y, -1,0, 1) or checkPos(d, x,y, 0,1, 1) or checkPos(d, x,y, 0,-1, 1) or
                checkPos(d, x,y, 1,1, sq2) or checkPos(d, x,y, -1,1, sq2) or checkPos(d, x,y, 1,-1, sq2) or checkPos(d, x,y, -1,-1, sq2)):
                pathFounded = True
                break
        result = []
        if pathFounded:
            x = xend
            y = yend
            
            while (parent[x][y]!=(x,y)):
                result.append(Vector2(x+0.5,y+0.5))
                x,y = parent[x][y]
            result.reverse()

        savePathWithText('path',[(p, int(self.averageMin[int(p.x)][int(p.y)]))for p in result], self.map)
        return result

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

    def getBreakingMap(self, paths, r, ignorePoints = None):
       
        ranks =[ [(0) for y in range(self.h)] for x in range(self.w)]
        rank = 1.0
        for path in paths:
            i = 0;
            for p in path:
                x,y=int(p.x), int(p.y)
                part = i*1.0/len(path)
                rank = 1.0-abs(1.0-part)
                prevPoint = path[i-1]
                i+=1

                if ignorePoints!=None and (x,y) in ignorePoints:
                    continue
                
                points = self.getAllVisiblePoints(p, r, self.getSectorIndex(p-prevPoint), 1)
                for visiblePoint in points:
                    x,y = visiblePoint
                    if (self.distanceField[x][y] > 0):
                        ranks[x][y] += rank/self.distanceField[x][y]


            #rank += 1.0/len(path)

        #for x in range(0,self.w):
        #    for y in range(0,self.h):
        #        if (ranks[x][y]>self.distanceField[x][y]):
        #            ranks[x][y] -= self.distanceField[x][y]
        #        else:
        #            ranks[x][y] = 0
        saveImage("breaking", ranks) 
        return ranks

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
   
    def getBestBreakingPoints(self, start, end, rPrefered, rControl, n):
        pathMaxLength = 50
        tmpMap = self.createMapForPathFinding()
        result = []
        allpaths = []
        for i in range(n):
            path = self.getPath(start, end, tmpMap)
            savePath("path_iteration"+str(i), path, tmpMap)
            if len(path)<1:
                break

            allpaths.append(path[-pathMaxLength:])

            breakingMap = self.getBreakingMap([path], rPrefered)
            x,y = self.getTheBestPos(breakingMap)
            bestPoint = Vector2(x+0.5,y+0.5)

            pathMap = [ [tmpMap[x][y]  for y in range(self.h)] for x in range(self.w)]
            
            for p in path:
                if self.checkVisibility(bestPoint, p):
                    bestPair = (bestPoint,[p], path, pathMap, i)
                    break
            result.append(bestPair)
            sector = self.getSectorIndex(bestPair[1][0]-bestPair[0])

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

        return result

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
        x = int(pos.x)
        y = int(pos.y)
        return [self.directions[i] for i in range(0,8)
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

    def debug(self):
        i=0
        for d in self.visibleSectors:
            saveImage('min_'+str(i), [ [(d[x][y][0])for x in range(self.w)] for y in range(self.h)] )
            saveImage('max_'+str(i), [ [(d[x][y][1])for x in range(self.w)] for y in range(self.h)] )
            i+=1
        saveImage('all_min', self.averageMin )

        saveImage('all_max', [ [(self.visibleSectors[0][x][y][1]
                                     +self.visibleSectors[1][x][y][1]
                                     +self.visibleSectors[2][x][y][1]
                                     +self.visibleSectors[3][x][y][1]
                                     +self.visibleSectors[4][x][y][1]
                                     +self.visibleSectors[5][x][y][1]
                                     +self.visibleSectors[6][x][y][1]
                                     +self.visibleSectors[7][x][y][1]
                                     +7)/8 for x in range(self.w)] for y in range(self.h)] )

        tmpbestDirectionsMap =[ [self.directions[self.bestDirectionsMap[x][y]] if self.map[x][y]==0 else None 
                                for y in range(self.h)] for x in range(self.w) ]
        saveImageVector('Dir', tmpbestDirectionsMap)


    def clamp(self, x, minValue, maxValue):
        return max(minValue, min(x, maxValue))


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
    data = transpose(data)
    arr = numpy.array(data, dtype='byte')
    
    img = PIL.Image.fromarray(arr, mode ='L')
    #img.transpose(FLIP_LEFT_RIGHT)
    img.save('D:\\tmp\\'+name+'.png') 
    #img.show()

def saveImageVector(name, data):
    s = 16;
    w = len(data)
    h = len(data[0])
    img = PIL.Image.new(mode="L", size=(w*s, h*s), color = 255)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            if data[x][y]!=None:
                draw.line([(x*s,y*s),((x+data[x][y].x/2)*s,(y+data[x][y].y/2)*s) ], fill=0)
                draw.ellipse([(x*s-s/8,y*s-s/8),(x*s+s/8,y*s+s/8) ], fill=0)

    img.save('D:\\tmp\\'+name+'.png') 

def savePath(name, path,data):
    s = 16;
    w = len(data)
    h = len(data[0])
    img = PIL.Image.new(mode="RGB", size=(w*s, h*s), color = 0xFFFFFF)
    draw = ImageDraw.Draw(img)
    
    for y in range(h):
        for x in range(w):
            color = 0xFFFFFF-data[x][y] if data[x][y]>0 else 0
            draw.rectangle([(x*s,y*s),((x+1)*s,(y+1)*s)], fill = color)
    i = 1
    for p in path:
        if isinstance(p, tuple):
            p1 = p[0]
            if isinstance(p[1], list):
                p2 = p[1]
            else:
                p2 = [p[1]]
        else:
            p1 = p
            p2 = None

        draw.ellipse([(p1.x*s-s/4,p1.y*s-s/4),(p1.x*s+s/4,p1.y*s+s/4) ], fill=0x00FF00)
        draw.text((p1.x*s-s/8,p1.y*s-s/8), str(i), fill=0xFF0000)
        if p2!=None:
            for p3 in p2:
                draw.line([(p1.x*s,p1.y*s),(p3.x*s,p3.y*s)], fill=0x00FF00)
        i+=1
                    
    img.save('D:\\tmp\\'+name+'.png') 
    

def savePathWithText(name, path,data):
    s = 16;
    w = len(data)
    h = len(data[0])
    img = PIL.Image.new(mode="L", size=(w*s, h*s), color = 255)
    draw = ImageDraw.Draw(img)
    for p in path:
        #draw.ellipse([(p.x*s-s/8,p.y*s-s/8),(p.x*s+s/8,p.y*s+s/8) ], fill=0)
        draw.text((p[0].x*s-s/8,p[0].y*s-s/8), str(p[1]))

    for y in range(h):
        for x in range(w):
            if data[x][y]>0:
                draw.rectangle([(x*s,y*s),((x+1)*s,(y+1)*s)], fill = 64)
    img.save('D:\\tmp\\'+name+'.png') 
    
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
