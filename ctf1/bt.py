
import random

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
        self.clear()

    def tick(self):
        self.debugInfo = ''
        self.root.execute(self, [], len(self.prevPath)>0)
        #print self.debugInfo
    
    def clear(self):
        self.prevPath = []
        self.currentIdPath = []
        self.lastRunningNode=None
        self.debugInfo = ''
        self.choices = []

    def addChoice(self, node, childIndex):
        #print 'choice', childIndex
        self.choices.append((node, childIndex))
    
    def applyLearning(self, delta):
        importantChoices = self.choices[-2:]
        for node, childIndex in importantChoices:
            node.score[childIndex]+=delta
        #self.choices = []
        #print 'Apply learning',  delta

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

        context.debugInfo+=']'
             
        return status


class BTSelector(BTNode):
    """
     Sequence node for Behaviour Tree
    """
    def execute(self, context, currentPath, isPathLikePrev):

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
        check = self.condition(*context.executionContext);
        context.debugInfo+='Cond:'+str(check)

        if (check):
            if (self.guardedNode == None):
                return BTNode.STATUS_OK
            else:
                return self.guardedNode.execute(context, currentPath, isPathLikePrev)
        else:
            return BTNode.STATUS_FAIL


class BTParallelCondition(BTNode):
    """
    Check condition in parallel with some node
    """
    def __init__(self, condition, guardedNode):
        self.condition = condition
        self.childs=[]
        self.guardedNode = guardedNode

    def execute(self, context, currentPath, isPathLikePrev):
        """
        Run node
        """
        check = self.condition(*context.executionContext);
        context.debugInfo+='ParallelCond:'+str(check)

        if (check):
            return self.guardedNode.execute(context, currentPath, isPathLikePrev)
        else:
            return BTNode.STATUS_FAIL

class BTLearningChoice(BTNode):
    """
     Learning choice node for Behaviour Tree
    """
    def __init__(self, *childs):
        
        if isinstance(childs[0], str):
            self.name = childs[0]
            childs = childs[1:]        
        else:
            self.name = ''
            #childs=childs        
        self.score = [s for s,_ in childs]
        self.childs = [node for _,node in childs]
        #return super(BTLearningChoice, self).__init__(*childs)
        

    def execute(self, context, currentPath, isPathLikePrev):

        context.debugInfo+= self.name
        currentChild = -1
        if (isPathLikePrev):
            prevPathChild = context.prevPath[len(currentPath)]
            currentChild = prevPathChild
        else:
            prevPathChild = -1
        context.debugInfo+=' LearningChoice('
        
        newChoice = False
        if currentChild == -1:
            newChoice = True
            currentChild = max(range(len(self.childs)), key = lambda index: self.score[index]*(0.5+random.random()*0.5))

        status = self.childs[currentChild].execute(context, currentPath+[currentChild], isPathLikePrev)
        if newChoice and status == BTNode.STATUS_RUNNING:
            context.addChoice(self, currentChild)
        context.debugInfo+=str(currentChild)+'/'


        context.debugInfo+=')'
        #print 'Choice', self.score
        return status
