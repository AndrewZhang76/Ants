"""CS 61A presents Ants Vs. SomeBees."""

import random
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################

class Place:
    """A Place holds insects and has an exit to another Place."""

    def __init__(self, name, exit=None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name = name
        self.exit = exit
        self.bees = []        # A list of Bees
        self.ant = None       # An Ant
        self.entrance = None  # A Place
        # Phase 1: Add an entrance to the exit
        if self.exit:
            exit.entrance=self

    def add_insect(self, insect):
        """
        Asks the insect to add itself to the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect):
        """
        Asks the insect to remove itself from the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has armor and a Place."""

    damage = 0
    is_watersafe=False

    def __init__(self, armor, place=None):
        """Create an Insect with an ARMOR amount and a starting PLACE."""
        self.armor = armor
        self.place = place  # set by Place.add_insect and Place.remove_insect

    def reduce_armor(self, amount):
        """Reduce armor by AMOUNT, and remove the insect from its place if it
        has no armor remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_armor(2)
        >>> test_insect.armor
        3
        """
        self.armor -= amount
        if self.armor <= 0:
            self.place.remove_insect(self)
            self.death_callback()

    def action(self, gamestate):
        """The action performed each turn.

        gamestate -- The GameState, used to access game state information.
        """

    def death_callback(self):
        # overriden by the gui
        pass

    def add_to(self, place):
        """Add this Insect to the given Place

        By default just sets the place attribute, but this should be overriden in the subclasses
            to manipulate the relevant attributes of Place
        """
        self.place = place

    def remove_from(self, place):
        self.place = None


    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.armor, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    blocks_path = True
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, armor=1):
        """Create an Ant with an ARMOR quantity."""
        Insect.__init__(self, armor)

    def can_contain(self, other):
        return False

    def contain_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
        elif isinstance(place.ant, ContainerAnt) and place.ant.can_contain(self) and not isinstance(self, ContainerAnt):
            place.ant.contain_ant(self)
        elif not isinstance(place.ant, ContainerAnt) and isinstance(self, ContainerAnt):
            self.contain_ant(place.ant)
            place.ant=self
            
        else:
            # BEGIN Problem 9
            assert place.ant is None, 'Two ants in {0}'.format(place)
            # END Problem 9
        Insect.add_to(self, place)

    def remove_from(self, place):
        if not isinstance(place.ant, QueenAnt) or place.ant.is_queen==False:
            
            if place.ant is self:
                place.ant = None
                Insect.remove_from(self, place)
            elif place.ant is None:
                assert False, '{0} is not in {1}'.format(self, place)
                Insect.remove_from(self, place)
            elif not isinstance(place.ant.contained_ant, QueenAnt) or place.ant.contained_ant.is_queen==False:
                place.ant.remove_ant(self)
                Insect.remove_from(self, place)
            

class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE

    def action(self, gamestate):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        gamestate.food+=1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    min_range=0
    max_range=float('inf')
    damage = 1
    food_cost=3
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE

    def nearest_bee(self, beehive):
        """Return the nearest Bee in a Place that is not the HIVE, connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        step=0
        min_range = self.min_range
        max_range = self.max_range
        def helper(place,hive):
            nonlocal step
            if place is hive or step>max_range or place.entrance==None:
                return None
            elif step<min_range:
                step+=1
                return helper(place.entrance,hive)
            elif step>=min_range:
                if random_or_none(place.bees) == None:
                    step+=1
                    return helper(place.entrance,hive)
                else:
                    return random_or_none(place.bees)
        return helper(self.place,beehive)
        # END Problem 3 and 4

    def throw_at(self, target):
        """Throw a leaf at the TARGET Bee, reducing its armor."""
        if target is not None:
            target.reduce_armor(self.damage)

    def action(self, gamestate):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee(gamestate.beehive))

def random_or_none(s):
    """Return a random element of sequence S, or return None if S is empty."""
    assert isinstance(s, list), "random_or_none's argument should be a list but was a %s" % type(s).__name__
    if s:
        return random.choice(s)

##############
# Extensions #
##############

class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    implemented = True
    min_range = 0
    max_range = 3
    # Change to True to view in the GUI
    # END Problem 4

class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    implemented = True
    min_range = 5
    max_range = float('inf')
    # END Problem 4

