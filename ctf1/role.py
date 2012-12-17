from collections import deque

from random import *
from random import choice
from random import random

from api import Commander
from api import commands
from api.vector2 import Vector2
from api.gameinfo import *

from bt import *
from role import *
import MapAnalyze
from MapAnalyze import *




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


def Command_MoveToBreakingPoint(commander, bot, breakingPoint):
    pos, threatPoints = breakingPoint[:2] #bot.defendBreakingPoint
    #commander.issue(commands.Attack, bot, commander.freePos(pos), threatPoints[0], description = 'Patrol (DEFENDER)')
    commander.issue(commands.Attack, bot, commander.freePos(threatPoints[0]), description = 'Patrol (DEFENDER)')



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
    #print freebreakingPointsIndex
    if len(freebreakingPointsIndex)>0: 
        bot.defendBreakingPointIndex = list(freebreakingPointsIndex)[0]#min(freebreakingPointsIndex, key=lambda index: (commander.breakingPoints[index][0]-bot.position).length())
        bot.defendBreakingPoint = commander.breakingPoints[bot.defendBreakingPointIndex]
        #print [b.defendBreakingPointIndex for b in commander.game.team.members]
    else:
        #print 'something wrong=('
        bot.defendBreakingPoint = choice(commander.breakingPoints)

    #bot.defendBreakingPoint = choice(commander.breakingPoints)

    pos, threatPoints = bot.defendBreakingPoint[:2]
    #allPoint = [breakingP for p in commander.breakingPoints if ]
    pos = commander.freePos(pos)
    commander.issue(commands.Charge, bot, commander.freePos(pos), description = 'Go to my flag (DEFENDER)')
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
        pos, threatPoints = bot.defendBreakingPoint[:2]
        dirs += [(threatPoint-bot.position, 4) for threatPoint in threatPoints]
        mainDir = dirs[0][0]
    else:
        pos = bot.position
        mainDir = commander.levelAnalysis.getBestDirection(pos)

    ##dir = commander.levelAnalysis.getBestDirection(bot.position)
    ##commander.levelAnalysis.updateDanger(bot.position, dir)
   
    othersDir = commander.levelAnalysis.getAllDirections(bot.position, 4, commander.levelAnalysis.getSectorIndex(mainDir), 1)
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


def Command_RunHomeSafe(commander, bot):
    target = commander.game.team.flagScoreLocation
    path = commander.getSafePath(bot.position, target)
    commander.issue(  commands.Charge, bot, path, description = 'Running home safe (ATTACKER)')
    return True

def Command_RunHome(commander, bot):
    target = commander.game.team.flagScoreLocation
    commander.issue(  commands.Charge, bot, target, description = 'Running home (ATTACKER)')
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
    commander.issue( commands.Attack, bot, commander.freePos(pos), description = 'Run to enemy flag (ATTACKER)')
    return True

def Command_RunToEnemyFlagFlank3(commander, bot):
    pos = commander.freePos(commander.game.enemyTeam.flag.position)
    path = GetPathFromFlank(commander, bot,pos)
    if len(path)<=1:
        return False
    ran =random.random()
    if ran<commander.dangerAtRespawn:
        command = commands.Attack
    else:
        command = commands.Charge

    commander.issue( command, bot, path, description = 'Goto flag use danger map (ATTACKER)')
    return True

def Command_RunToEnemyFlagFlank2(commander, bot):
    pos = commander.game.enemyTeam.flag.position
    pos, threat, tmpPath, map, index = choice(commander.attackingPaths)
    path = getPath(bot.position, commander.freePos(pos), map)
    if index > len(commander.attackingPaths):#/2:
        command = commands.Charge
    else:
        command = commands.Attack

    commander.issue( command, bot, path, description = 'Flank to enemy flag (ATTACKER)')
    return True

def Command_RunToEnemyFlag(commander, bot):
    pos = commander.game.enemyTeam.flag.position
    commander.issue( commands.Charge, bot, pos, description = 'Run to enemy flag (ATTACKER)')
    return True



def Condition_SetEnemy(commander, bot, enemy):
    #if bot.Enemy!=None:
    #    print bot.Enemy.name+' health='+str(bot.Enemy.health)
    #if enemy!=None:
    #    print bot.name + ' has enemy ' + enemy.name
    bot.Enemy = enemy
    return True

def Condition_ReadyToAttack(commander, bot):
    result = (bot.state==BotInfo.STATE_SHOOTING or bot.state==BotInfo.STATE_TAKINGORDERS
               or len([(b.position-bot.position).length()<commander.level.firingDistance for b in bot.visibleEnemies if b.health>0])>0)
    return result

