#!/usr/bin/python
"""
 Requirements:
  * curses			included with python
  * pickle          included with python
  * random			included with python
  * sqlite3			included with python 2.5+
  * OpenSimplex 	pip install opensimplex

  TL;DR: Python 2.5+, pip install opensimplex
"""
import curses, random, solar, sqlite3, pickle, time
from solar import Colors
from opensimplex import OpenSimplex

DBFILE = "solar.db"

worldset = solar.TwoDimWorldSettings(
    chunksize=21,
    defmarker='#',
    defcolor=Colors.DARK_GREEN,
    #markermap={1:'#', 2:'#', 3:'#'},
    markermap={1:'~', 2:'.', 3:'o'},
    colormap={1:Colors.BRIGHT_BLUE, 2:Colors.DARK_GREEN, 3:Colors.DARK_GRAY},
    width=2,
    height=1)

## DEBUG?
SHOWDEBUG = True
debugwin = "" # Needs an initial value if we intend to use it as a global

def main(stdscr):
    "Main program"
    global debugwin

    # Find out the dimensions of our main winow
    w = stdscr.getmaxyx()[1]
    h = stdscr.getmaxyx()[0]

    # Make sure the terrain window fits on the screen
    maxsize = h - 1
    if (w - 2) < ( worldset.width *  worldset.chunksize):
        maxsize = int((w - 2) /  worldset.width)
    if maxsize <  worldset.chunksize:
         worldset.chunksize = maxsize

    # Set up our color pairs
    # curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK) # IMO this should be black, but curses wont let me init it, so it's now white...
    curses.init_pair(Colors.DARK_RED, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(Colors.DARK_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(Colors.DARK_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(Colors.DARK_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(Colors.DARK_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(Colors.DARK_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(Colors.BLACK, curses.COLOR_BLACK, curses.COLOR_BLACK)

    # Create the window to show the debug messages
    if SHOWDEBUG:
        debugwin = stdscr.derwin(h - 1 - ( worldset.chunksize + 1), w - 1,  worldset.chunksize + 1, 0)
        debugwin.scrollok(True)
        debugwin.idlok(1)
        worldset.debugwin = debugwin

    # We can't show this any earlier, the debug window hasn't been created yet
    debug("Program started")

    # Create the window to display the terrain
    terrwin = stdscr.derwin( worldset.chunksize + 1, ( worldset.chunksize + 1) *  worldset.width, 0, 0) # Top-left

    # Seed the random number generator
    random.seed()

    # Connect to the database
    db = sqlite3.connect(DBFILE)
    c = db.cursor()
    worldset.db = db
    worldset.c = c

    # Set up the database
    c.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name='chunks'")
    tables = c.fetchall()
    if len(tables) < 1:
        # debug("Creating chunks table")
        c.execute('''CREATE TABLE IF NOT EXISTS chunks
    			     (x INTEGER, y INTEGER, data TEXT)''')
    c.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name='objects'")
    tables = c.fetchall()
    if len(tables) < 1:
        # debug("Creating objects table")
        c.execute('''CREATE TABLE IF NOT EXISTS objects
    			     (x INTEGER, y INTEGER, chunkX INTEGER, chunkY INTEGER, icon TEXT, width INTEGER, height INTEGER, color INTEGER)''')

    # Set up the world
    smp = OpenSimplex(seed=worldset.seed)
    world = solar.TwoDimWorld(smp, worldset, db, c, debugwin)

    chunkX = 0
    chunkY = 0

    # Load current chunk from the database/generate a new chunk if not found
    dataset = world.loadchunk(chunkX, chunkY)

    chunk = solar.TwoDimChunk(dataset, worldset, chunkX, chunkY)
    painter = solar.TwoDimDrawing(worldset, debugwin)

    # Create the player
    objects = []
    c.execute("SELECT rowid,* FROM objects")
    records = c.fetchall()
    if len(records) < 1:
        # chunkX/Y and x/y all default to 0,0. All the other defaults are sane too
        objects.append(solar.TwoDimMoveable(worldset, painter, db, c, terrwin, objid=1, debugwin=debugwin))
        # debug("Object " + objects[-1].icon + " created at " + str(objects[-1].x) + "," + str(objects[-1].y))
        c.execute("INSERT INTO objects (x, y, chunkX, chunkY, icon, width, height, color) VALUES (" + str(objects[-1].x) + "," + str(objects[-1].y) + ","  + str(objects[-1].chunkX) + "," + str(objects[-1].chunkY) + "," + "'" + str(objects[-1].icon) + "'" + "," + str(objects[-1].width) + "," + str(objects[-1].height) + "," + str(objects[-1].color) + ")")
        db.commit()
        # debug("Object " + objects[-1].icon + " written to the database")

        objects.append(solar.TwoDimMoveable(worldset, painter, db, c, terrwin, icon='%', objid=1, debugwin=debugwin))
        # debug("Object " + objects[-1].icon + " created at " + str(objects[-1].x) + "," + str(objects[-1].y))
        c.execute("INSERT INTO objects (x, y, chunkX, chunkY, icon, width, height, color) VALUES (" + str(objects[-1].x) + "," + str(objects[-1].y) + "," + str(objects[-1].chunkX) + "," + str(objects[-1].chunkY) + "," + "'" + str(objects[-1].icon) + "'" + "," + str(objects[-1].width) + "," + str(objects[-1].height) + "," + str(objects[-1].color) + ")")
        db.commit()
        # debug("Object " + objects[-1].icon + " written to the database")

        objects.append(solar.TwoDimMoveable(worldset, painter, db, c, terrwin, icon='&', color=Colors.BRIGHT_CYAN, x=5, y=5, objid=1, debugwin=debugwin))
        # debug("Object " + objects[-1].icon + " created at " + str(objects[-1].x) + "," + str(objects[-1].y))
        c.execute("INSERT INTO objects (x, y, chunkX, chunkY, icon, width, height, color) VALUES (" + str(objects[-1].x) + "," + str(objects[-1].y) + "," + str(objects[-1].chunkX) + "," + str(objects[-1].chunkY) + "," + "'" + str(objects[-1].icon) + "'" + "," + str(objects[-1].width) + "," + str(objects[-1].height) + "," + str(objects[-1].color) + ")")
        db.commit()
        # debug("Object " + objects[-1].icon + " written to the database")
    else:
        for rec in records:
            objects.append(painter.db2moveable(rec, painter, db, c, terrwin, chunkX, chunkY))

    painter.drawchunk(c, chunkX, chunkY, terrwin, drawobjs=True)

    curobj = 0
    debug("Waiting for user input, Q to quit")
    # Process user key presses
    keypress = ""
    while keypress.upper() != "E" and keypress.upper() != "Q":  # E, Q - Quit
        keypress = stdscr.getkey()
        if keypress == "KEY_LEFT":
            try:
                objects[curobj].moveoffset(0,-1)
            except ValueError as e:
                debug("Player at maximum western edge of chunk")
        elif keypress == "KEY_UP":
            try:
                objects[curobj].moveoffset(-1,0)
            except ValueError as e:
                debug("Player at maximum northern edge of chunk")
        elif keypress == "KEY_RIGHT":
            try:
                objects[curobj].moveoffset(0,1)
            except ValueError as e:
                debug("Player at maximum eastern edge of chunk")
        elif keypress == "KEY_DOWN":
            try:
                objects[curobj].moveoffset(1,0)
            except ValueError as e:
                debug("Player at maximum southern edge of chunk")
        elif keypress.upper() == "E" or keypress.upper() == "Q":
            # Do nothing, loop will exit
            # Of course in Python you can't do NOTHING, there has to be an indented
            #  block below an elif:, so we just assign keypress to itself so we do
            #  SOMETHING that equates to NOTHING
            keypress = keypress
        elif is_int(keypress):
            # If the key pressed was a number (1-9), select an object
            if int(keypress) > 0 and int(keypress) < 10:
                # Make sure the selected object exists
                if int(keypress) <= len(objects):
                    # Select it
                    curobj = int(keypress) - 1
                    debug("Object " + objects[curobj].icon + " selected")
                else:
                    debug("Invalid object " + str(keypress) + " selected")
            else:
                debug("Invalid object " + str(keypress) + " selected")
        else:
            debug("Unknown key pressed: " + str(keypress))

    debug("User requested quit")
    db.commit()
    db.close()

def debug(text):
    if SHOWDEBUG:
        printwin(debugwin, str(text))

def printwin(win, text):
    "Write the text to a curses window, followed by a newline (print if no window)"
    # Check and see if we were passed a curses window
    if str(type(win)) == "<type '_curses.curses window'>":
        # Add the text to the window, along with a newline
        win.addstr(str(text) + "\n")
        # Refresh the window to update the screen
        win.refresh()
    else:
        # No curses window, print the text to stdout
        print(str(text))

def is_int(val):
    "Returns true if val is an integer"
    return type(val) == type(int())

## Use the curses wrapper to call main so that the console still gets cleaned
##  up if we throw an unhandled exception
curses.wrapper(main)
