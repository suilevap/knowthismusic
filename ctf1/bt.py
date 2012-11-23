

class BTTree():
    def __init__(self, root):
        self.maxId = _build(root)
        self.root = root


    def _build(self, root):
        maxid = genId(root, 0)
        def genId(node, id):
            id += 1
            node.id = id;        
            for child in node.childs:
                id = genId(child, id)
            return id;

    def getNewContext(self, *executionContext):
        context = BTContext(self.root, self.maxid, *executionContext)
        context.tree = self;

    #def execute(self, context):
    #    if (context.tree == self):
    #        root.execute(context)

class BTContext:
    def __init__(self, root, n, *executionContext):
        self.root = root
        self.executionContext=executionContext
        self.currentChild=[0 for x in range(n)]
        self.currentRunningNodeId=-1


    def RunTree(self):
        root.execute(self)
        

class BTNode():
    """
    Base node for Behaviour Tree
    """
    STATUS_OK=1
    STATUS_FAIL=2
    STATUS_RUNNING=3

    def __init__(self, *childs):
        self.childs=childs        
        self.id=0

    def execute(self):
        """
        Run node
        """
        pass

class BTSequence(BTNode):
    """
     Sequence node for Behaviour Tree
    """

    def execute(self, context):
        currentChild = context.currentChild[self.id]

        status = self.childs[currentChild].execute(context)
        while (status == BTNode.STATUS_OK):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context)
            else:
                currentChild = 0
                break

        if (status == BTNode.STATUS_FAIL):
            currentChild=0

        context.currentChild[self.id] = currentChild        
        return status


class BTSelector(BTNode):
    """
     Sequence node for Behaviour Tree
    """
    def execute(self, context):
        currentChild=0
        status = self.childs[currentChild].execute(context)
        while (status == BTNode.STATUS_FAIL):            
            currentChild+=1
            if currentChild<len(self.childs):
                status = self.childs[currentChild].execute(context)
            else:
                currentChild = 0
                break
        context.currentChild[self.id] = currentChild        
        return status

class BTAction(BTNode):
    """
    Atomic action
    """
    def __init__(self, action):
        self.action = action  
        self.childs=[]      

    def execute(self, context):
        """
        Run node
        """
        
        check = action(*context.executionContext);
        #for easier using, actions cannot be failed
        if (check):
            #assume only one action can be running at one time
            context.currentRunningNodeId = self.id
            return BTNode.STATUS_RUNNING
        else:
            context.currentRunningNodeId = -1
            return BTNode.STATUS_OK

class BTCondition(BTNode):
    """
    Check condition
    """
    def __init__(self, condition):
        self.condition = condition
        self.childs=[]

    def execute(self, context):
        """
        Run node
        """
        check = condition(*context.executionContext);
        if (check):
            return BTNode.STATUS_OK
        else:
            return BTNode.STATUS_FAIL

