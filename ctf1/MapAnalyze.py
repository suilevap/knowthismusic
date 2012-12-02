from math import sqrt
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

        self.dangerMap =[ [(0) for y in range(self.h)] for x in range(self.w)]


    def getAllVisiblePoints(self, pos ,r ):
        result = []
        x0 = int(pos.x)
        y0 = int(pos.y)

        minX, minY = self.clamp(int(pos.x-r), 0, self.w-1), self.clamp(int(pos.y-r), 0, self.h-1)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w-1), self.clamp(int(pos.y+r), 0, self.h-1) 
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                delta = Vector2(x,y)-pos
                sector = self.getSectorIndex(delta)
                r0Min = self.visibleSectors[sector][x0][y0][0]
                r1Min = self.visibleSectors[(sector+4)%8][x][y][0]
                d = max(abs(x0-x),abs(y0-y))
                if (r0Min>= d or r1Min>=d ):#or (r1Max<d and r2Max<d)):
                    result.append((x,y))
        return result

    
     
    def updateDanger(self, pos, dir):
        sector = self.getSectorIndex(dir)
        x0 = int(pos.x)
        y0 = int(pos.y)

        r0Min = self.visibleSectors[sector][x0][y0][0]
        r0Max = self.visibleSectors[sector][x0][y0][1]
        r = r0Max
        minX, minY = self.clamp(int(pos.x-r), 0, self.w-1), self.clamp(int(pos.y-r), 0, self.h-1)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w-1), self.clamp(int(pos.y+r), 0, self.h-1) 
        for x in range(minX, maxX):
            for y in range(minY, maxY): 
                delta = Vector2(x,y)-pos
                sector2 = self.getSectorIndex(delta)
                r2Min = self.visibleSectors[(sector2+4)%8][x][y][0]
                d = max(abs(x0-x),abs(y0-y))

                if (sector==sector2):
                    if (r0Min>= d or r2Min>=d ):#or (r1Max<d and r2Max<d)):
                        self.dangerMap[x][y]+=8

                #r1Min = self.visibleSectors[sector2][x0][y0][0]
                #r1Max = self.visibleSectors[sector2][x0][y0][1]

                #r2Min = self.visibleSectors[(sector2+4)%8][x][y][0]
                #r2Max = self.visibleSectors[(sector2+4)%8][x][y][1]

                #if (r1Min>= d or r2Min>=d ):#or (r1Max<d and r2Max<d)):
                #    self.dangerMap[x][y]+=8
        

    def updateDangerStep(self, bots):
        for y in range(0, self.h):
            for x in range(0, self.w):
                if self.dangerMap[x][y]>0:
                    self.dangerMap[x][y]=1
                if self.map[x][y]>0:
                    self.dangerMap[x][y]=-1
        for bot in bots:
            self.updateDanger(bot.position, bot.facingDirection)

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
            if (mapData[x1][y1]==0) and (parent[x1][y1]==None or distance[x1][y1]>d+delta):
                parent[x1][y1] = (x,y)
                distance[x1][y1] = d + delta
                queue._put((d+delta+heuristic(x,y,x1,y1), (x1,y1)))

                if ((x1==xend) and (y1==yend)):
                    result = True
            return result

        pathFounded = False
        if checkPos(0, xstart,ystart, 0,0, 0):
            return [Vector(x,y)]
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
                result.append(Vector2(x,y))
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

    def getBreakingMap(self, path, r):
       
        ranks =[ [(0) for y in range(self.h)] for x in range(self.w)]
        rank = 1.0
        for p in path:
            points = self.getAllVisiblePoints(p, r)
            for visiblePoint in points:
                x,y = visiblePoint
                if (self.distanceField[x][y] > 0):
                    ranks[x][y] += rank/self.distanceField[x][y]
            rank += 3/len(path)

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

    def getBestBreakingPoints(self, start, end, r, n):
        tmpMap =[ [self.map[x][y] for y in range(self.h)] for x in range(self.w)]
        result = []
        for i in range(n):
            path = self.getPath(start, end, tmpMap)
            if len(path)<1:
                break
            breakingMap = self.getBreakingMap(path, r)
            x,y = self.getTheBestPos(breakingMap)
            bestPoint = Vector2(x,y)
            result.append(bestPoint)
            visiblePoints = self.getAllVisiblePoints(bestPoint, r)
            for x,y in visiblePoints:
                tmpMap[x][y] = 2
        savePath("allBreakingPoints", result, self.map)
        return result

    def getBestDirection(self, pos):
        x = int(pos.x)
        y = int(pos.y)
        return self.directions[self.bestDirectionsMap[x][y]]

    def getAllDirections(self, pos, dmin):
        x = int(pos.x)
        y = int(pos.y)
        return [self.directions[i] for i in range(0,8) if self.visibleSectors[i][x][y][0]>=dmin]

    def getBestPosition(self, pos, r):
        minX, minY = self.clamp(int(pos.x-r), 0, self.w-1), self.clamp(int(pos.y-r), 0, self.h-1)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w-1), self.clamp(int(pos.y+r), 0, self.h-1)    
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
        minX, minY = self.clamp(int(pos.x-r), 0, self.w-1), self.clamp(int(pos.y-r), 0, self.h-1)
        maxX, maxY = self.clamp(int(pos.x+r), 0, self.w-1), self.clamp(int(pos.y+r), 0, self.h-1)    
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

            result =[ [(0,0) for y in range(self.h)] for x in range(self.w)]
            for y in rangeY:
                for x in rangeX:
                    if (self.map[x][y] <= 1):
                        result[x][y] = (min([result[x + dx1][y + dy1][0]+1,result[x + dx2][y + dy2][0]+1]),
                                        max([result[x + dx1][y + dy1][1]+1,result[x + dx2][y + dy2][1]+1]))
                    else:
                        result[x][y] = (-1,-1)
            return result
       
        finalResult =[
                buildLosDir(range(self.w-1-1, -1, -1), range(1,self.h), 1, 0, 1, -1),
                buildLosDir(range(0,self.w-1), range(1,self.h), 0, -1, 1, -1),
                buildLosDir(range(1,self.w), range(1,self.h), 0, -1, -1, -1),
                buildLosDir(range(1,self.w), range(1,self.h), -1, 0, -1, -1),

                buildLosDir(range(1,self.w), range(self.h-1-1,-1,-1), -1, 0, -1, 1),
                buildLosDir(range(1,self.w), range(self.h-1-1,-1,-1), 0, 1, -1, 1),
                buildLosDir(range(0,self.w-1), range(self.h-1-1,-1,-1), 0, 1, 1, 1),
                buildLosDir(range(self.w-1-1, -1, -1), range(self.h-1-1,-1,-1), 1, 0, 1, 1)]


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
    img = PIL.Image.new(mode="L", size=(w*s, h*s), color = 255)
    draw = ImageDraw.Draw(img)
    for p in path:
        draw.ellipse([(p.x*s-s/8,p.y*s-s/8),(p.x*s+s/8,p.y*s+s/8) ], fill=0)

    for y in range(h):
        for x in range(w):
            if data[x][y]>0:
                draw.rectangle([(x*s-s/2,y*s-s/2),((x+1)*s-s/2,(y+1)*s-s/2)], fill = 64)
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
                draw.rectangle([(x*s-s/2,y*s-s/2),((x+1)*s-s/2,(y+1)*s-s/2)], fill = 64)
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
