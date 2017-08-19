#!/usr/bin/python
"""
 Requirements:
  * curses			included with python
  * pickle          included with python
  * random			included with python
  * sqlite3			included with python 2.5+
  * OpenSimplex 	pip install opensimplex

  TL;DR: Python 2.5+, pip install opensimplex

 A NOTE ABOUT COORDINATES:
  You will find four types of coordnates used here:
   * Screen coordinates  - 0,0 is the top,left corner of the chunk, and each
        step is a single character (column or line)
   * Absolute coordnates - 0,0 is the top,left corner of the chunk, and each
        step is determined by self.width, self.height
   * Relative coordnates - 0,0 is the center of the map (not limited to a single
        chunk), and each step is determined by self.width, self.height
        OBJECTS STORE x/y AS RELATIVE COORDINATES
   * Offset coordinates  - 0,0 is the current position, and each step is
        determined by self.width, self.height
        Useful for taking small steps (+/-1)
"""

import curses, pickle, sqlite3, time, random
from opensimplex import OpenSimplex

class Colors:
    BRIGHT_GRAY = 0
    DARK_WHITE = 0
    DARK_RED = 1
    DARK_GREEN = 2
    DARK_YELLOW = 3
    DARK_BLUE = 4
    DARK_MAGENTA = 5
    DARK_CYAN = 6
    DARK_BLACK = 7
    BLACK = 7
    BRIGHT_WHITE = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_BLACK = 15
    DARK_GRAY = 15

