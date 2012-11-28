

class BTTree():
    def __init__(self, root):
        self.root = root


    def getNewContext(self, *executionContext):
        context = BTContext(self.root, *executionContext)
        context.tree = self;
        return context

class BTContext:
    def __init__(self, root, *executionContext):
        self.root = root
        self.executionContext=executionContext
        #self.currentChild=[0 for x in range(n)]
        self.prevPath = []
        self.currentIdPath = []
        self.lastRunningNode=None
        #commander, bot = self.executionContext
        #commander.log.info("Context created") 

    def tick(self):
        #commander, bot = self.executionContext
        #commander.log.info("Context run") 
        self.root.execute(self, [], len(self.prevPath)>0)
        

class BTNode():
    """
    Base node for Behaviour Tree
    """
    STATUS_OK=1
    STATUS_FAIL=2
    STATUS_RUNNING=3

    def __init__(self, *childs):
        self.childs=childs        
        

    def execute(self, context, currentPath, isPathLikePrev):
        """
        Run node
        """
        pass

    def stop(self, context):
        pass

class BTSequence(BTNode):
    """
     Sequence node for Behaviour Tree
    """

    def execute(self, context, currentPath, isPathLikePrev):

        currentChild = 0
        if (isPathLikePrev):
            prevPathChild = context.prevPath[len(currentPath)]
            currentChild = prevPathChild
        else:
            prevPathChild = -1

        #commander, bot = context.executionContext
        #commander.log.info("Sequence run" + str(currentChild))  

        status = self.childs[currentChild].execute(context, currentPath+[currentChild], isPathLikePrev)
        while (status == BTNode.STATUS_OK):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context, currentPath+[currentChild], False)
            else:
                #currentChild = 0
                break

        #if (status == BTNode.STATUS_FAIL):
        #    currentChild=0

        #context.currentChild[self.id] = currentChild   
             
        return status


class BTSelector(BTNode):
    """
     Sequence node for Behaviour Tree
    """
    def execute(self, context, currentPath, isPathLikePrev):
        #commander, bot = context.executionContext
        #commander.log.info("Selector run")  
        if (isPathLikePrev):
            prevPathChild = context.prevPath[len(currentPath)]
        else:
            prevPathChild = -1

        currentChild=0
        status = self.childs[currentChild].execute(context, currentPath+[currentChild], currentChild==prevPathChild)
        while (status == BTNode.STATUS_FAIL):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context, currentPath+[currentChild], currentChild==prevPathChild)
            else:
                #currentChild = 0
                break    
        return status

class BTAction(BTNode):
    """
    Atomic action
    """
    def __init__(self, action ):
        self.action = action  
        self.childs=[]      

    def execute(self, context, currentPath, isPathLikePrev):
        """
        Run node
        """    
        #commander, bot = context.executionContext
        #commander.log.info("Action run")    
        
  
        check = self.action(*context.executionContext);
        #for easier using, actions cannot be failed
        if (check or check==None):
            #assume only one action can be running at one time
            context.prevPath = currentPath
            if context.lastRunningNode != None:
                context.lastRunningNode.stop(context)
            context.lastRunningNode = self
            return BTNode.STATUS_RUNNING
        else:
            context.prevPath = []
            return BTNode.STATUS_OK

class BTCondition(BTNode):
    """
    Check condition
    """
    def __init__(self, condition):
        self.condition = condition
        self.childs=[]

    def execute(self, context, currentPath, isPathLikePrev):
        """
        Run node
        """
        #commander, bot = context.executionContext
        #commander.log.info("Condition run")    

        check = self.condition(*context.executionContext);
        if (check):
            return BTNode.STATUS_OK
        else:
            return BTNode.STATUS_FAIL