def Condition_SetEnemyIfNotNone(commander, bot, enemy):
    #if bot.Enemy!=None:
    #    print bot.Enemy.name+' health='+str(bot.Enemy.health)
    #if enemy!=None:
    #    print bot.name + ' has enemy ' + enemy.name
    if enemy != None:
        bot.Enemy = enemy
    return bot.Enemy != None

def LookAtDangerEvent(commander, bot):
    allSuspicious = [(e.instigator.position,e) if e.instigator!=None else (e.subject.position,e) for e in commander.dangerEvents]
    allSuspicious = [p for p in allSuspicious if p[0] != None]
    if len(allSuspicious)==0:
        return False
    suspicious = min(allSuspicious, key=lambda p:(bot.position-p[0]).length() )
    if (bot.position - suspicious[0]).length()>commander.level.firingDistance*1.5:
        return False
    dir = suspicious[0] - bot.position
    bot.investigateEvent = suspicious[1]
    commander.issue( commands.Defend, bot, dir , description = 'Look at suspicious event (DEFENDER)')

def Command_AttackEnemyFromFlank(commander, bot):
    path = GetPathFromFlank(commander, bot, bot.Enemy.position)
    if len(path)>0:
        commander.issue(commands.Attack, bot, path, bot.Enemy.position,description='Attack enemy from flank');
        return True
    else:
        return False
    ##print 'Attack from flank'
    #recalculatePath = True;
    #if (bot.safePathFailedLastTime):
    #    recalculatePath = False;
    #    for b in bot.enemyDefenders:
    #        if b.health <= 0 or b.state != BotInfo.STATE_DEFENDING:
    #            recalculatePath = True;
    #            break;
    #path =[]

    #if (recalculatePath):
    #    path = commander.getSafePath(bot.position, bot.Enemy.position)
    #
    #if len(path)>1:
    #    bot.safePathFailedLastTime = False
    #    commander.issue(commands.Attack, bot, path, bot.Enemy.position,description='Attack enemy from flank')
    #else:
    #    if recalculatePath:
    #        bot.enemyDefenders = [b for b in commander.visibleEnemies if b.health > 0 and b.state == BotInfo.STATE_DEFENDING]
    #    bot.safePathFailedLastTime = True
    #    return False

def GetPathFromFlank(commander, bot, pos):
    #print 'Attack from flank'
    recalculatePath = True;
    if (bot.safePathFailedLastTime):
        recalculatePath = False;
        for b in bot.enemyDefenders:
            if b.health <= 0 or b.state != BotInfo.STATE_DEFENDING:
                recalculatePath = True;
                break;
    path =[]

    if (recalculatePath):
        path = commander.getSafePath(bot.position, pos)
  
    if len(path)>1:
        bot.safePathFailedLastTime = False
        #commander.issue(commands.Attack, bot, path, bot.Enemy.position,description='Attack enemy from flank')
    else:
        if recalculatePath:
            bot.enemyDefenders = [b for b in commander.visibleEnemies if b.health > 0 and b.state == BotInfo.STATE_DEFENDING]
        bot.safePathFailedLastTime = True
    return path

def Command_AttackEnemy(commander, bot):
    #print 'Attack direct'
    commander.issue(commands.Attack, bot,bot.Enemy.position, bot.Enemy.position,description='Attack enemy directly')

def Command_None(commander, bot):
    #print 'Do nothing'
    return True

def Command_ChargeEnemyWithPrediction(commander, bot):
    #print 'Charge with prediction'
    pos = bot.Enemy.position + bot.Enemy.facingDirection * commander.level.runningSpeed *1
    commander.issue(commands.Charge, bot, commander.freePos(pos),description='Charge enemy with prediction')

def GetFriends(commander, bot):
    result = []
    distance = (bot.position - bot.Enemy.position).length()
    if distance<commander.level.firingDistance+5:
        for friend in commander.game.bots_alive:
            if (friend!=bot 
                and friend.Enemy in bot.seenBy 
                and friend.Enemy in friend.visibleEnemies
                and friend.state==BotInfo.STATE_DEFENDING 
                and abs((friend.position-friend.Enemy.position).length()-distance)<1):

                result.append(bot)
    return result 

def Command_MoveToSuppressEnemyPosition(commander, bot):
    dir = bot.position - bot.Enemy.position
    dir.normalize()
    pos = bot.Enemy.position + dir * (commander.level.firingDistance+2)
    commander.issue(commands.Charge, bot, commander.freePos(pos), description='Suppress Enemy')
    return True