class InputValidation:
    def validate_int(self, val, name, minval=False, maxval=False):
        """
        Ensure a value is an integer and within the valid range (if specified)
         Returns the validated integer or throws an exception
        """
        if type(val) != type(int()):
            raise TypeError(str(name) + " is not type int (" + str(type(val)).split("'")[1] + ")")
        if type(minval) == type(int()):
            if val < minval:
                raise ValueError(str(name) + " < " + str(minval) + " (" + str(val) + ")")
        if type(maxval) == type(int()):
            if val > maxval:
                raise ValueError(str(name) + " > " + str(maxval) + " (" + str(val) + ")")
        return val

    def validate_str(self, val, name, blank=True):
        """
        Ensure a value is a string and non-blank (if specified)
         Returns the validated string or throws an exception
        """
        if type(val) != type(str()) and type(val) != type(u''):
            raise TypeError(str(name) + " is not type str (" + str(type(val)).split("'")[1] + ")")
        if blank == False and val == '':
            raise ValueError(str(name) + " == ''")
        return str(val)

    def validate_dict(self, val, name, mincount=False, maxcount=False):
        """
        Ensure a value is a dictionary and the count of entries is withing the valid range (if specified)
         Returns the validated dictionary or throws an exception
        """
        if type(val) != type({}):
            raise TypeError(str(name) + " is not type dict (" + str(type(val)).split("'")[1] + ")")
        if type(mincount) == type(int()):
            if len(val) < mincount:
                raise ValueError(str(name) + " len() < " + str(mincount) + " (" + str(len(val)) + ")")
        if type(maxcount) == type(int()):
            if len(val) > maxcount:
                raise ValueError(str(name) + " len() > " + str(maxcount) + " (" + str(len(val)) + ")")
        return val

    def validate_list(self, val, name, mincount=False, maxcount=False):
        """
        Ensure a value is a list and the count of entries is withing the valid range (if specified)
         Returns the validated list or throws an exception
        """
        if type(val) != type([]):
            raise TypeError(str(name) + " is not type list (" + str(type(val)).split("'")[1] + ")")
        if type(mincount) == type(int()):
            if len(val) < mincount:
                raise ValueError(str(name) + " len() < " + str(mincount) + " (" + str(len(val)) + ")")
        if type(maxcount) == type(int()):
            if len(val) > maxcount:
                raise ValueError(str(name) + " len() > " + str(maxcount) + " (" + str(len(val)) + ")")
        return val

    def validate_tup(self, val, name, mincount=False, maxcount=False):
        """
        Ensure that a value is a tuple and the count of enties is within the
         range (if specified)
         Returns the validated tuple or throws an exception
        """
        if type(val) != type(()):
            raise ValueError(str(name) + " is not type tuple (" + str(type(val)).split("'")[1] + ")")
        if len(val) > maxcount:
            raise ValueError(str(name) + " len() > " + str(maxcount))
        if len(val)  < mincount:
            raise ValueError(str(name) + " len() < " + str(mincount))
        return val

    def validate_win(self, win, name, falseok=False):
        """
        Ensure that a value is a curses window,
         or optionally evaluates to False (falseok=True)
        """
        if falseok and win == False:
            return win
        if str(type(win)) != "<type '_curses.curses window'>":
            raise TypeError(str(name) + " is not a Curses window (" + str(type(val)).split("'")[1] + ")")
        return win

    def validate_smp(self, val, name):
        """
        Ensure that a value is an OpenSimplex object
        """
        if str(type(val)) != "<class 'opensimplex.opensimplex.OpenSimplex'>":
            raise TypeError(str(name) + " is not an OpenSimplex object (" + str(type(val)).split("'")[1] + ")")
        return val

    def validate_worldset(self, val, name):
        """
        Ensure that a value is a TwoDimWorldSettings object
        """
        if str(type(val)) != "<type 'instance'>":
            raise TypeError(str(name) + " is not a TwoDimWorldSettings object (" + str(type(val)).split("'")[1] + ")")
        else:
            if str(type(val)).split("'")[1] == "instance" and val.__class__.__name__ == "TwoDimWorldSettings":
                return val
            else:
                raise TypeError(str(name) + " is not a TwoDimWorldSettings object (" + str(type(val)).split("'")[1] + " " + val.__class__.__name__ +  ")")
        return val

    def validate_db(self, val, name):
        """
        Ensure that a value is a sqlite3 Connection OR that it's a bool (disabled)
        """
        if str(type(val)) != "<type 'sqlite3.Connection'>" and type(val) != type(bool()):
            raise TypeError(str(name) + " is not a sqlite3 Connection (" + str(type(val)).split("'")[1] + ")")
        return val

    def validate_dbcur(self, val, name):
        """
        Ensures a value is a sqlite3 db cursor OR that it's a bool (disabled)
        """
        if str(type(val)) != "<type 'sqlite3.Cursor'>" and type(val) != type(bool()):
            raise TypeError(str(name) + " is not a sqlite3 Cursor (" + str(type(val)).split("'")[1] + ")")
        return val

