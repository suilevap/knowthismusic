from api.gameinfo import *
from api import Commander
from api import commands


from bt import *

class BTSampleCommander(Commander):
    """
    Commander simple assign and run bt tree for each bots
    """

    def initialize(self):
        """
        Assign BT tree to each member
        """
        self.verbose = True    # display the command descriptions next to the bot labels
        self.brains={}
        for bot in self.game.team.members: 
            self.brains[bot.name]= MainAi.getNewContext(self, bot)

    def tick(self):
        """Tick for all BTTree"""

        for bot in self.game.team.members: 
            self.brains[bot.name].tick()
            if self.verbose:
                print "%s : %s"%(bot.name, self.brains[bot.name].debugInfo)
        



class BTBotTask(BTAction):
    '''
    Primitive task for Bot
    '''

    def __init__(self, action):
        BTAction.__init__(self, action)

    def execute(self, context, currentPath, isPathLikePrev):

        commander, bot = context.executionContext

        if (context.prevPath == currentPath):
            if (bot.state != BotInfo.STATE_IDLE  ):
                state = BTNode.STATUS_RUNNING
            elif bot.state != BotInfo.STATE_HOLDING:
                state = BTNode.STATUS_FAIL
                context.prevPath = []
            else:
                state = BTNode.STATUS_OK
                context.prevPath = []
        else:
            state = BTAction.execute(self, context, currentPath, isPathLikePrev)

        return state


def Condition_ReadyToAttack(commander, bot):
    result = (bot.state==BotInfo.STATE_SHOOTING or bot.state==BotInfo.STATE_TAKINGORDERS
               or len([b for b in bot.visibleEnemies if b.health>0 and (b.position-bot.position).length()<commander.level.firingDistance ])>0)
    return result

TakeFlag = BTSequence('Take Flag',
    BTCondition(lambda commander,bot: bot.flag==None),
    BTBotTask(lambda commander,bot:commander.issue( commands.Charge, bot, commander.level.findRandomFreePositionInBox(commander.level.area), description = 'Charge to random point')),  
    #then
    BTBotTask(lambda commander,bot:commander.issue( commands.Attack, bot, commander.game.enemyTeam.flag.position, description = 'Attack enemy home')),  

)

ReturnFlag = BTSequence('Return Enemy flag',
    BTCondition(lambda commander,bot: bot.flag!=None),
    BTBotTask(lambda commander,bot:commander.issue( commands.Charge, bot, commander.level.findRandomFreePositionInBox(commander.level.area), description = 'Charge to random point')),  
    #then
    BTBotTask(lambda commander,bot:commander.issue( commands.Charge, bot, commander.game.team.flagScoreLocation, description = 'Running home'))   
)

AttackEnemy = BTSequence('Attack enemy',
    BTCondition(lambda commander,bot: len(bot.visibleEnemies)!=0), #simple sequnce condition, check only once, when  sequence started
    BTParallelCondition(lambda commander,bot: len(bot.visibleEnemies)!=0 and list(bot.visibleEnemies)[0].health >0, # ParallelCondition, check every tick while nested nodes are runnig, if false, nested noes return FAIL
        BTSelector('Choose style',
            BTSequence('Atacck is not safe',
                BTCondition(lambda commander,bot: bot.seenBy!=0),
                BTBotTask(lambda commander,bot:commander.issue( commands.Attack, bot, list(bot.visibleEnemies)[0].position, description = 'Attack visible enemy'))   
            ),
            #or
            BTSequence('Atacck is safe',
                BTBotTask(lambda commander,bot:commander.issue( commands.Charge, bot, list(bot.visibleEnemies)[0].position, description = 'Charge visible enemy'))   
            )
        )
    )
)

MainAi = BTTree(
    BTSelector('Main Ai',
        BTCondition(Condition_ReadyToAttack),#to avoid interruption and delay when better use default behaviour
        ReturnFlag,
        #or
        AttackEnemy,
        #or
        TakeFlag
    ),
)