def GetInterceptPoint(commander, bot, start, end, delta=0):
    path = getPath(start, end, commander.levelAnalysis.map)
    #min(path, key=lambda p: 
    #myPath,distmap, parent = getPathWithPathDistanceMap(bot.position, end, commander.levelAnalysis.map, False)
    pos = end
    for p in path:
        if (p-start).length()-delta>(p-bot.position).length():
            pos = p
            break
    return pos


InterceptEnemy = BTSequence('Intercept My Flag',
    BTCondition(lambda commander,bot: commander.game.team.flag.carrier != None,
        BTSelector(
            BTSequence(
                BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()< commander.level.firingDistance*1.5 
                            and (commander.game.enemyTeam.flagScoreLocation-bot.position).length()<(commander.game.enemyTeam.flagScoreLocation-commander.game.team.flag.position).length(),
                #BTCondition(lambda commander,bot: (GetInterceptPoint(commander, bot,commander.game.team.flag.position, commander.game.enemyTeam.flagScoreLocation)-bot.position).length()< commander.level.firingDistance*1.5),
                #BTBotTask(lambda commander,bot:Command_DefendDirection(commander,bot,bot.Enemy.position-bot.position ))
                #SmartAttack
                    BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, GetInterceptPoint(commander, bot,commander.game.team.flag.position, commander.game.enemyTeam.flagScoreLocation, commander.level.firingDistance*1.2*0), description='Intercept Attack flag carrier (ATTACKER)'))
                )
            ),
            BTSequence(
                BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, GetInterceptPoint(commander, bot,commander.game.team.flag.position, commander.game.enemyTeam.flagScoreLocation), description='Intercept flag carrier (ATTACKER)'))
            )
        )
    )
)

TakeFlag = BTSequence('TakeFlag',
    BTCondition(lambda commander,bot: commander.game.enemyTeam.flag.carrier==None ,
        BTSelector(
            BTCondition((lambda commander,bot: commander.enemyBotsAlive>0 and (commander.game.enemyTeam.flag.position-bot.position).length()>commander.level.firingDistance*1.2),
                BTSelector(
                    BTBotTask(Command_RunToEnemyFlagFlank3)
                )
            ),
            #BTBotTask(Command_RunToEnemyFlag)
            BTCondition(
                lambda commander,bot:(commander.game.enemyTeam.flag.position-bot.position).length()>commander.level.firingDistance*1.2 or commander.enemyBotsAlive==0,
                BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.enemyTeam.flag.position, description='Charge flag (ATTACKER)'))
            ),
            BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.game.enemyTeam.flag.position, commander.game.enemyTeam.flag.position, description='Attack flag (ATTACKER)'))
        )
    )

    #BTSelector(
    #    BTSequence(
    #        BTCondition(lambda commander,bot: commander.botCanSeePos(bot, commander.game.enemyTeam.flag.position) ),
    #        BTBotTask(Command_RunToEnemyFlag)
    #    ),
    #    BTSequence(
    #        BTCondition(lambda commander,bot: commander.enemyBotsAlive>0),
    #        BTCondition(lambda commander,bot: (bot.position-commander.game.enemyTeam.flag.position).length()>16),

    #        BTBotTask(Command_RunToEnemyFlagFlank, 
    #                    lambda commander,bot: commander.enemyBotsAlive>0),
    #        BTBotTask(Command_AttackEnemyFlag)
    #    ),
    #    BTSequence(
    #        BTBotTask(Command_RunToEnemyFlag, 
    #                    lambda commander,bot: commander.enemyBotsAlive==0)
    #    )
    #)
)

ReturnFlag = BTSequence(
    BTCondition(lambda commander,bot: bot.flag!=None),
    BTSelector(
        BTCondition(lambda commander,bot: commander.enemyBotsAlive>0,
            BTBotTask(Command_RunHomeSafe)),
        BTBotTask(Command_RunHome)
    )
)
SupportFlagCarrier =BTSequence(
    BTCondition(lambda commander,bot: commander.game.enemyTeam.flag.carrier != None and commander.game.enemyTeam.flag.carrier!=bot),
    BTSelector(
        BTSequence(
            BTCondition(lambda commander,bot: (commander.game.enemyTeam.flag.position-commander.game.team.flagScoreLocation).squaredLength()<(bot.position-commander.game.team.flagScoreLocation).squaredLength()),
            BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.team.flagScoreLocation, description='Support carrier (ATTACKER)'))
        ),
        BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.game.team.flagScoreLocation, description='Support carrier (ATTACKER)'))
    ),
    BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.game.enemyTeam.flag.position, description='Support carrier (ATTACKER)'))

)
ReturnMyFlag =BTSequence(
    BTCondition(lambda commander,bot: commander.game.team.flag.carrier != None,
        BTSelector(
            InterceptEnemy,
            BTSequence(
                BTCondition(lambda commander,bot: (commander.game.team.flag.position-commander.game.enemyTeam.flagScoreLocation).length()>(bot.position-commander.game.enemyTeam.flagScoreLocation).length()-commander.level.firingDistance),
                BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.team.flagScoreLocation, description='ReturnMyFlag (ATTACKER)'))
            )#,
            #BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.game.enemyTeam.flagScoreLocation, description='ReturnMyFlag (ATTACKER)'))
        )
    )
    #BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.game.team.flag.position, description='ReturnMyFlag (ATTACKER)')),

)
ChaseFlagCarrier =BTSequence(
    BTCondition(lambda commander,bot: commander.game.team.flag.carrier != None),
    BTSelector(
        BTBotTask(lambda commander,bot: commander.issue(commands.Charge, bot, commander.game.team.flag.position,description='Chase carrier (DEFENDER)'))
    )
)