class TwoDimCommon(InputValidation):
    # self.xoffset = int(worldset.chunksize / 2)
    # self.yoffset = int(worldset.chunksize / 2)

    ## YOU MUST SET xoffset AND yoffset IN __init__() USING ABOVE FORMULA ##
    ######## THIS APPLIES TO ALL OBJECTS THAT SUBCLASS TwoDimCommon ########
    # TODO: Put this in __init__()

    def debug(self, text):
        """
        Write the text to the curses window 'self.world.debugwin', followed by
         a newline. Only adds text if 'self.world.debugwin' is a curses window
        """
        # Check and see if we have a curses window
        if str(type(self.world.debugwin)) == "<type '_curses.curses window'>":
            # Add the text to the window, along with a newline
            self.world.debugwin.addstr(str(text) + "\n")
            # Refresh the window to update the screen
            self.world.debugwin.refresh()

    def abs2rel(self, x, y):
        """
        Returns a tuple of (x, y) where x and y are adjusted
         from Absolute coordinates  (0,0=top,left and each step is (self.width) or (self.height) characters)
         to Relative Coordinates    (0,0=center and each step is (self.width) or (self.height) characters)
        """
        # self.debug("abs2rel(" + str(x) + "," + str(y) + ") = " + str(x-self.xoffset) + "," + str(y-self.yoffset) + " (" + str(getattr(self, 'chunksize', self.world.chunksize)) + ")")
        x, y = self.validate_abs(x, y)
        x = x - self.xoffset
        y = y - self.yoffset
        return (x, y)

    def rel2abs(self, x, y):
        """
        Returns a tuple of (x, y) where x and y are adjusted
         from Relative Coordinates  (0,0=center and each step is (self.width) or (self.height) characters)
         to Absolute coordinates    (0,0=top,left and each step is (self.width) or (self.height) characters)
        """
        # self.debug("rel2abs(" + str(x) + "," + str(y) + ") = " + str(x+getattr(self, 'xoffset', 0)) + "," + str(y+getattr(self, 'yoffset', 0)) + " (" + str(getattr(self, 'chunksize', self.world.chunksize)) + ")")
        x, y = self.validate_rel(x, y)
        x = x + self.xoffset
        y = y + self.yoffset
        return (x, y)

    def rel2screen(self, x, y):
        """
        Returns a tuple of (x, y) where x and y are adjusted
         from Relative Coordinates  (0,0=center and each step is (self.width) or (self.height) characters)
         to Screen Coordinates      (0,0=top,left and each step is 1 character)
        """
        x, y = self.validate_rel(x, y)
        x, y = self.rel2abs(x, y)
        x, y = self.abs2screen(x, y)
        return (x, y)

    def abs2screen(self, x, y):
        """
        Returns a tuple of (x,y) where x and y are adjusted
         from Absolute coordinates  (0,0=top,left and each step is (self.width) or (self.height) characters)
         to Screen Coordinates      (0,0=top,left and each step is 1 character)
        """
        x = self.validate_int(x, 'x', 0, self.world.chunksize)
        y = self.validate_int(y, 'y', 0, self.world.chunksize)
        x = x * self.world.height
        y = y * self.world.width
        return (x, y)

    def screen2abs(self, x, y):
        """
        Returns a tuple of (x,y) where x and y are adjusted
         from Screen Coordinates    (0,0=top,left and each step is 1 character)
         to Absolute coordinates    (0,0=top,left and each step is (self.width) or (self.height) characters)
        """
        x = self.validate_int(x, 'x', 0, self.world.chunksize)
        y = self.validate_int(y, 'y', 0, self.world.chunksize)
        x = x / self.world.height
        y = y / self.world.width
        return (x, y)

    def color2attr(self, color):
        "Returns a Curses attribtue value from an internal color value"
        # Valid colors are 0-7 (8)
        ret = curses.color_pair(color % 8)
        # If the color value was > 7, it must be bright (bold)
        if color > 7:
            ret = ret | curses.A_BOLD
        return ret

    def validate_rel(self, x, y):
        """
        Ensures that a set of x,y coordinates are valid RELATIVE coordinates
         Returns a tuple containing the validated coordinates or raises an exception
        """
        if type(x) != type(int()):
            raise TypeError('x is not type int (' + str(type(x)).split("'")[1] + ")")
        if type(y) != type(int()):
            raise TypeError('y is not type int (' + str(type(y)).split("'")[1] + ")")
        # Relative coordinates are no longer limited in scope to a single chunk
        #  so as long as they pass  the integer test, they are good ot go
        return (x, y)

    def validate_abs(self, x, y):
        """
        Ensures that a set of x,y coordinates are valid ABSOLUTE coordinates
         Returns a tuple containing the validated coordinates or raises an exception
        """
        # self.debug("validate_abs(" + str(x) + ", " + str(y) + ")")
        if type(x) != type(int()):
            raise TypeError('x is not type int (' + str(type(x)).split("'")[1] + ")")
        if type(y) != type(int()):
            raise TypeError('y is not type int (' + str(type(y)).split("'")[1] + ")")
        if x < 0:
            raise ValueError("x < 0 (" + str(x) + ")")
        if x > self.world.chunksize - 1:
            raise ValueError("x > " + str(self.world.chunksize - 1) + " (" + str(x) + ")")
        if y < 0:
            raise ValueError("y < 0 (" + str(y) + ")")
        if y > self.world.chunksize - 1:
            raise ValueError("y > " + str(self.world.chunksize - 1) + " (" + str(y) + ")")
        return (x, y)

    def db2object(self, record, chunkX, chunkY):
        """
        Returns a TwoDimObject from a previously unpickled db record
        """
        # self.debug("db2object: " + str(record[1]) + ", " + str(record[2]))
        return TwoDimObject(self.world,
                            objid=self.validate_int(record[0], 'objid', minval=0),
                            x=self.validate_int(record[1], 'x'),
                            y=self.validate_int(record[2], 'y'),
                            chunkX=self.validate_int(record[3], 'chunkX'),
                            chunkY=self.validate_int(record[4], 'chunkY'),
                            icon=self.validate_str(record[5], 'icon', blank=False),
                            width=self.validate_int(record[6], 'width', minval=0, maxval=self.world.chunksize),
                            height=self.validate_int(record[7], 'height', minval=0, maxval=self.world.chunksize),
                            color=self.validate_int(record[8], 'color'))

    def db2moveable(self, record, painter, win, chunkX, chunkY):
        """
        Returns a TwoDimMoveable from a previously unpickled db record
        """
        return TwoDimMoveable(  self.world,
                                painter,
                                self.validate_win(win, 'win'),
                                objid=self.validate_int(record[0], 'objid', minval=0),
                                x=self.validate_int(record[1], 'x'),
                                y=self.validate_int(record[2], 'y'),
                                chunkX=self.validate_int(record[3], 'chunkX'),
                                chunkY=self.validate_int(record[4], 'chunkY'),
                                icon=self.validate_str(record[5], 'icon', blank=False),
                                width=self.validate_int(record[6], 'width', minval=0, maxval=self.world.chunksize),
                                height=self.validate_int(record[7], 'height', minval=0, maxval=self.world.chunksize),
                                color=self.validate_int(record[8], 'color'))

