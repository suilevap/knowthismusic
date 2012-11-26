from math import sqrt
class MapAnalyze(object):
    """description of class"""

    def __init__(self, map):
        self.map = map
        self.w = len(self.map)
        self.h = len(self.map[0])
    
    def buildLOS(self):
        
        sq2 = sqrt(2)
        result =[ [0 for y in range(self.h)] for x in range(self.w)]
        for y in range(1,self.h-1):
            for x in range(1,self.w-1):
                if (self.map[x][y] <= 1):
                    result[x][y] = max([result[x][y-1]+1,result[x-1][y-1]+sq2])
                else:
                    result[x][y] = 0

        return result



def transpose(m):
    w = len(m)
    h = len(m[0])
    result = [[ 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            result[y][x] = m[x][y]
    return result

if __name__ == '__main__':
    map = [[0, 0, 0, 0, 0], 
           [0, 2, 2, 0, 0], 
           [0, 0, 0, 0, 0], 
           [0, 0, 0, 0, 0]]
    
    an = MapAnalyze(transpose(map))
    result = transpose(an.buildLOS())
    print result
