# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.


# The commander can send 'Commands' to individual bots.  These are listed and
# documented in commands.py from the ./api/ folder also.
import sys
sys.path.append("c:\\Python27\\Lib\\site-packages\\")

from api import Commander
from api import commands
from api.vector2 import Vector2
from api.gameinfo import *
from bt import *
from role import *
import MapAnalyze
from MapAnalyze import *


#from commander import *
#from commands import *
#from ctf1.gameinfo import BotInfo
#from ctf1 import commands
#from ctf1.vector2 import Vector2
#from ctf1.bt import *

from collections import deque

from random import *
from random import choice


class PandSBot(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """

    #ROLE_NONE   =  0
    #ROLE_DEFENDER =  1
    #ROLE_ATTACKER =  2

    def initialize(self):
        """Use this function to setup your bot before the game starts."""
        self.verbose = True    # display the command descriptions next to the bot labels
        for bot in self.game.team.members:            
            bot.role=None
            bot.brain = None
            bot.defendBreakingPoint=None
            bot.defendBreakingPointIndex=-1


        self.defenderPart = 0.75
        self.countBot = len(self.game.team.members)
        self.lastTickTime=0
        self.lastTickEvents=0
        self.enemyBotsAlive=self.countBot;
        self.debugInfo=""

        self.roleDefender=Role(DefenderBTTree, self.defenderSuitabilityFunction)
        self.roleAttacker=Role(AttackerBTTree, self.attackerSuitabilityFunction)

        map = self.level.blockHeights;
        self.levelAnalysis = MapAnalyzeVisibility(map)
        self.levelAnalysis.buildDirecionMap(self.game.enemyTeam.flag.position)
        self.levelAnalysis.debug()
        spawn = (self.game.enemyTeam.botSpawnArea[0]+self.game.enemyTeam.botSpawnArea[1])/2
        #path = self.levelAnalysis.getPath(spawn, self.game.team.flag.position, self.levelAnalysis.map)
        #self.levelAnalysis.getBreakingPoints(path)
        #self.levelAnalysis.getBreakingMap(path, self.level.firingDistance)
        ##result = an.buildLOS()

        self.breakingPoints = self.levelAnalysis.getBestBreakingPoints(spawn, self.game.team.flag.position, self.level.firingDistance*0.75, self.level.firingDistance*1.5, int(self.countBot)+2*0)

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) / 2.0

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()
        self.visibleEnemies =[]
        print "New commander"

        

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""

        #self.log.info("Commander tick") 
        self.lastTickEvents=[x for x in self.game.match.combatEvents if x.time >= self.lastTickTime]
        self.lastTickEventsAnalyze()
        self.debugInfo=str(self.enemyBotsAlive)
        self.reassignRoles()

        for bot in self.game.bots_alive:
        # define defenders
            if bot.role==None:
                if (len(self.botsInRole(self.roleDefender))<=self.defenderPart*self.countBot):
                    self.assignRole(bot, self.roleDefender);
                else:
                    self.assignRole(bot, self.roleAttacker);

                #if bot == self.game.bots_alive[0]:
                #    bot.brain = DebuggerBTTree.getNewContext(self, bot)

        for bot in self.game.bots_alive:
            if (bot.brain != None):
                bot.brain.tick()

        #self.levelAnalysis.updateDangerStep(self.game.bots_alive)
        #saveImage('danger', self.levelAnalysis.dangerMap)
        self.visibleEnemies = [bot for bot in self.game.enemyTeam.members if len(bot.seenBy)>0 and bot.health>0]
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
        return self.getNearest(bot, list)

    def getNearest(self,bot, list):
        if len(list)>0:
            return min(list, key=lambda item: (item.position-bot.position).length())
        else:
            return None

    def lastTickEventsAnalyze(self):
        for event in self.lastTickEvents:
            if event.type==MatchCombatEvent.TYPE_RESPAWN:
                self.enemyBotsAlive=self.countBot
                print "Alive enemies: %d"%self.enemyBotsAlive
            elif event.type==MatchCombatEvent.TYPE_KILLED and event.subject.team.name!=self.game.team.name:
                self.enemyBotsAlive-=1
                print "Alive enemies: %d"%self.enemyBotsAlive

    def reassignRoles(self):
        maxBots=len(self.game.bots_alive)
        enemies=self.enemyBotsAlive
        
        optimalDefenders=enemies*0.75
        optimalAttackers=maxBots-optimalDefenders

        if optimalAttackers<0:
            optimalAttackers=0
        defenders = self.botsInRole(self.roleDefender)
        attackers = self.botsInRole(self.roleAttacker)

        if len(defenders)<optimalDefenders:
            avalaibleBots = self.roleDefender.botsSuitability(attackers)
            n = min([len(avalaibleBots), int(optimalDefenders-len(defenders))])
            for i in range(n):
                self.assignRole(avalaibleBots[i], self.roleDefender)

        elif len(attackers)<optimalAttackers:
            avalaibleBots = self.roleDefender.botsSuitability(defenders)
            n = min([len(avalaibleBots), int(optimalAttackers-len(attackers))])
            for i in range(n):
                self.assignRole(avalaibleBots[i], self.roleAttacker)

    def assignRole(self, bot , role):
        bot.role=role
        bot.brain = bot.role.btTree.getNewContext(self, bot)

    def defenderSuitabilityFunction(self, bot):
        pos = self.game.team.flag.position
        result = -(bot.position - pos).length()
        return result;

    def attackerSuitabilityFunction(self, bot):
        pos = self.game.enemyTeam.flag.position
        result = -(bot.position - pos).length()
        return result;

    def getFlankingPosition(self, bot, target):
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (bot.position - p).length())[0]





def Command_MoveToMyFlag(commander, bot):
    r = 10
    #pos = commander.game.team.flag.position
    #sector =  commander.levelAnalysis.getSectorIndex(commander.game.enemyTeam.flag.position-bot.position)+int((random()-0.5)*4)
    #sector = sector%8

    ##pos = commander.freePos( commander.levelAnalysis.getBestPosition(pos, r))
    #pos = commander.level.findRandomFreePositionInBox([pos-Vector2(r,r), pos+Vector2(r,r)]) 
    #pos = commander.freePos( commander.levelAnalysis.getBestPositionSector(pos, r/2, sector))
    
    bot.defendBreakingPointIndex = -1

    
    freebreakingPointsIndex = set(range(len(commander.breakingPoints)))

    freebreakingPointsIndex -= set([b.defendBreakingPointIndex for b in commander.game.team.members if b.defendBreakingPointIndex>=0])
    print freebreakingPointsIndex
    if len(freebreakingPointsIndex)>0: 
        bot.defendBreakingPointIndex = min(freebreakingPointsIndex, key=lambda index: (commander.breakingPoints[index][0]-bot.position).length())
        bot.defendBreakingPoint = commander.breakingPoints[bot.defendBreakingPointIndex]
        print [b.defendBreakingPointIndex for b in commander.game.team.members]
    else:
        print 'something wrong=('
        bot.defendBreakingPoint = choice(commander.breakingPoints)

    #bot.defendBreakingPoint = choice(commander.breakingPoints)

    pos, threatPoint = bot.defendBreakingPoint
    #allPoint = [breakingP for p in commander.breakingPoints if ]
    pos = commander.freePos(pos)
    commander.issue(commands.Move, bot, commander.freePos(pos), description = 'Go to my flag (DEFENDER)')
    return True

def Command_DefendMyFlag(commander, bot):
    #dir = commander.game.enemyTeam.flag.position-bot.position;
    #dir.normalize()
    #n = len([b for b in commander.game.bots_alive if b.state==BotInfo.STATE_DEFENDING and (b.position-bot.position).length()<15])
    #for i in range(n):
    #    dir.x=dir.y
    #    dir.y=-dir.x
    dirs = []
    if bot.defendBreakingPoint != None:
        pos, threatPoints = bot.defendBreakingPoint
        dirs += [(threatPoint-bot.position, 4) for threatPoint in threatPoints]
    else:
        pos = bot.position, 


    ##dir = commander.levelAnalysis.getBestDirection(bot.position)
    ##commander.levelAnalysis.updateDanger(bot.position, dir)
   
    othersDir = commander.levelAnalysis.getAllDirections(bot.position, 4)
    dirs += [(d, 1) for d in othersDir]
    
    #dirs = []
    #i = 0
    #for threatPoint in threatPoints :
    #    part = i * 1.0 / len(threatPoints)
    #    dirs.append((threatPoint-bot.position,1+(1-part)*3))
    #    i +=1 
    shuffle(dirs)
    commander.issue( commands.Defend, bot, dirs , description = 'Defend my flag (DEFENDER)')
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

def Command_RunToEnemyFlagFlank(commander, bot):
    pos = commander.getFlankingPosition(bot, commander.game.enemyTeam.flag.position)
    commander.issue( commands.Move, bot, commander.freePos(pos), description = 'Run to enemy flag (ATTACKER)')
    return True

def Command_RunToEnemyFlag(commander, bot):
    pos = commander.game.enemyTeam.flag.position
    commander.issue( commands.Move, bot, commander.freePos(pos), description = 'Run to enemy flag (ATTACKER)')
    return True

def Command_SetEnemy(commander, bot, enemy):
    bot.Enemy = enemy
    
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

class BTBotOrder(BTAction):

    def __init__(self):
        self.priority = 0
        BTAction.__init__(self, None)


    def execute(self, context, currentPath, isPathLikePrev):

        commander, bot = context.executionContext
        action2,priority2 = bot.role.dequeOrder()
        runNew = False
        if (isPathLikePrev or context.prevPath != currentPath or priority2>self.priority):
            self.stop(context)
            self.action,self.priority = action2,priority2
            runNew = True


        if (isPathLikePrev and context.prevPath == currentPath and not runNew):
            if (bot.state != BotInfo.STATE_IDLE):
                state = BTNode.STATUS_RUNNING
            else:
                state = BTNode.STATUS_OK
                context.prevPath = []
                self.stop(context)
        elif self.action != None:
            state = BTAction.execute(self, context, currentPath, isPathLikePrev)
        else:
            state = BTNode.STATUS_FAIL

        #commander.log.info("Task run "+str(state))
        return state

    def stop(self, context):
        if self.action != None:
            commander, bot = context.executionContext
            bot.role.enqueOrder(self.action, self.priority)
            self.action = None
            self.priority = -1

TakeFlag = BTSequence(
    BTSelector(
        BTSequence(
            BTCondition(lambda commander,bot: commander.enemyBotsAlive>0),
            BTBotTask(Command_RunToEnemyFlagFlank, 
                        lambda commander,bot: commander.enemyBotsAlive>0),
            BTBotTask(Command_AttackEnemyFlag)
        ),
        BTSequence(
            BTBotTask(Command_RunToEnemyFlag, 
                        lambda commander,bot: commander.enemyBotsAlive==0)
        )
    )
)

ReturnFlag = BTSequence(
    BTCondition(lambda commander,bot: bot.flag),
    BTBotTask(Command_RunHome)
)
SupportFlagCarrier =BTSequence(
    BTCondition(lambda commander,bot: commander.game.enemyTeam.flag.carrier != None and commander.game.enemyTeam.flag.carrier!=bot),
    BTSelector(
        BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.enemyTeam.flag.position,description='Support carrier (ATTACKER)'))
        
    )
)
ChaseFlagCarrier =BTSequence(
    BTCondition(lambda commander,bot: commander.game.team.flag.carrier != None),
    BTSelector(
        BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.team.flag.position,description='Chase carrier (DEFENDER)'))
    )
)

SmartAttack = BTSelector(
    BTCondition(lambda commander,bot: bot.Enemy==None),
    BTSequence(
        BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()<10),
        BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, bot.Enemy.position-bot.position, description='Wait nearest enemy'),
                    lambda commander,bot: bot.Enemy!=None and bot.Enemy.health>0 )
        ) ,
    BTSequence(
        BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()),
        BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, bot.Enemy.position, bot.Enemy.position,description='Attack nearest enemy'),
                    lambda commander,bot: bot.Enemy!=None and bot.Enemy.health>0 )
        )
)
  
        
DefenderBTTree = BTTree(
    BTSelector(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_SHOOTING),#continue shooting if started

        ReturnFlag,
        BTSequence(
            BTCondition(lambda commander,bot: commander.enemyBotsAlive==0),
            TakeFlag
        ),

        #or
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0),
            BTSelector(
                BTSequence(
                    BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()<10),
                    BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, commander.getNearestVisibleAliveEnemy(bot).position-bot.position, description='Wait nearest enemy'),
                              lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0 )
                    ),
                BTSequence(
                    BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()),
                    BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.getNearestVisibleAliveEnemy(bot).position, commander.getNearestVisibleAliveEnemy(bot).position,description='Attack nearest enemy'),
                              lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0 )
                    )
                )
        ),
        #or
        ChaseFlagCarrier,
        #or
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.visibleEnemies)>0),
            BTBotTask(lambda commander,bot: Command_SetEnemy(commander,bot, commander.getNearest(bot,commander.visibleEnemies))),
            BTCondition(lambda commander,bot: bot.Enemy!= None and (bot.Enemy.position-bot.position).length()<commander.level.firingDistance),
            SmartAttack
        ),
        #or
        BTSequence(
            BTCondition(lambda commander,bot: (bot.position - commander.game.team.flag.position).length()>5),
            BTBotTask(Command_MoveToMyFlag),
            BTBotTask(Command_DefendMyFlag)
        ),
        #or
        BTBotTask(Command_DefendMyFlag)
    )
)

AttackerBTTree = BTTree(
    BTSelector(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_SHOOTING),#continue shooting if started

        ReturnFlag,

        BTSequence(
            BTCondition(lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0),
            BTCondition(lambda commander,bot: commander.getNearestVisibleAliveEnemy(bot) not in bot.seenBy),
            BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.getNearestVisibleAliveEnemy(bot).position,commander.getNearestVisibleAliveEnemy(bot).position, description='Atack nearest enemy'),
                      lambda commander,bot:  len(commander.getVisibleAliveEnemies(bot))>0 )
        ),
        SupportFlagCarrier,
        TakeFlag
    ),
)