class TwoDimWorldSettings(InputValidation):
    def __init__(self,
        seed=1234567890,
        chunksize=9,
        # Marker settings
        defmarker='#',
        defcolor=Colors.DARK_GREEN,
        markermap={1:'#'},
        colormap={1,Colors.DARK_GREEN},
        width=2,
        height=1,
        debugwin=False,
        db=False,
        c=False):
        "Stores the settings for a two-dimensional world"
        # Validate and store the settings
        # Validate debugwin first so that everything else can access it
        self.debugwin = self.validate_win(debugwin, 'debugwin', falseok=True)
        self.seed = self.validate_int(seed, 'seed')
        self.chunksize = self.validate_int(chunksize, 'chunksize', minval=1)
        self.defmarker = self.validate_str(defmarker, 'defmarker', blank=False)
        self.defcolor = self.validate_int(defcolor, 'defcolor', minval=0)
        self.markermap = self.validate_dict(markermap, 'markermap', mincount=1)
        self.colormap = self.validate_dict(colormap, 'colormap', mincount=1)
        self.width = self.validate_int(width, 'width', minval=1, maxval=chunksize)
        self.height = self.validate_int(height, 'height', minval=1, maxval=chunksize)
        # TODO: Update all the db stuff to use self.db and self.c
        self.db = self.validate_db(db, 'db')
        self.c = self.validate_dbcur(c, 'c')

