# Your AI for CTF must inherit from the base Commander class.  See how this is
# implemented by looking at the commander.py in the ./api/ folder.
from api import Commander

# The commander can send 'Commands' to individual bots.  These are listed and
# documented in commands.py from the ./api/ folder also.
from api import commands

# The maps for CTF are layed out along the X and Z axis in space, but can be
# effectively be considered 2D.
from api import Vector2


class PlaceholderCommander(Commander):
    """
    Rename and modify this class to create your own commander and add mycmd.Placeholder
    to the execution command you use to run the competition.
    """

    def initialize(self):
        """Use this function to setup your bot before the game starts."""
        self.pos = self.game.team.flag.position
        dir = [Vector2(1,0),Vector2(1.73/2,-1.0/2),Vector2(1.73/2,1.0/2),Vector2(1.0/2, 1.73/2),Vector2(1.0/2, -1.73/2),Vector2(0,1),Vector2(0,-1)]

        if self.pos.x>self.level.width/2:
            self.pos.x=self.level.width-1
            self.dir = [-d for d in dir]
        else:
            self.pos.x=0+1
            self.dir = [d for d in dir]
        self.dirIndex=0
        self.verbose = True    # display the command descriptions next to the bot labels

    def tick(self):
        """Override this function for your own bots.  Here you can access all the information in self.game,
        which includes game information, and self.level which includes information about the level."""
        
        for bot in self.game.team.members: 
            print bot.visibleEnemies,bot.seenBy
        
        # for all bots which aren't currently doing anything
        for bot in self.game.bots_available:
             # if a bot has the flag run to the scoring location
             if (bot.position-self.pos).length()>=1:
                 self.issue(commands.Move, bot, self.pos, description = 'Run to ')
             else:
                flagScoreLocation = self.game.enemyTeam.flagScoreLocation
                self.issue(commands.Defend, bot, self.dir[self.dirIndex], description = 'def')
                self.dirIndex=(self.dirIndex+1)% len(self.dir)
            

    def shutdown(self):
        """Use this function to teardown your bot after the game is over, or perform an
        analysis of the data accumulated during the game."""

        pass
