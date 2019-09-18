""" 
This script contains functions to get various output variables 
from Cyclus's sqlite output database 
"""

# Dependencies 
import pandas as pd 
import numpy as np 
import sqlite3 as lite

def cursor(file_name):
    """Connects and returns a cursor to an sqlite output file
    Parameters
    ----------
    file_name: str
        name of the sqlite file
    Returns
    -------
    sqlite cursor3
    """

    con = lite.connect(file_name)
    con.row_factory = lite.Row
    return con.cursor()