class TwoDimWorld(TwoDimCommon):
    def __init__(self, simplexobj, worldsettings):
        # Set this before we do ANYTHING so that if possible we have a debug window
        self.smp = self.validate_smp(simplexobj, 'simplexobj')
        self.world = self.validate_worldset(worldsettings, 'worldsettings')

    def genchunk(self, chunkX, chunkY, replace=False):
        """
        Generates a new chunk, adds it to the database, and returns the chunk data
        """
        dataset = []

        # Check and see if this chunk is already in the database
        count = self.chunksindb(chunkX, chunkY)
        if count > 0 and replace == False:
            return self.loadchunk(chunkX, chunkY)

        # EITHER count == 0 OR replace == True, so we need to generate a new chunk
        # Generate the dataset
        # self.debug("Generating new chunk data for " + str(chunkX) + ", " + str(chunkY))
        i = 0
        for x in range(chunkX * self.world.chunksize, (chunkX * self.world.chunksize) + self.world.chunksize):
            dataset.append([])
            for y in range(chunkX * self.world.chunksize, (chunkX * self.world.chunksize) + self.world.chunksize):
                dataset[i].append(self.smp.noise2d(x=x,y=y))
            i += 1

        if count > 0 and replace == True:
            self.world.c.execute("DELETE FROM chunks WHERE x=" + str(chunkX) + " and y=" + str(chunkY))
            self.world.db.commit()
        if count == 0 or replace == True:
            self.world.c.execute("INSERT INTO chunks (x, y, data) VALUES (" + str(chunkX) +  ", " + str(chunkY) + ", " + "'" + pickle.dumps(dataset) + "'" + ")")
            self.world.db.commit()
        return dataset

    def chunksindb(self, chunkX, chunkY):
        """
        Returns the number of chunks in the database for chunkX,chunkY
        """
        self.world.c.execute("SELECT * FROM chunks WHERE x=" + str(chunkX) + " and y=" + str(chunkY))
        records = self.world.c.fetchall()
        return len(records)

    def loadchunk(self, chunkX, chunkY, loadneighbors=True):
        """
        Loads a chunk from the database and returns the chunk dataset
        If the chunk does not exist in the database, a new one is generated
        If loadneighbors == True (defaut) it will also generate any missing chunks
         in a 3x3 grid surrounding the specified chunk
        """
        # self.debug("LOADCHUNK(" + str(chunkX) + ", " + str(chunkY) + ")")
        if loadneighbors:
            # load  the neighboring chunks, x/y -1, 0, +1 -- but range() skips the last value so we do +2
            for x in range(chunkX - 1, chunkX + 2):
                for y in range(chunkY - 1, chunkY + 2):
                    # attempt to load  the chunk so that any that don't exist are created
                    dataset = self.loadchunk(x, y, loadneighbors=False)

        self.world.c.execute("SELECT * FROM chunks WHERE x=" + str(chunkX) + " and y=" + str(chunkY))
        records = self.world.c.fetchall()
        if len(records) < 1:
            dataset = self.genchunk(chunkX, chunkY)
        else:
            dataset = pickle.loads(records[0][2])
        return dataset

class TwoDimChunk(TwoDimCommon):
    def __init__(self, dataset, world, chunkX=0, chunkY=0):
        "A two-dimensional chunk of the game world"
        self.world = world
        # Validate and set dataset
        self.dataset = self.validate_list(dataset, 'dataset', mincount=self.world.chunksize, maxcount=self.world.chunksize)
        self.dataset[0] = self.validate_list(dataset[0], 'dataset', mincount=self.world.chunksize, maxcount=self.world.chunksize)
        # Validate and set chunkX
        self.chunkX = self.validate_int(chunkX, 'chunkX')
        # Validate and set chunkY
        self.chunkY = self.validate_int(chunkY, 'chunkY')