AttackFromFlank = BTSelector('Attack from flank',
    BTCondition(lambda commander, bot: commander.enemyDefendersDelta!=0,
        BTBotTask(Command_None)
    ),
    BTBotTask(Command_AttackEnemyFromFlank),
    BTSequence(
        BTCondition(lambda commander,bot: bot.state==BotInfo.STATE_DEFENDING and len(GetFriends(commander,bot))>=len(bot.seenBy)),
        BTBotTask(Command_AttackEnemy)
    ),
    BTSequence(
        BTBotTask(Command_MoveToSuppressEnemyPosition),

        BTBotTask(lambda commander,bot:Command_DefendDirection(commander,bot,bot.Enemy.position-bot.position ))
    )
)

SmartAttack = BTSequence('SmartAttack',
    BTCondition(lambda commander,bot: bot.Enemy!=None and bot.Enemy.health>0,
        BTSelector(
            BTSequence('Killed Enemy',
                BTCondition(lambda commander,bot: bot.Enemy==None or bot.Enemy.health<=0),
                BTCondition(lambda commander,bot: Condition_SetEnemy(commander, bot, None)),
                BTBotTask(Command_None)
            ),
            BTSequence('EnemySee',
                BTCondition(lambda commander,bot: bot in bot.Enemy.visibleEnemies),
                BTSelector(                    
                    BTSequence('EnemyAttacking',
                        BTCondition(lambda commander,bot: bot.Enemy.state == BotInfo.STATE_ATTACKING,
                            BTBotTask(lambda commander,bot:Command_DefendDirection(commander,bot,bot.Enemy.position-bot.position ))
                        )
                    ),
                    BTSequence('EnemyDefending',
                        BTCondition(lambda commander,bot: bot.Enemy.state == BotInfo.STATE_DEFENDING),

                        AttackFromFlank
                    )
                    #BTBotTask(Command_AttackEnemy)
                )
            ),

            BTSequence('EnemyNotSee',
                BTSelector(
                    BTSequence(
                        BTCondition(lambda commander,bot: bot.Enemy in bot.visibleEnemies),
                        BTSelector(
                            BTSequence('EnemyDefendingOrAttacking',
                                BTCondition(lambda commander,bot: bot.Enemy.state == BotInfo.STATE_DEFENDING or bot.Enemy.state == BotInfo.STATE_ATTACKING),
                                BTBotTask(Command_AttackEnemy )
                            ),
                            BTBotTask(Command_ChargeEnemyWithPrediction)
                        )
                    ),
                    BTSequence(
                        BTCondition(
                                    lambda commander,bot: 
                                        (bot.Enemy.position- commander.game.enemyTeam.flag.position).length()<(bot.position- commander.game.enemyTeam.flag.position).length()),
                        BTSelector(
                                BTSequence('EnemyDefendingOrAttacking',
                                    BTCondition(lambda commander,bot: bot.Enemy.state == BotInfo.STATE_DEFENDING),
                                    AttackFromFlank
                                ),
                                BTBotTask(Command_ChargeEnemyWithPrediction)
                        )
                    )
                )
            )#,
        
            #BTBotTask(Command_AttackEnemy)

            #BTSequence(
            #    BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()<10),
            #    BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, bot.Enemy.position-bot.position, description='Wait nearest enemy'),
            #                lambda commander,bot: bot.Enemy!=None and bot.Enemy.health>0 )
            #    ),
            #BTSequence(
            #    #BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()),
            #    BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, bot.Enemy.position, bot.Enemy.position,description='Attack nearest enemy'),
            #                lambda commander,bot: bot.Enemy!=None and bot.Enemy.health>0 )
            #    )
        )
    )
)
BaseLogic = BTSequence(
    BTCondition(lambda commander,bot: (commander.game.enemyTeam.flag.position-bot.position).length()<10),
    TakeFlag
)

