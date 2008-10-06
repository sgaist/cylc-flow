#!/usr/bin/python

""" 
Program called by the controller to "dummy out" external tasks.

(1) Takes <task name> and <reference time> arguments, which uniquely
    identifies the corresponding task object in the controller.
  
(2) Connects to the said controller task object via Pyro. 

(3) Calls [task object].get_postrequisites() to acquire a list of task
    postrequisites, and sets each of them "satisfied" in turn, with a
    short delay between each.

This allows the entire control program to be tested on the real model
sequence, without actually running the models, so long as model pre- and
post-requisites have been correctly defined, and with the proviso that
the dummy run-times are not currently proportional to the real run times.  
"""

import sys
import Pyro.naming, Pyro.core
from Pyro.errors import NamingError
from config import dummy_rate
import reference_time
import datetime

from time import sleep

pyro_shortcut = False

# command line arguments
if len( sys.argv ) != 3:
    print "USAGE:", sys.argv[0], "<task name> <REFERENCE_TIME>"
    sys.exit(1)
    
[task_name, ref_time] = sys.argv[1:]

# connect to the task object inside the control program

# need non pyro_shortcut (see below) for clock!
clock = Pyro.core.getProxyForURI("PYRONAME://" + "dummy_clock" )

if pyro_shortcut:
    task = Pyro.core.getProxyForURI("PYRONAME://" + task_name + "_" + ref_time )

else:
    # locate the NS
    locator = Pyro.naming.NameServerLocator()
    print "searching for pyro name server"
    ns = locator.getNS()

    # resolve the Pyro object
    print "resolving " + task_name + '_' + ref_time + " task object"
    try:
        URI = ns.resolve( task_name + '_' + ref_time )
        print 'URI:', URI
    except NamingError,x:
        print "failed: ", x
        raise SystemExit

    # create a proxy for the Pyro object, and return that
    task = Pyro.core.getProxyForURI( URI )

    est_hrs = task.get_estimated_run_time() / 60.0
    est_dummy_secs = est_hrs * dummy_rate

    postreqs = task.get_postrequisite_list()
    n_postreqs = len( postreqs )
    delay = est_dummy_secs / n_postreqs 
    print "DELAY for " + task_name + " is: ", delay

if task_name == "downloader":

    rt = reference_time._rt_to_dt( ref_time )
    dt = clock.get_datetime()
    difft = rt - dt
    if dt >= rt + datetime.timedelta( 0,0,0,0,0,3.25,0 ):
        task.incoming( 'NORMAL', 'input files already exist for ' + ref_time )
        task.incoming( 'NORMAL', 'CONTROLLER IN CATCHUP MODE' + str( difft ) )
    else:
        task.incoming( 'NORMAL', 'waiting for files for ' + ref_time )
        task.incoming( 'NORMAL', 'CONTROLLER IN REALTIME MODE' )
        while True:
            dt = clock.get_datetime()
            if dt >= rt:
                break
            sleep(2)

    for message in postreqs:
        # set each postrequisite satisfied in turn
        task.incoming( "NORMAL", message )
        sleep(1)

else:
    # set each postrequisite satisfied in turn
    for message in postreqs:
        task.incoming( "NORMAL", message )
        sleep(delay)

# finished simulating the external task
task.set_finished()