class TwoDimDrawing(TwoDimCommon):
    def __init__(self, worldsettings):
        "Handles drawing onto curses windows of two-dimensional chunks and objects"
        self.world = worldsettings
        # TODO: Use superclass constructor instead to set xoffset/yoffset
        self.xoffset = int(worldsettings.chunksize / 2)
        self.yoffset = int(worldsettings.chunksize / 2)


    def drawchunk(self, chunkX, chunkY, win, xoffset=0, yoffset=0, drawobjs=True):
        """
        Draws the chunk specified by chunkX,chunkY onto curses window win
         Also draws objects located on same chunk, unless drawobjs == False
        """
        # Validate params
        chunkX = self.validate_int(chunkX, 'chunkX')
        chunkY = self.validate_int(chunkY, 'chunkY')
        win = self.validate_win(win, 'win')
        xoffset, yoffset = self.validate_rel(xoffset, yoffset)
        self.world.c.execute("SELECT data FROM chunks WHERE x=" + str(chunkX) + " AND y=" + str(chunkY))
        records = self.world.c.fetchall()
        if len(records) < 1:
            raise ValueError("Chunk " + str(chunkX) + "," + str(chunkY) + " not found in database")
        dataset = pickle.loads(records[0][0])
        win.clear()
        for x in range(self.world.chunksize):
            for y in range(self.world.chunksize):
                self.drawmarker(dataset, win, x, y, xoffset, yoffset, refresh=False)
        self.world.c.execute("SELECT rowid,* FROM objects")
        records = self.world.c.fetchall()
        if len(records) > 0:
            # self.debug("There are " + str(len(records)) + " objects to be displayed")
            for rec in records:
                # self.debug("RECORD: " + str(rec))
                self.drawobjectfromrecord(rec, chunkX, chunkY, win, xoffset, yoffset, refresh=False)
        win.refresh()

    def eraseobject(self,objid, dataset, win, x, y, chunkX=0, chunkY=0, xoffset=0, yoffset=0, refresh=True):
        # TODO: Data validation, documentation
        # REMOVE? Pretty sure we're not using this
        #  at least TEST it...
        self.world.c.execute("SELECT rowid,* FROM objects WHERE rowid IS NOT " + str(objid) + " AND x=" + str(x) + " AND y=" + str(y))
        records = self.world.c.fetchall()
        if len(records):
            self.drawobjectfromrecord(records[-1], chunkX, chunkY, win, xoffset, yoffset, refresh)
        else:
            self.drawmarker(dataset, win, x, y, xoffset, yoffset, refresh)

    def drawmarker(self, dataset, win, x, y, xoffset=0, yoffset=0, refresh=True):
        """
        Draws and colors the (terrain) marker from dataset onto window win
         located at x,y in dataset. xoffset,yoffset adjust the position of x,y
         BEFORE it is converted to screen coords. When refresh==True the window
         will be refreshed at the end
        """
        relx, rely = self.validate_rel(x + xoffset, y + yoffset)
        scrx, scry = self.abs2screen(relx, rely)
        win.addstr(scrx, scry, self.getmarker(x,y,dataset)*self.world.width)
        win.chgat(scrx, scry, self.world.width, self.getcolor(x,y,dataset))
        if refresh:
            win.refresh

    def drawobjectfromrecord(self, rec, chunkX, chunkY, win, xoffset=0, yoffset=0, refresh=True):
        """
        Draws an object from an (depickled) object record
         chunkX,chunkY are a necessary evil at this moment as they are required
         to construct a new TwoDimObject/TwoDimMoveable
        """
        # Validate the incoming record
        rec = self.validate_tup(rec, 'rec', mincount=9, maxcount=9)
        # Convert it into a TwoDimObject
        obj = self.db2object(rec, chunkX, chunkY)
        # Determine our screen coordinates, taking into account any x/y offset prior to coversion
        scrx, scry = self.rel2screen(obj.x + xoffset, obj.y + yoffset)
        # Draw tbe icon on the screen, making it the appropriate width
        win.addstr(scrx, scry, obj.icon*obj.width)
        # Change the color of the icon on the screen
        win.chgat(scrx, scry, obj.width, self.color2attr(obj.color))
        # Regfresh the screen/window, but only if requested
        if refresh:
            win.refresh()

    def drawlocation(self, win, chunkX, chunkY, x, y, xoffset=0, yoffset=0, refresh=True):
        """
        Draws the chunk terrain or top-most object located at the specified
         coordinates
        """
        # TODO: Objects need chunkX and chunkY
        #        or do we just calculate it from x,y? That seems cleaner
        # self.debug("DRAWLOCATION(" + str(x) + "," + str(y) + ")")
        x, y = self.validate_abs(x, y)
        self.world.c.execute("SELECT data FROM chunks WHERE x=" + str(chunkX) + " AND y=" + str(chunkY))
        records = self.world.c.fetchall()
        if len(records) < 1:
            raise ValueError("Chunk " + str(chunkX) + "," + str(chunkY) + " not found in database")
        dataset = pickle.loads(records[0][0])
        relx, rely = self.abs2rel(x, y)
        self.world.c.execute("SELECT rowid,* FROM objects WHERE x=" + str(relx) + " AND y=" + str(rely))
        records = self.world.c.fetchall()
        if len(records) > 0:
            # self.debug("There are " + str(len(records)) + " objects to be displayed (DRAWLOCATION)")
            for rec in records:
                self.drawobjectfromrecord(rec, chunkX, chunkY, win, xoffset, yoffset, refresh=False)
                if refresh:
                    win.refresh()
        else:
            self.drawmarker(dataset, win, x, y, xoffset, yoffset, refresh=refresh)

    def getval(self, x, y, dataset):
        "Returns the terrain value at the absolute x,y coordinates"
        x = self.validate_int(x, 'x', minval=0, maxval=self.world.chunksize)
        y = self.validate_int(y, 'y', minval=0, maxval=self.world.chunksize)
        # Adjust terrval to be ABOVE zero, and then scale to be between 0 and 1
        terrval = dataset[x][y] + 1
        terrval *= .5
        # Calculate the size of the slices each type of terrain will be
        offset = 1.0 / len(self.world.markermap)
        # Determine which color we're using
        ret  = int(terrval / offset) + 1
        return ret

    def getmarker(self, x, y, dataset):
        "Returns the marker located at the absolute x,y coordinates"
        x = self.validate_int(x, 'x', minval=0, maxval=self.world.chunksize)
        y = self.validate_int(y, 'y', minval=0, maxval=self.world.chunksize)
        terr = self.getval(x,y, dataset)
        if not self.world.markermap.has_key(terr):
            return self.world.defmarker
        else:
            return self.world.markermap[terr]

    def getcolor(self, x, y, dataset):
        "Returns the curses color pair of the marker located at the absolute x,y coordinates"
        x = self.validate_int(x, 'x', minval=0, maxval=self.world.chunksize)
        y = self.validate_int(y, 'y', minval=0, maxval=self.world.chunksize)
        terr = self.getval(x, y, dataset)
        if self.world.colormap.has_key(terr):
            ret = self.world.colormap[terr]
        else:
            # Use default color
            ret = self.world.defcolor
            #debug("Failed to find color for terrain value " + str(terr))
        return self.color2attr(ret)

