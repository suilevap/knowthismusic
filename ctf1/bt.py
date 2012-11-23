

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

    def getNewContext(self, executionContext):
        context = BTContext(executionContext, self.maxid)
        context.tree = self;

    def execute(self, context):
        if (context.tree == self):
            root.execute(context)

class BTContext:
    def __init__(self, executionContext, n):
        self.executionContext=executionContext
        self.currentChild=[0 for x in range(n)]
        

class BTNode():
    """
    Base node for Behaviour Tree
    """
    STATUS_OK=1
    STATUS_FAIL=2
    STATUS_RUNNING=3

    def __init__(self, childs):
        self.childs=childs        
        self.id=0

    def execute(self):
        """
        Run node
        """

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
                self.currentChild = 0
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
        check = action(context);
        #for easier using, actions cannot be failed
        if (check):
            return BTNode.STATUS_RUNNING
        else:
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
        check = condition(context);
        if (check):
            return BTNode.STATUS_OK
        else:
            return BTNode.STATUS_FAIL

