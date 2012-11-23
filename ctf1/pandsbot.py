# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.


# The commander can send 'Commands' to individual bots.  These are listed and
# documented in commands.py from the ./api/ folder also.


from api import Commander
from api import commands
from api.vector2 import Vector2
from api.gameinfo import *
from bt import *

#from commander import *
#from commands import *
#from ctf1.gameinfo import BotInfo
#from ctf1 import commands
#from ctf1.vector2 import Vector2
#from ctf1.bt import *

from collections import deque



class PandSBot(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """

    ROLE_NONE   =  0
    ROLE_DEFENDER =  1
    ROLE_ATTACKER =  2

    def initialize(self):
        """Use this function to setup your bot before the game starts."""
        self.verbose = True    # display the command descriptions next to the bot labels
        for bot in self.game.team.members:            
            bot.role=PandSBot.ROLE_NONE
            bot.commandQueue = deque()
            bot.brain = None
        self.defenderPart = 0.25
        self.countBot = len(self.game.bots)
        

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""

        #self.log.info("Commander tick") 

        for bot in self.game.bots_alive:
        # define defenders
            if bot.role==PandSBot.ROLE_NONE:
                if (len(self.botsInRole(PandSBot.ROLE_DEFENDER))<=self.defenderPart*self.countBot):
                    bot.role=PandSBot.ROLE_DEFENDER
                    bot.brain = DefenderBTTree.getNewContext(self, bot)
                else:
                    bot.role=PandSBot.ROLE_ATTACKER
                    bot.brain = AttackerBTTree.getNewContext(self, bot)

        for bot in self.game.bots_alive:
            if (bot.brain != None):
                bot.brain.tick()
            self.updateBotCommandQueue(bot)
        
        #defenders = self.botsInRole(PandSBot.ROLE_DEFENDER)
        #for bot in defenders:
        #    if len(bot.visibleEnemies)>0 and bot.state!=BotInfo.STATE_SHOOTING:
        #        self.clearCommands(bot)
        #        #self.enqueCommand(bot,lambda s,b:Command_DefendDirection(s, b, b.position)) 
        #        self.issue(commands.Defend, bot, bot.visibleEnemies[0].position-bot.position, description='AAA')
        #    elif self.botFree(bot):
        #        #self.issue(commands.Move, bot, self.freePos(pos), description = 'Go to my flag (DEFENDER)')
        #        #self.issue(commands.Defend, bot, self.game.enemyTeam.flag.position-bot.position , description = 'Defend my flag (DEFENDER)')
        #        self.clearCommands(bot)
        #        self.enqueCommand(bot,Command_MoveToMyFlag) 
        #        self.enqueCommand(bot,Command_DefendMyFlag) 

        #                
        #attackers = self.botsInRole(PandSBot.ROLE_ATTACKER)
        #for bot in attackers:
        #    if not bot.flag and len(bot.visibleEnemies)>0 and bot.state!=BotInfo.STATE_SHOOTING:
        #        self.clearCommands(bot)
        #        #self.enqueCommand(bot,lambda s,b:Command_AttackBot(s,b, b)) 
        #        self.issue(commands.Attack, bot, bot.visibleEnemies[0].position, description='BB')
        #      
        #    elif self.botFree(bot):
        #        if bot.flag:
        #            # Tell the flag carrier to run home!
        #            target = self.game.team.flagScoreLocation
        #            self.clearCommands(bot)
        #            self.enqueCommand(bot, Command_RunHome)
        #        else:
        #            pos = self.game.enemyTeam.flag.position 
        #            #self.issue(commands.Move, bot, self.freePos((self.game.team.flag.position+pos)/2), description = 'Run to enemy flag (ATTACKER)')
        #            self.clearCommands(bot)
        #            self.enqueCommand(bot, Command_RunToMidPoint)
        #            self.enqueCommand(bot, Command_AttackEnemyFlag)  

        ## for all bots which aren't currently doing anything
        #for bot in self.game.bots_available:

        #

        #    if bot.flag:
        #        # if a bot has the flag run to the scoring location
        #        flagScoreLocation = self.game.team.flagScoreLocation
        #        self.issue(commands.Charge, bot, flagScoreLocation, description = 'Run to my flag')
        #    else:
        #        # otherwise run to where the flag is
        #        enemyFlag = self.game.enemyTeam.flag.position
        #        self.issue(commands.Charge, bot, enemyFlag, description = 'Run to enemy flag')

    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass



    def getBotNearestToPoint(self,position):
        return min(self.game.bots_alive, key=lambda bot: (bot.position-position).length())

    def botsInRole(self, role):
        return [bot for bot in self.game.bots_alive if bot.role==role]

    def clearCommands(self, bot):
        bot.commandQueue.clear();

    def botFree(self, bot):
        return bot.state == BotInfo.STATE_IDLE and len(bot.commandQueue)==0;

    #def enqueCommand(self, CommandClass, bot, *args, **dct):
    #    bot.commandQueue.append(CommandClass(bot.name, *args, **dct))
    def enqueCommand(self, bot, action):
        bot.commandQueue.append(action)

    def updateBotCommandQueue(self, bot):
        if bot.state == BotInfo.STATE_IDLE and len(bot.commandQueue)>0:
            nextOrder = bot.commandQueue.popleft()
            nextOrder(self, bot)
            #self.issue(nextOrder[0], bot, nextOrder[1], nextOrder[2])
            #self.commandQueue.append(nextOrder())


    def freePos(self, pos):
        return self.level.findNearestFreePosition(pos)




def Command_MoveToMyFlag(commander, bot):
    r = 5
    pos = commander.game.team.flag.position
    pos = commander.level.findRandomFreePositionInBox([pos-Vector2(r,r), pos+Vector2(r,r)]) 
    commander.issue(commands.Move, bot, commander.freePos(pos), description = 'Go to my flag (DEFENDER)')
    return True

def Command_DefendMyFlag(commander, bot):
    commander.issue( commands.Defend, bot, commander.game.enemyTeam.flag.position-bot.position , description = 'Defend my flag (DEFENDER)')
    return True


def Command_DefendDirection(commander, bot, dir):
    commander.issue( commands.Defend, bot, dir , description = 'Defend direction (DEFENDER)')
    return True


def Command_AttackBot(commander, bot, enemy):
    commander.issue( commands.Attack, bot, enemy.position , description = 'Defend direction (DEFENDER)')
    return True


def Command_RunHome(commander, bot):
    target = commander.game.team.flagScoreLocation
    commander.issue(  commands.Move, bot, target, description = 'Running home (ATTACKER)')
    return True


def Command_RunToMidPoint(commander, bot):
    pos = commander.game.enemyTeam.flag.position 
    commander.issue( commands.Move, bot, commander.freePos((bot.position+pos)/2), description = 'Run to enemy flag (ATTACKER)')
    return True

                   
def Command_AttackEnemyFlag(commander, bot):
    pos = commander.game.enemyTeam.flag.position 
    commander.issue( commands.Attack, bot, commander.freePos(pos), description = 'Go to enemy flag (ATTACKER)')
    return True

    
class BTBotTask(BTAction):

    def execute(self, context):

        commander, bot = context.executionContext

        if (context.currentRunningNodeId == self.id): 
            if (bot.state == BotInfo.STATE_IDLE):
                state = BTNode.STATUS_OK
            else:
                state = BTNode.STATUS_RUNNING
                if (self.guardCondition != None):
                    condCheck = self.guardCondition(*context.executionContext)
                    if (not condCheck):
                        context.currentRunningNodeId = -1
                        state = BTNode.STATUS_OK
        else:
            state = BTAction.execute(self, context)

        #commander.log.info("Task run "+str(state))
        return state

        
DefenderBTTree = BTTree(
    BTSelector(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_SHOOTING),#continue shooting if started
        BTSequence(
            BTCondition(lambda commander,bot: len([x for x in bot.visibleEnemies if x.health>0])>0),
            BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, bot.visibleEnemies[0].position-bot.position, description='AAA'),
                      lambda commander,bot: len([x for x in bot.visibleEnemies if x.health>0])>0 )
        ),
        BTSequence(
            BTCondition(lambda commander,bot: (bot.position - commander.game.team.flag.position).length()>5),
            BTBotTask(Command_MoveToMyFlag),
            BTBotTask(Command_DefendMyFlag)
        ),
        BTBotTask(Command_DefendMyFlag)
    ),
)

AttackerBTTree = BTTree(
    BTSelector(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_SHOOTING),#continue shooting if started
        BTSequence(
            BTCondition(lambda commander,bot: len([x for x in bot.visibleEnemies if x.health>0])>0 ),
            BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, bot.visibleEnemies[0].position, description='AAA'),
                      lambda commander,bot: len([x for x in bot.visibleEnemies if x.health>0])>0 )
        ),
        BTSequence(
            BTCondition(lambda commander,bot: bot.flag),
            BTBotTask(Command_RunHome),
        ),
        BTSequence(
            BTBotTask(Command_RunToMidPoint),
            BTBotTask(Command_AttackEnemyFlag),
        ),
    ),
)