class TwoDimObject(TwoDimCommon):
    # RELATIVE COORDINATES
    def __init__(self, worldset, chunkX=0, chunkY=0, objid=1, x=0, y=0, icon='@', width=0, height=0, color=Colors.BRIGHT_RED):
        # TODO: Validate
        self.world = worldset
        # self.debug("Creating object " + icon + " at " + str(x) + ", " + str(y))
        # Validate and set the object id (database record number)
        self.objid = self.validate_int(objid, 'objid', minval=1)
        # Set the world settings
        # Update the x/y offsets for the relative coordinates (within the chunk) to the new chunksize
        self.xoffset = int(self.world.chunksize / 2)
        self.yoffset = int(self.world.chunksize / 2)
        # Validate and set the coordinates of the chunk
        self.chunkX = self.validate_int(chunkX, "chunkX")
        self.chunkY = self.validate_int(chunkY, "chunkY")
        # Make sure x and y are integers
        self.x, self.y = self.validate_rel(x, y)

        # Validate and set icon character
        self.icon = self.validate_str(icon, 'icon', blank=False)
        # Validate and set color value
        self.color = self.validate_int(color, 'color', minval=0)
        # Check for default width and height
        if width == 0:
            width = self.world.width
        if height == 0:
            height = self.world.height
        # Validate and set the width and height
        self.width = self.validate_int(width, 'width', minval=1, maxval=self.world.chunksize)
        self.height = self.validate_int(height, 'height', minval=1, maxval=self.world.chunksize)