class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True   # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, armor=3):
        """Create an Ant with an ARMOR quantity."""
        Ant.__init__(self, armor)

    def reduce_armor(self, amount):
        """Reduce armor by AMOUNT, and remove the FireAnt from its place if it
        has no armor remaining.

        Make sure to damage each bee in the current place, and apply the bonus
        if the fire ant dies.
        """
        # BEGIN Problem 5
        copy=list(self.place.bees)
        self.armor-=amount
        if self.armor>0:
            for element in copy:
                element.reduce_armor(amount)

        else:
            for element in copy:
                damage=self.damage+amount+self.armor
                element.reduce_armor(damage)
            Insect.reduce_armor(self,0)
                
            
        # END Problem 5

class HungryAnt(Ant):
    """HungryAnt will take three turns to digest a Bee in its place.
    While digesting, the HungryAnt can't eat another Bee.
    """
    name = 'Hungry'
    food_cost = 4
    time_to_digest=3
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 6
    implemented = True   # Change to True to view in the GUI
    # END Problem 6

    def __init__(self, armor=1):
        self.digesting=0
        Ant.__init__(self,armor)
        # END Problem 6

    def eat_bee(self, bee):
        # BEGIN Problem 6
        bee.reduce_armor(bee.armor)
        self.digesting=self.time_to_digest
        # END Problem 6

    def action(self, gamestate):
        if self.digesting==0 and random_or_none(self.place.bees):
            self.eat_bee(random_or_none(self.place.bees))
        elif self.digesting>0:
            self.digesting-=1
        # END Problem 6

class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    blocks_path=False
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 7
    implemented = True   # Change to True to view in the GUI
    # END Problem 7

    def action(self, gamestate):
        # BEGIN Problem 7\
        copy=list(self.place.bees)
        for bee in copy:
            bee.reduce_armor(self.damage)
        # END Problem 7

# BEGIN Problem 8
class WallAnt(Ant):
    name='Wall'
    food_cost=4
    implemented=True
    def __init__(self,armor=4):
        Ant.__init__(self,armor)
    
    
# END Problem 8

class ContainerAnt(Ant):
    def __init__(self, *args, **kwargs):
        Ant.__init__(self, 2, **kwargs)
        self.contained_ant = None

    def can_contain(self, other):
        # BEGIN Problem 9
        if self.contained_ant or isinstance(other,ContainerAnt):
            return False
        else:
            return True
        # END Problem 9

    def contain_ant(self, ant):
        # BEGIN Problem 9
        self.contained_ant=ant
        # END Problem 9

    def remove_ant(self, ant):
        if self.contained_ant is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.contained_ant = None

    def remove_from(self, place):
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.contained_ant
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate):
        # BEGIN Problem 9
        if self.contained_ant:
            self.contained_ant.action(gamestate)
        # END Problem 9

class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""

    name = 'Bodyguard'
    food_cost = 4
    def __init__(self,armor=2,can_contain=True):
        return ContainerAnt.__init__(self,armor,can_contain)
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 9
    implemented = True  # Change to True to view in the GUI
    # END Problem 9

class TankAnt(ContainerAnt):
    """TankAnt provides both offensive and defensive capabilities."""

    name = 'Tank'
    damage = 1
    food_cost = 6
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 10
    implemented = True  # Change to True to view in the GUI
    # END Problem 10

    def __init__(self, armor=2):
        ContainerAnt.__init__(self, armor)

    def action(self, gamestate):
        # BEGIN Problem 10
        copy=list(self.place.bees)
        for bee in copy:
            bee.reduce_armor(self.damage)
        if self.contained_ant:
            self.contained_ant.action(gamestate)
        # END Problem 10

class Water(Place):
    """Water is a place that can only hold watersafe insects."""

    def add_insect(self, insect):
        """Add an Insect to this place. If the insect is not watersafe, reduce
        its armor to 0."""
        # BEGIN Problem 11
        Place.add_insect(self,insect)
        if insect.is_watersafe==False:
            insect.reduce_armor(insect.armor)
        # END Problem 11

# BEGIN Problem 12
class ScubaThrower(ThrowerAnt):
    name= 'Scuba'
    is_watersafe=True
    food_cost=6
    implemented=True
# END Problem 12

