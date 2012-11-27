from math import sqrt
import PIL
import numpy
from PIL import Image, ImageDraw
from api.vector2 import Vector2

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
                                     +7)/8 for y in range(self.h)] for x in range(self.w)] 
      

        self.directions =[Vector2(1,0), Vector2(1,-1).normalized(), Vector2(0,-1), Vector2(-1,-1).normalized(), 
                          Vector2(-1,0), Vector2(-1,1).normalized(), Vector2(0,1), Vector2(1,1).normalized()]
 


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
    

    def getBestDirection(self, pos):
        x = int(pos.x)
        y = int(pos.y)
        return self.directions[self.bestDirectionsMap[x][y]]

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
    arr = numpy.array(data, dtype='byte')
    img = PIL.Image.fromarray(arr, mode ='L')
    img.save('D:\\tmp\\'+name+'.png') 

def saveImageVector(name, data):
    s = 32;
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
