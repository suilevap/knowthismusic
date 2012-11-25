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
            bot.brain = None
        self.defenderPart = 0.25
        self.countBot = len(self.game.team.members)
        self.lastTickTime=0
        self.lastTickEvents=0
        self.enemyBotsAlive=self.countBot;
        self.debugInfo=""

        

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""

        #self.log.info("Commander tick") 
        self.lastTickEvents=[x for x in self.game.match.combatEvents if x.time >= self.lastTickTime]
        self.lastTickEventsAnalyze()
        self.debugInfo=str(self.enemyBotsAlive)

        for bot in self.game.bots_alive:
        # define defenders
            if bot.role==PandSBot.ROLE_NONE:
                if (len(self.botsInRole(PandSBot.ROLE_DEFENDER))<=self.defenderPart*self.countBot):
                    bot.role=PandSBot.ROLE_DEFENDER
                    bot.brain = DefenderBTTree.getNewContext(self, bot)
                else:
                    bot.role=PandSBot.ROLE_ATTACKER
                    bot.brain = AttackerBTTree.getNewContext(self, bot)

                #if bot == self.game.bots_alive[0]:
                #    bot.brain = DebuggerBTTree.getNewContext(self, bot)

        for bot in self.game.bots_alive:
            if (bot.brain != None):
                bot.brain.tick()

        self.lastTickTime=self.game.match.timePassed

    
    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass


    def getBotNearestToPoint(self,position):
        return min(self.game.bots_alive, key=lambda bot: (bot.position-position).length())

    def botsInRole(self, role):
        return [bot for bot in self.game.bots_alive if bot.role==role]


    def freePos(self, pos):
        return self.level.findNearestFreePosition(pos)

    def getVisibleAliveEnemies(self,bot):
        return [x for x in bot.visibleEnemies if x.health>0]

    def getNearestVisibleAliveEnemy(self,bot):
        list = self.getVisibleAliveEnemies(bot)
        return min(list, key=lambda enemy: (enemy.position-bot.position).length())

    def lastTickEventsAnalyze(self):
        for event in self.lastTickEvents:
            if event.type==MatchCombatEvent.TYPE_RESPAWN:
                self.enemyBotsAlive=self.countBot
                print "Alive enemies: %d"%self.enemyBotsAlive
            elif event.type==MatchCombatEvent.TYPE_KILLED and event.subject.team.name!=self.game.team.name:
                self.enemyBotsAlive-=1
                print "Alive enemies: %d"%self.enemyBotsAlive

                 





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

    def __init__(self, action, guardCondition = None):
        BTAction.__init__(self, action)
        self.guardCondition = guardCondition


    def execute(self, context, currentPath, isPathLikePrev):

        commander, bot = context.executionContext

        if (context.prevPath == currentPath):
            if (bot.state != BotInfo.STATE_IDLE):
                state = BTNode.STATUS_RUNNING
                if (self.guardCondition != None):
                    condWhileCheck = self.guardCondition(*context.executionContext)
                    if (not condWhileCheck):
                        context.prevPath = []
                        state = BTNode.STATUS_OK
            else:
                state = BTNode.STATUS_OK
                context.prevPath = []
        else:
            state = BTAction.execute(self, context, currentPath, isPathLikePrev)

        #commander.log.info("Task run "+str(state))
        return state

        
DefenderBTTree = BTTree(
    BTSelector(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_SHOOTING),#continue shooting if started
         BTSequence(
            BTCondition(lambda commander,bot: commander.enemyBotsAlive==0),
            BTBotTask(Command_RunToMidPoint),
            BTBotTask(Command_AttackEnemyFlag)
        ),
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0),
            BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, commander.getNearestVisibleAliveEnemy(bot).position-bot.position, description='Wait nearest enemy'),
                      lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0 )
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
            BTCondition(lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0),
            BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.getNearestVisibleAliveEnemy(bot).position, description='Atack nearest enemy'),
                      lambda commander,bot:  len(commander.getVisibleAliveEnemies(bot))>0 )
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

DebuggerBTTree = BTTree(
    BTSequence(BTBotTask(Command_MoveToMyFlag),
               BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, bot.position, description="debug "+commander.debugInfo))
              )
    )        