# BEGIN Problem 13
class QueenAnt(ScubaThrower):  # You should change this line
# END Problem 13
    """The Queen of the colony. The game is over if a bee enters her place."""

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 13
    implemented = True
    is_queen=True
    # Change to True to view in the GUI
    # END Problem 13

    def __init__(self, armor=1):
        # BEGIN Problem 13
       ScubaThrower.__init__(self)
       self.is_queen = QueenAnt.is_queen
       self.doubled_ant=[]
       QueenAnt.is_queen = False
        # END Problem 13

    def action(self, gamestate):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.

        Impostor queens do only one thing: reduce their own armor to 0.
        """
        # BEGIN Problem 13
        if self.is_queen==False:
            Ant.reduce_armor(self,self.armor)
        else:
            ScubaThrower.action(self,gamestate)
            place=self.place.exit
            while place.exit:
                ant=place.ant
                if ant and ant not in self.doubled_ant:
                    ant.damage*=2
                    self.doubled_ant.append(ant)
                if isinstance(ant,ContainerAnt) and isinstance(ant.contained_ant,Ant) and ant.contained_ant not in self.doubled_ant:
                    ant.contained_ant.damage*=2
                    self.doubled_ant.append(ant.contained_ant)
                place=place.exit                    
            
        # END Problem 13
        

    def reduce_armor(self, amount):
        """Reduce armor by AMOUNT, and if the True QueenAnt has no armor
        remaining, signal the end of the game.
        """
        # BEGIN Problem 13
        self.armor-=amount
        if self.armor<=0:
            if self.is_queen:
                bees_win()
            else:
                self.place.remove_insect(self)
        # END Problem 13



class AntRemover(Ant):
    """Allows the player to remove ants from the board in the GUI."""

    name = 'Remover'
    implemented = False

    def __init__(self):
        Ant.__init__(self, 0)

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_watersafe=True
    right_direction=True


    def sting(self, ant):
        """Attack an ANT, reducing its armor by 1."""
        ant.reduce_armor(self.damage)

    def move_to(self, place):
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self):
        """Return True if this Bee cannot advance to the next Place."""
        # Phase 4: Special handling for NinjaAnt
        # BEGIN Problem 7
        return self.place.ant and self.place.ant.blocks_path
        # END Problem 7

    def action(self, gamestate):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination = self.place.exit
        # Extra credit: Special handling for bee direction
        # BEGIN EC
        
        # END EC
        if self.blocked():
            self.sting(self.place.ant)
        elif self.armor > 0 and destination is not None:
            if self.right_direction:
                self.move_to(destination)
            else:
                self.move_to(self.place.entrance)  

    def add_to(self, place):
        place.bees.append(self)
        Insect.add_to(self, place)

    def remove_from(self, place):
        place.bees.remove(self)
        Insect.remove_from(self, place)

##################
# Status Effects #
##################

def make_slow(action, bee):
    """Return a new action method that calls ACTION every other turn.

    action -- An action method of some Bee
    """
    # BEGIN Problem EC
    def action2(gamestate):
        if gamestate.time % 2 == 0:
            action(gamestate)
    return action2
    # END Problem EC

def make_scare(action, bee):
    """Return a new action method that makes the bee go backwards.

    action -- An action method of some Bee
    """
    # BEGIN Problem EC
    def action3(gamestate):
        action(gamestate)
    return action3       
    # END Problem EC

def apply_effect(effect, bee, duration):
    """Apply a status effect to a BEE that lasts for DURATION turns."""
    # BEGIN Problem EC
    old_action=bee.action
    new_action=effect(bee.action,bee)
    def action1(gamestate):
        nonlocal duration
        if duration == 0:
            bee.right_direction=True
            return old_action(gamestate)
        else:
            duration -= 1
            return new_action(gamestate)
    bee.action = action1 
        # END Problem EC


class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 4
    # BEGIN Problem EC
    implemented = True   # Change to True to view in the GUI
    # END Problem EC

    def throw_at(self, target):
        if target:
            apply_effect(make_slow, target, 3)


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC
    implemented = True   # Change to True to view in the GUI
    # END Problem EC

    def throw_at(self, target):
        # BEGIN Problem EC
        if target:
            target.right_direction=False
            apply_effect(make_scare,target,2)
            
        # END Problem EC

class LaserAnt(ThrowerAnt):
    # This class is optional. Only one test is provided for this class.

    name = 'Laser'
    food_cost = 10
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem OPTIONAL
    implemented = False   # Change to True to view in the GUI
    # END Problem OPTIONAL

    def __init__(self, armor=1):
        ThrowerAnt.__init__(self, armor)
        self.insects_shot = 0

    def insects_in_front(self, beehive):
        # BEGIN Problem OPTIONAL
        return {}
        # END Problem OPTIONAL

    def calculate_damage(self, distance):
        # BEGIN Problem OPTIONAL
        return 0
        # END Problem OPTIONAL

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front(gamestate.beehive)
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_armor(damage)
            if damage:
                self.insects_shot += 1


##################
# Bees Extension #
##################

class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2

class Hornet(Bee):
    """Class of bee that is capable of taking two actions per turn, although
    its overall damage output is lower. Immune to status effects.
    """
    name = 'Hornet'
    damage = 0.25

    def action(self, gamestate):
        for i in range(2):
            if self.armor > 0:
                super().action(gamestate)

    def __setattr__(self, name, value):
        if name != 'action':
            object.__setattr__(self, name, value)

class NinjaBee(Bee):
    """A Bee that cannot be blocked. Is capable of moving past all defenses to
    assassinate the Queen.
    """
    name = 'NinjaBee'

    def blocked(self):
        return False

class Boss(Wasp, Hornet):
    """The leader of the bees. Combines the high damage of the Wasp along with
    status effect immunity of Hornets. Damage to the boss is capped up to 8
    damage by a single attack.
    """
    name = 'Boss'
    damage_cap = 8
    action = Wasp.action

    def reduce_armor(self, amount):
        super().reduce_armor(self.damage_modifier(amount))

    def damage_modifier(self, amount):
        return amount * self.damage_cap/(self.damage_cap + amount)

class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees:
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)


class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    
    """
    
    def __init__(self, strategy, beehive, ant_types, create_places, dimensions, food=2):
        """Create an GameState for simulating a game.

        Arguments:
        strategy -- a function to deploy ants to places
        beehive -- a Hive full of bees
        ant_types -- a list of ant constructors
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.strategy = strategy
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        """Configure the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []
        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place, self.dimensions[0], self.dimensions[1])

    def simulate(self):
        """Simulate an attack on the ant colony (i.e., play the game)."""
        num_bees = len(self.bees)
        try:
            while True:
                self.strategy(self)                 # Ants deploy
                self.beehive.strategy(self)         # Bees invade
                for ant in self.ants:               # Ants take actions
                    if ant.armor > 0:
                        ant.action(self)
                for bee in self.active_bees[:]:     # Bees take actions
                    if bee.armor > 0:
                        bee.action(self)
                    if bee.armor <= 0:
                        num_bees -= 1
                        self.active_bees.remove(bee)
                if num_bees == 0:
                    raise AntsWinException()
                self.time += 1
        except AntsWinException:
            print('All bees are vanquished. You win!')
            return True
        except BeesWinException:
            print('The ant queen has perished. Please try again.')
            return False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        constructor = self.ant_types[ant_type_name]
        if self.food < constructor.food_cost:
            print('Not enough food remains to place ' + ant_type_name)
        else:
            ant = constructor()
            self.places[place_name].add_insect(ant)
            self.food -= constructor.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status

class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a BeesWinException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise BeesWinException()

def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()

def bees_win():
    """Signal that Bees win."""
    raise BeesWinException()

def ant_types():
    """Return a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]

class GameOverException(Exception):
    """Base game over Exception."""
    pass

class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass

class BeesWinException(GameOverException):
    """Exception to signal that the bees win."""
    pass

def interactive_strategy(gamestate):
    """A strategy that starts an interactive session and lets the user make
    changes to the gamestate.

    For example, one might deploy a ThrowerAnt to the first tunnel by invoking
    gamestate.deploy_ant('tunnel_0_0', 'Thrower')
    """
    print('gamestate: ' + str(gamestate))
    msg = '<Control>-D (<Control>-Z <Enter> on Windows) completes a turn.\n'
    interact(msg)

###########
# Layouts #
###########

def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)

def dry_layout(queen, register_place, tunnels=3, length=9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_armor, time, count):
        """Add a wave at time with count Bees that have the specified armor."""
        bees = [bee_type(bee_armor) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    @property
    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]
