# Distributed under the terms of the GNU GPLv3
# Copyright 2010 Berin Smaldon
import re # Use this for getItem

# The Universal Object class
class BerinObject:
    # Mostly define attributes that everything needs to have
    def __init__(self, world, loc, **attribs):
        if 'id' in attribs.keys():
            self.ident = int(attribs['id'])
            del attribs['id'] # Don't store that
        else:
            self.ident = world.getNewID()
        self.world = world
        self.loc = loc
        self.attributes = attribs
        self.contents = [ ]

        world.register(self)
    
    def getID(self):
        return self.ident

    def display(self, text):
        pass

    def moveTo(self, newLoc):
        if self.loc:
            self.loc.removeItem(self)
        self.loc = newLoc
        if self.loc:
            self.loc.pushItem(self)

    def hasItem(self, item):
        if type(item) != int:
            item = item.getID()
        return (item in [i.getID() for i in self.contents])

    def pushItem(self, newItem):
        self.contents.append(newItem)

    def removeItem(self, toRemove):
        self.contents.remove(toRemove)

    def setAttribute(self, attr, value):
        """Set the attribute attr to value."""
        
        self.attributes[attr] = value

    def getAttribute(self, attr):
        """Get the attribute attr, or None if it does not exist."""
        
        #try:
        #    return self.attributes[attr]
        #except KeyError:
        #    return None
        return self.attributes.get(attr, None)
    
    def getAllAttributes(self):
        """Get the dictionary of attributes."""
        
        return self.attributes

    def delAttribute(self, attr):
        if attr in self.attributes.keys():
            del self.attribues[attr]

    def getWorld(self):
        """Returns the world the object is in."""
        return self.world

    def getLocation(self):
        return self.loc

    def renderExits(self):
        return "There are no exits here"

    def renderContents(self):
        if len(self.contents) > 0:
            return "Items here: " + \
            ", ".join([i.getAttribute('oshort') for i in self.contents])
        else:
            return "No items here"

    def hasExit(self, exit):
        return False

    def addExit(self, exit, destination):
        pass
    
    def delExit(self, exit):
        pass

    def getContents(self):
        return self.contents

    def getItemMatches(self, identifier):
        """Returns a list of items in this item whose names match the
        given identifier."""

        result = []

        p = re.compile(identifier)
        for i in self.contents:
            if p.match(i.getAttribute('oshort')):
                result.append(i)

        return result
    
    def getItem(self, identifier, n=None):
        n = n or "1"
        try:
            n = int(n)
        except ValueError:
            return None
        if n < 1:
            return None

        p = re.compile(identifier)
        for i in self.contents:
            if p.match(i.getAttribute('oshort')):
                    n -= 1
                    if n <= 0:
                        return i

        return None

    # Display text to all other objects in location
    def emit(self, text):
        if self.loc:
            self.loc.show(text, fltr=[self])

    # Show text to objects in location, configurable
    # TODO: Add more functionality
    def show(self, text, **kwargs):
        for i in self.contents:
            if i not in kwargs.get('fltr',[]):
                i.display(text)

# The Room class, only slightly different to the  Object class
class Room(BerinObject):
    def __init__(self, world, loc, **attribs):
        self.exits = { }
        BerinObject.__init__(self, world, loc, **attribs)
        world.registerRoom(self)

    def renderExits(self):
        return ", ".join(self.exits.keys())
    
    def addExit(self, exit, destination):
        self.exits[exit] = destination
        
    def setExits(self, exitdict):
        """Replace the dictionary of room exits with the given dictionary.
        
        This should only be done when the current exit dictionary is empty.
        """
        
        assert len(self.exits) == 0
        
        self.exits = exitdict

    def hasExit(self, exit):
        return (exit in self.exits.keys())
    
    def delExit(self, exit):
        del self.exits[exit]

    def getExit(self, exit):
        #print self.exits
        return self.exits.get(exit, None)

# Objects that represent the players, mostly they just need to be tired to
# an appropriate connection class, but None should be supported for
# link-dead clients.
class Puppet(BerinObject):
    def __init__(self, world, loc, **attribs):
        self.client = None
        self._quitFlag = 0
        BerinObject.__init__(self, world, loc, **attribs)
        world.registerPuppet(self)

    def display(self, text):
        if self.client != None:
            self.client.sendLine(text)

    def registerClient(self, newClient):
        assert self.client == None, \
                "Tried to assign client to active puppet"
        self.client = newClient

    def deregisterClient(self):
        self.client = None

    def forceQuit(self, qFlag=None):
        self._quitFlag = qFlag or self._quitFlag
        self.client.transport.loseConnection()

# Item type list, please keep up to date:
itemTypes = [
        BerinObject,
        Room,
        Puppet,
]
