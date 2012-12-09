

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
        self.debugInfo = ''
        #commander, bot = self.executionContext
        #commander.log.info("Context created") 

    def tick(self):
        #commander, bot = self.executionContext
        #commander.log.info("Context run") 
        self.debugInfo = ''
        self.root.execute(self, [], len(self.prevPath)>0)
        print self.debugInfo

        

class BTNode():
    """
    Base node for Behaviour Tree
    """
    STATUS_OK=1
    STATUS_FAIL=2
    STATUS_RUNNING=3

    def __init__(self, *childs):
        if isinstance(childs[0], str):
            self.name = childs[0]
            self.childs = childs[1:]        
        else:
            self.name = ''
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
        context.debugInfo+= self.name
        currentChild = 0
        if (isPathLikePrev):
            prevPathChild = context.prevPath[len(currentPath)]
            currentChild = prevPathChild
        else:
            prevPathChild = -1
        context.debugInfo+=' Seq['
        #commander, bot = context.executionContext
        #commander.log.info("Sequence run" + str(currentChild))  

        status = self.childs[currentChild].execute(context, currentPath+[currentChild], isPathLikePrev)
        context.debugInfo+=str(currentChild)+'/'

        while (status == BTNode.STATUS_OK):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context, currentPath+[currentChild], False)
                context.debugInfo+=str(currentChild)+'/'
            else:
                #currentChild = 0
                break

        #if (status == BTNode.STATUS_FAIL):
        #    currentChild=0

        #context.currentChild[self.id] = currentChild   
        context.debugInfo+=']'
             
        return status


class BTSelector(BTNode):
    """
     Sequence node for Behaviour Tree
    """
    def execute(self, context, currentPath, isPathLikePrev):
        #commander, bot = context.executionContext
        #commander.log.info("Selector run")  
        context.debugInfo+= self.name
        
        if (isPathLikePrev):
            prevPathChild = context.prevPath[len(currentPath)]
        else:
            prevPathChild = -1
        context.debugInfo+=' Selector('

        currentChild=0
        status = self.childs[currentChild].execute(context, currentPath+[currentChild], currentChild==prevPathChild)
        context.debugInfo+=str(currentChild)+'/'

        while (status == BTNode.STATUS_FAIL):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context, currentPath+[currentChild], currentChild==prevPathChild)
                context.debugInfo+=str(currentChild)+'/'

            else:
                #currentChild = 0
                break    
        context.debugInfo+=')'

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
        context.debugInfo+='Act'

        #for easier using, actions cannot be failed
        if (check or check==None):
            #assume only one action can be running at one time
            context.prevPath = currentPath
            if context.lastRunningNode != None:
                context.lastRunningNode.stop(context)
            context.lastRunningNode = self
            return BTNode.STATUS_RUNNING
        else:
            #context.prevPath = []
            return BTNode.STATUS_FAIL

class BTCondition(BTNode):
    """
    Check condition
    """
    def __init__(self, condition, guardedNode = None):
        self.condition = condition
        self.childs=[]
        self.guardedNode = guardedNode

    def execute(self, context, currentPath, isPathLikePrev):
        """
        Run node
        """
        #commander, bot = context.executionContext
        #commander.log.info("Condition run")    

        check = self.condition(*context.executionContext);
        context.debugInfo+='Cond:'+str(check)

        if (check):
            if (self.guardedNode == None):
                return BTNode.STATUS_OK
            else:
                return self.guardedNode.execute(context, currentPath, isPathLikePrev)
        else:
            return BTNode.STATUS_FAIL