class TwoDimMoveable(TwoDimObject):
    # RELATIVE COORDINATES
    def __init__(self,
                 worldset,
                 painter,
                 win,
                 chunkX=0,
                 chunkY=0,
                 objid=1,
                 x=0,
                 y=0,
                 icon='@',
                 width=0,
                 height=0,
                 color=Colors.BRIGHT_RED):
        TwoDimObject.__init__(self, worldset, chunkX, chunkY, objid, x, y, icon, width, height, color)
        # TODO: Fix other subclasses to call super-class constructors for common things like setting x/yoffset and debugwin
        # TODO: validate
        self.painter = painter
        self.win = self.validate_win(win, 'win')

    def write2db(self):
        self.world.c.execute("SELECT rowid FROM objects WHERE rowid=" + str(self.objid))
        records = self.world.c.fetchall()
        if len(records) > 0:
            self.world.c.execute("UPDATE objects SET x=" + str(self.x) + ", y=" + str(self.y) + ", chunkX=" + str(self.chunkX) + ", chunkY=" + str(self.chunkY) + ", icon=" + "'" + self.icon + "'" + ", width=" + str(self.width) + ", height=" + str(self.height) + ", color=" + str(self.color)  + " WHERE rowid=" + str(self.objid) )
        else:
            self.world.c.execute("INSERT INTO objects (x, y, chunkX, chunkY, icon, width, height, color) VALUES (" + str(self.x) + ", " + str(self.y) + ", " + str(self.chunkX) + ", " + str(self.chunkY) + ", " + self.icon + ", " + str(self.width) + ", " + str(self.height) + ", " + str(self.color) + ")")
        # self.debug("Wrote object " + self.icon + " at " + str(self.x) + ", " + str(self.y) + " to the database")
        self.world.db.commit()

    def move(self, newX, newY):
        "Pretty alias for moverelative()"
        self.moverelative(newX, newY)

    def moveabsolute(self, newX, newY):
        "Move object to a new position using absolute coordinates x,y"
        # Convert the absolute coordinates to relative
        #  the reason we do this before the validation is so the debug displays regardless
        relx, rely = self.abs2rel(newX, newY)
        # self.debug("Moving object " + self.icon + " to absolute coordinates " + str(newX) + "," + str(newY) + " (" + str(relx) + "," + str(rely) + ")")

        # Validate new X and Y values
        newX, newY = self.validate_abs(newX, newY)

        if  relx != self.x or rely != self.y:
            # Save the old x,y so we can redraw the screen in that location
            oldabsx, oldabsy = self.rel2abs(self.x, self.y)
            # Update the x,y for the object
            self.x = relx
            self.y = rely
            # Update the database
            self.write2db()
            # Repaint the relevant portions of the screen
            self.painter.drawlocation(self.win, self.chunkX, self.chunkY, oldabsx, oldabsy, refresh=True)
            self.painter.drawlocation(self.win, self.chunkX, self.chunkY, newX, newY, refresh=True)

    def moverelative(self, newX, newY):
        "Move object to a new position using relative coordinates x,y"
        absx, absy = self.rel2abs(newX, newY)
        # self.debug("Moving object " + self.icon + " to relative coordinates " + str(newX) + "," + str(newY) + " (" + str(absx) + "," + str(absy) + ")")
        self.moveabsolute(absx, absy)

    def moveoffset(self, offsetX, offsetY):
        "Move object to a new position using offset coordinates x,y"
        absx, absy = self.rel2abs(self.x + offsetX, self.y + offsetY)
        # self.debug("moveoffset(" + str(offsetX) + "," + str(offsetY) + ") = " + str(absx) + "," + str(absy))
        self.moveabsolute(absx, absy)
