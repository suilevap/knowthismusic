class Role(object):
    """Bot role"""
    def __init__(self,btTree, suitabilityFunction):
        self.btTree=btTree
        self.suitabilityFunction=suitabilityFunction
    
    def botsSuitability(self, bots):
        return sorted(bots, key =self.suitabilityFunction, reverse = True)
    
    def dequeOrder(self):
        return (None, -1)

    def enqueOrder(self, action, priority):
        pass
