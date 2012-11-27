from math import sqrt
import PIL
import numpy
from PIL import Image

class MapAnalyzeVisibility(object):
    """description of class"""

    def __init__(self, map):
        self.map = map
        self.w = len(self.map)
        self.h = len(self.map[0])

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
            saveImage('min_'+str(dx1)+str(dy1)+str(dx2)+str(dy2), [ [(result[x][y][0]+1) for y in range(self.h)] for x in range(self.w)])
            saveImage('max_'+str(dx1)+str(dy1)+str(dx2)+str(dy2), [ [(result[x][y][1]+1) for y in range(self.h)] for x in range(self.w)])

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
#    #arr = numpy.array(map, dtype="byte")
#    #img = PIL.Image.fromarray(arr, mode ="L")
#    #img.save('new_name.png') 
#    result = an.buildLOS()
#    r2 = [transpose(x) for x in result]

#    print r2
