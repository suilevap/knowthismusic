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

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) / 2.0

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()

        for bot in self.game.team.members:            
            bot.role=None
            bot.brain = None
            bot.defendBreakingPoint=None
            bot.defendBreakingPointIndex=-1
            bot.Enemy = None
            bot.enemyDefenders = []
            bot.safePathFailedLastTime = False


        self.defenderPart = 0.4
        self.countBot = len(self.game.team.members)
        self.lastTickTime=0.0
        self.lastTickEvents=0
        self.enemyBotsAlive=0*self.countBot;
        self.debugInfo=""

        self.roleDefender=Role(DefenderBTTree, self.defenderSuitabilityFunction)
        self.roleAttacker=Role(AttackerBTTree, self.attackerSuitabilityFunction)

        map = self.level.blockHeights;
        self.levelAnalysis = MapAnalyzeVisibility(map)
        self.levelAnalysis.buildDirecionMap(self.game.enemyTeam.flag.position)
        self.levelAnalysis.debug()
        self.spawn = (self.game.enemyTeam.botSpawnArea[0]+self.game.enemyTeam.botSpawnArea[1])/2
        self.ourSpawn = (self.game.team.botSpawnArea[0]+self.game.team.botSpawnArea[1])/2

        #path = self.levelAnalysis.getPath(spawn, self.game.team.flag.position, self.levelAnalysis.map)
        #self.levelAnalysis.getBreakingPoints(path)
        #self.levelAnalysis.getBreakingMap(path, self.level.firingDistance)
        ##result = an.buildLOS()
        self.attackingPaths = self.levelAnalysis.getBestBreakingPoints([self.ourSpawn], self.game.enemyTeam.flag.position, self.level.firingDistance*0.75, self.level.firingDistance*1.5, int(self.countBot)+2*0)

        ourFlanks = [self.freePos(self.game.team.flag.position + f * 16.0) for f in [self.left, self.right]]
        startPoints = [self.spawn]+ourFlanks
        self.breakingPoints = self.levelAnalysis.getBestBreakingPoints(startPoints, self.game.team.flag.position, self.level.firingDistance*0.75, self.level.firingDistance*1.5, int(self.countBot)+2*0)


        self.visibleEnemies =[]
        self.eventInvalidationTime = 2.0
        self.dangerEnemies =[]
        self.dangerEvents = []
        self.dangerMapUpdated = False
        self.timeMap = self.generateTimeMap()

        self.enemyDefendersDelta = 0
        self.enemyDefendersPrevious = 0
        

        #print self.level.initializationTime
        #print "New commander"
        self.dangerAtRespawn = 0.0;
        self.lastRespawnTime = 0;
        self.updateDangerAtRespawn()
        

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""
       
        self.visibleEnemies = [bot for bot in self.game.enemyTeam.members if len(bot.seenBy)>0 and bot.health>0]
        self.visibleEnemies2 = [[b.name for b in bot.visibleEnemies] for bot in self.game.team.members]

        #print [b.health for b in self.visibleEnemies ]
        #print self.visibleEnemies2

        self.dangerEnemies = [bot for bot in self.game.enemyTeam.members 
                               if bot.health>0 and 
                               ((bot.seenlast)<self.eventInvalidationTime or 
                                (bot.state == BotInfo.STATE_DEFENDING and (bot.seenlast)<self.eventInvalidationTime*2))]

        self.enemyDefenders = [b for b in self.game.enemyTeam.members if b.state == BotInfo.STATE_DEFENDING and b.health>0] 
        self.enemyDefendersDelta = len(self.enemyDefenders)-self.enemyDefendersPrevious
        self.enemyDefendersPrevious = len(self.enemyDefenders)
        #if self.enemyDefendersDelta!=0:
        #    print self.enemyDefendersDelta
        self.dangerMapUpdated = False

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
      
        #print self.dangerEnemies
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

    def getBestEnemy(self,bot, list):
        def getEnemyInverstPriority(bot,enemy):
            result = (bot.position-enemy.position).length()
            if (bot in enemy.visibleEnemies):
                result /= 2
            if (bot in enemy.seenBy):
                result /= 1.5
            return result 

        if len(list)>0:
            return min(list, key=lambda item: getEnemyInverstPriority(bot, item))
        else:
            return None

    def updateDangerAtRespawn(self):
        #if (self.spawn-self.ourSpawn).length()>self.level.firingDistance*2:
        self.dangerAtRespawn = ((self.countBot-self.enemyBotsAlive)*1.0)/self.countBot
        self.lastRespawnTime = self.game.match.timePassed;
        #else:
        #    self.dangerAtRespawn = 0.8
        #print 'danger:' + str(self.dangerAtRespawn)

    def lastTickEventsAnalyze(self):
        self.dangerEvents = [e for e in self.dangerEvents if (self.game.match.timePassed-e.time)<self.eventInvalidationTime]
 
        for event in self.lastTickEvents:

            if event.type==MatchCombatEvent.TYPE_RESPAWN:
                bot = event.subject
                if bot in self.game.enemyTeam.members:
                    bot.position = self.level.findRandomFreePositionInBox(self.game.enemyTeam.botSpawnArea)
                    bot.seenLast = 0
                    bot.health = 100
                    bot.facingDirection = Vector2((random()-0.5),random()-0.5)

                if  self.enemyBotsAlive!=self.countBot:
                    self.updateDangerAtRespawn()
                    self.enemyBotsAlive=self.countBot
                #print "Alive enemies: %d"%self.enemyBotsAlive
            elif event.type==MatchCombatEvent.TYPE_KILLED:
                if event.subject.team.name!=self.game.team.name:
                    self.enemyBotsAlive-=1
                    #print "Alive enemies: %d"%self.enemyBotsAlive
                else:
                    self.dangerEvents.append(event)
                    #pos = e.instigator.position if e.instigator!=None else e.subject.position
                    pos = event.subject.position
                    self.levelAnalysis.updateDangerStatic(pos, 4, 196)
            elif event.type == MatchCombatEvent.TYPE_FLAG_PICKEDUP and event.subject.team.name==self.game.team.name:
                self.dangerEvents.append(event)

        #if len(self.dangerEvents)>0:
        #    print 'events'
        #    print self.dangerEvents

    def reassignRoles(self):
        maxBots=len(self.game.bots_alive)
        enemies=self.enemyBotsAlive
        
        optimalDefenders=self.defenderPart*(enemies-len(self.enemyDefenders))
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

    def botCanSeePos(self, bot, pos):
        return self.levelAnalysis.checkVisibility(bot.position, pos)

    def getSafePath(self, start, end):
        if not self.dangerMapUpdated:
            #print 'dangerMapUpdated'
            #print self.dangerEnemies
            self.levelAnalysis.updateDangerStep(self.dangerEnemies, self.level.firingDistance*1.0)
            self.dangerMapUpdated = True
        path = self.levelAnalysis.getPathThroughDanger(start, end)
        return path

    def generateTimeMap(self):
        path, distMap, parentMap = getPathWithPathDistanceMap(self.spawn, self.game.team.flag.position, self.levelAnalysis.pathMap, False)
        #dirMap = computeMap(parentMap, 
        #                    lambda v,x,y: 
        #                        Vector2(v[0]-x, v[1]-y).normalized() 
        #                        if v!=None and (x-v[0]!=0 or y-v[1]!=0) 
        #                        else None)
        #saveImageVector('dirMap', dirMap)

        #fireStepMap = computeMap(distMap, lambda v,x,y: 
        #                         v - self.levelAnalysis.visibleSectors[self.levelAnalysis.getSectorIndex(dirMap[x][y])][x][y][1]
        #                         if dirMap[x][y] != None else v )


        saveImage('distMapOr', distMap)
        
        timeMap = computeMap(distMap, lambda v,x,y: (v-self.level.firingDistance) /self.level.runningSpeed)
        saveImage('distMap', timeMap)

        #timeMap5s = computeMap(timeMap, lambda v,x,y: 255 if v>5 else v)
        #saveImage('timeMap3s', timeMap5s)
        return timeMap

    def IsPosSafeNow(self, pos):
        if self.enemyBotsAlive == 0:
            return True
        if self.dangerAtRespawn<0.3:
            return False

        deltaTime = self.game.match.timePassed - self.lastRespawnTime;
        
        x,y = int(pos.x), int(pos.y)
        safeTime = self.timeMap[x][y]
        isSafe = safeTime>deltaTime

        return isSafe

    def distToNextRespawn(self):
        return self.game.match.timeToNextRespawn*self.level.runningSpeed