""" 
This script contains functions to get various output variables 
from Cyclus's sqlite output database 
"""

# Dependencies 
import pandas as pd 
import numpy as np 
import sqlite3 as lite
import collections

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

def timeseries_cum(specific_search, duration, kg_to_tons):
    """returns a timeseries list from specific_search data.
    Parameters
    ----------
    specific_search: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    multiplyby: int
        integer to multiply the value in the list by for
        unit conversion from kilograms
    kg_to_tons: bool
        if True, list returned has units of tons
        if False, list returned as units of kilograms
    Returns
    -------
    timeseries of commodities in kg or tons
    """
    value = 0
    value_timeseries = []
    array = np.array(specific_search)
    if len(specific_search) > 0:
        for i in range(0, duration):
            value += sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries


def simulation_timesteps(cur):
    """Returns simulation start year, month,
    duration and timesteps (in numpy linspace).
    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    Returns
    -------
    init_year: int
        start year of simulation
    init_month: int
        start month of simulation
    duration: int
        duration of simulation
    timestep: list
        linspace up to duration: ar array with
        [start of the sequence, end of the sequence]
    """
    info = cur.execute('SELECT initialyear, initialmonth, '
                       'duration FROM info').fetchone()
    init_year = info['initialyear']
    init_month = info['initialmonth']
    duration = info['duration']
    timestep = np.linspace(0, duration - 1, num=duration)

    return init_year, init_month, duration, timestep


def stockpiles(cur, facility, is_cum=True):
    """gets inventory timeseries in a fuel facility
    Parameters
    ----------
    cur: sqlite cursor
        sqlite cursor
    facility: str
        name of facility
    is_cum: bool
        gets cumulative timeseris if True, monthly value if False
    Returns
    -------
    pile: dictionary
        dictionary with "key=agent type, and
        value=timeseries list of stockpile"
    """
    pile = collections.OrderedDict()
    agentid = agent_ids(cur, facility)
    query = exec_string(agentid, 'agentid', 'timecreated, quantity, qualid')
    query = query.replace('transactions', 'agentstateinventories')
    print(query)
    stockpile = cur.execute(query).fetchall()
    init_year, init_month, duration, timestep = simulation_timesteps(cur)
    if is_cum:
        stock_timeseries = timeseries_cum(stockpile, duration, False)
    else:
        stock_timeseries = timeseries(stockpile, duration, False)
    pile[facility] = stock_timeseries

    return pile


def agent_ids(cur, archetype):
    """Gets all agentids from Agententry table for wanted archetype

        agententry table has the following format:
            SimId / AgentId / Kind / Spec /
            Prototype / ParentID / Lifetime / EnterTime

    Parameters
    ----------
    cur: cursor
        sqlite cursor3
    archetype: str
        agent's archetype specification

    Returns
    -------
    agentids: list
        list of all agentId strings
    """
    agents = cur.execute("SELECT agentid FROM agententry WHERE prototype "
                         "LIKE '%" + archetype + "%' COLLATE NOCASE"
                         ).fetchall()

    return list(str(agent['agentid']) for agent in agents)

def exec_string(specific_search, search, request_colmn):
    """Generates sqlite query command to select things and
        inner join resources and transactions.

    Parameters
    ----------
    specific_search: list
        list of items to specify search
        This variable will be inserted as sqlite
        query arugment following the search keyword
    search: str
        criteria for specific_search search
        This variable will be inserted as sqlite
        query arugment following the WHERE keyword
    request_colmn: str
        column (set of values) that the sqlite query should return
        This variable will be inserted as sqlite
        query arugment following the SELECT keyword

    Returns
    -------
    str
        sqlite query command.
    """
    if len(specific_search) == 0:
        raise Exception('Cannot create an exec_string with an empty list')
    if isinstance(specific_search[0], str):
        specific_search = ['"' + x + '"' for x in specific_search]

    query = ("SELECT " + request_colmn +
             " FROM resources INNER JOIN transactions"
             " ON transactions.resourceid = resources.resourceid"
             " WHERE (" + str(search) + ' = ' + str(specific_search[0])
             )
    for item in specific_search[1:]:
        query += ' OR ' + str(search) + ' = ' + str(item)
    query += ')'

    return query


def timeseries(specific_search, duration, kg_to_tons):
    """returns a timeseries list from specific_search data.

    Parameters
    ----------
    specific_search: list
        list of data to be created into timeseries
        list[0] = time
        list[1] = value, quantity
    duration: int
        duration of the simulation
    kg_to_tons: bool
        if True, list returned has units of tons
        if False, list returned as units of kilograms

    Returns
    -------
    timeseries list of commodities stored in specific_search
    """
    value = 0
    value_timeseries = []
    array = np.array(specific_search)
    if len(specific_search) > 0:
        for i in range(0, duration):
            value = sum(array[array[:, 0] == i][:, 1])
            if kg_to_tons:
                value_timeseries.append(value * 0.001)
            else:
                value_timeseries.append(value)
    return value_timeseries