ReactAtDanger = BTSequence(
            BTCondition(lambda commander,bot: len(commander.dangerEvents)>0),
            BTBotTask(LookAtDangerEvent,
                      lambda commander,bot: bot.investigateEvent==None or bot.investigateEvent in commander.dangerEvents)
        )  
        
DefenderBTTree = BTTree(
    BTSelector(

        BTCondition(Condition_ReadyToAttack ),#continue shooting if started
        ReturnFlag,
        BaseLogic,

        BTSequence(
            BTCondition(lambda commander,bot: commander.enemyBotsAlive==0 or (commander.game.enemyTeam.flag.position-bot.position).length()<16),
            TakeFlag
        ),

        ##or
        #BTSequence(
        #    BTCondition(lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0),
        #    BTSelector(
        #        BTSequence(
        #            BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()<10),
        #            BTBotTask(lambda commander,bot: commander.issue(commands.Defend, bot, commander.getNearestVisibleAliveEnemy(bot).position-bot.position, description='Wait nearest enemy'),
        #                      lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0 )
        #            ),
        #        BTSequence(
        #            BTCondition(lambda commander,bot: (commander.game.team.flag.position-bot.position).length()),
        #            BTBotTask(lambda commander,bot: commander.issue(commands.Attack, bot, commander.getNearestVisibleAliveEnemy(bot).position, commander.getNearestVisibleAliveEnemy(bot).position,description='Attack nearest enemy'),
        #                      lambda commander,bot: len(commander.getVisibleAliveEnemies(bot))>0 )
        #            )
        #        )
        #),
        #or
        ReturnMyFlag,
        #or 
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.dangerEvents)>0),
            BTBotTask(LookAtDangerEvent,
                      lambda commander,bot: bot.investigateEvent==None or bot.investigateEvent in commander.dangerEvents)
        ),
        #or
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.visibleEnemies)>0),
            BTCondition(lambda commander,bot: Condition_SetEnemy(commander,bot, commander.getBestEnemy(bot,commander.visibleEnemies))),
            BTCondition(lambda commander,bot: bot.Enemy!= None and 
                        (bot.Enemy.position-bot.position).length()<commander.level.firingDistance *2 and commander.botCanSeePos(bot, bot.Enemy.position)),
            SmartAttack
        ),
        #or

        BTSelector(
            #BTSequence(
            #    BTCondition(lambda commander,bot: bot.state == BotInfo.STATE_IDLE and random()>0.5),
            #    BTSelector(
            #        BTCondition(lambda commander,bot: (bot.position - commander.game.team.flag.position).length()<5),
            #        #or
            #        BTBotTask(Command_MoveToMyFlag)
            #    ),

            #    BTBotTask(lambda commander,bot: Command_MoveToBreakingPoint(commander, bot, choice(commander.breakingPoints))),
            #    BTBotTask(lambda commander,bot: Command_MoveToBreakingPoint(commander, bot, choice(commander.breakingPoints))),
            #    BTBotTask(lambda commander,bot: Command_MoveToBreakingPoint(commander, bot, choice(commander.breakingPoints))),
            #),
            BTSequence(
                BTCondition(lambda commander,bot: (bot.position - commander.game.team.flag.position).length()>5),
                BTBotTask(Command_MoveToMyFlag),
                BTBotTask(Command_DefendMyFlag)
            )
        ),
        #or
        BTBotTask(Command_DefendMyFlag)
    )
)

AttackerBTTree = BTTree(
    BTSelector(
        BTCondition(Condition_ReadyToAttack),#continue shooting if started
        ReturnFlag,
        #BaseLogic,
        BTSequence(
            BTCondition(lambda commander,bot: len(commander.visibleEnemies)>0),
            BTCondition(lambda commander,bot: Condition_SetEnemyIfNotNone(commander,bot, commander.getBestEnemy(bot,commander.visibleEnemies)) 
                        and bot.Enemy!=None and (bot.Enemy.position-bot.position).length()<commander.level.firingDistance*4,
            #BTCondition(lambda commander,bot: bot.Enemy!= None and 
            #            (bot.Enemy.position-bot.position).length()<commander.level.firingDistance 
            #            and commander.botCanSeePos(bot, bot.Enemy.position)),
                SmartAttack
            )
        ),
        ReactAtDanger,
        TakeFlag,
        ReturnMyFlag,
        SupportFlagCarrier
    ),
)


