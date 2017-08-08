# SolarWindsPython
An attempt at my Solar Winds concept in Python

The long term goal is a game where you control one or more automated drones. It starts on a planet, where you mine for the resources you need to take to space. Once in space you can continue to mine, no longer limited to a single planet (or even to planets) while building up your automaton empire. OSLT. The original plan was to make a MUD using the TinyMARE engine, but there were too many limitations to make the universe as large as I wanted it to be.

# Current status
Presently only two-dimensional support exists (still planet-bound). It loads chunk 0,0 from the database (or inits a new one if missing), loads up the object(s) from the database (or creates some test ones if there aren't any) and draws the objects on the screen. Objects can be moved with the arrow keys, different objects can be selected using the number keys (1-9).

# Requirements
The following Python libraries are required:

  * **curses**			included with python (on Linux, sorry Windows users!)
  * **pickle**      included with python
  * **random**			included with python
  * **sqlite3**			included with python 2.5+
  * **OpenSimplex** 	available via pip as `opensimplex`

  TL;DR: **Python 2.5+**, `pip install opensimplex`
