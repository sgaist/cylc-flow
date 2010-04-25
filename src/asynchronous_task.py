#!/usr/bin/python

#         __________________________
#         |____C_O_P_Y_R_I_G_H_T___|
#         |                        |
#         |  (c) NIWA, 2008-2010   |
#         | Contact: Hilary Oliver |
#         |  h.oliver@niwa.co.nz   |
#         |    +64-4-386 0461      |
#         |________________________|


# asynchronous tasks: cycle time required for some operations, at least for now, so give all 
# the time of 2999010101 but never change it.

import sys
from task import task
import cycle_time
from mod_nopid import nopid
import task_state
import logging
import Pyro.core
from copy import deepcopy

global state_changed
#state_changed = False
state_changed = True

# The abdication mechanism ASSUMES that the task manager creates the
# successor task as soon as the current task spawns.

class asynchronous_task( nopid, task ):

    used_outputs = {}
    
    quick_death = True

    def __init__( self, state, no_reset ):
        # Call this AFTER derived class initialisation

        # Derived class init MUST define:
        #  * prerequisites and outputs
        #  * self.env_vars 

        # Top level derived classes must define:
        #   self.id 
        #   <class>.instance_count = 0
        #   <class>.upward_instance_count = 0

        task.__init__( self, state, no_reset )

    # DO WE NEED THE FOLLOWING?
    #def nearest_c_time( self, rt ):
    #    return rt
    #def prev_c_time( self, rt ):
    #    return rt

    def next_c_time( self, rt = None ):
        # still needed for now, for spawning by manager
        return rt

    def dump_state( self, FILE ):
        # Write state information to the state dump file, cycle time
        # first to allow users to sort the file easily in case they need
        # to edit it:
        #   ctime name state

        # This must be compatible with __init__() on reload

        FILE.write( 'ASYNC'     + ' : ' + 
                    self.name         + ' : ' + 
                    self.state.dump() + '\n' )

    def check_requisites( self ):
        for message in self.prerequisites.get_satisfied_list():
            self.__class__.used_outputs[ message ] = True
