#!/usr/bin/python

import os, sys

def usage():
    print 'USAGE: ' + sys.argv[0] + ' <n (number of tasks)>'
    print 'Generate a system of n interdependent cyclon task definition files,'
    print 'and a cyclon config file to run the system in dummy mode. For use'
    print 'in testing cyclon performance on large task numbers (dummy mode'
    print 'and real mode are the same as far as cyclon is concerned).'
    print ''
    print 'Each task depends only on the previous one, i.e. a simple linear'
    print 'sequence so that only a few external dummy task programs run at once.'
    print 'This prevents the system (hardware, not cyclon) being swamped by a'
    print 'large number of external dummy programs all running at the same time.'
    print ''
    print 'Output locations relative to script running directory:'
    print '  sys/scaling-test/user_config.py'
    print '  sys/scaling-test/taskdef/(task definition files)'
    sys.exit(1)

def main( argv ):

    if len( argv ) != 2:
        usage()

    n_tasks = argv[1]

    topdir = 'system-def/scaling-test'
    defdir = topdir + '/taskdef'

    if not os.path.exists( defdir ):
	print '> creating directory ' + defdir 
	os.makedirs( defdir )

    print "> writing task definition files:"
    for task in range( 1, int(n_tasks) + 1 ):

        tdef = 'T' + str( task )
        prev_tdef = 'T' + str( task - 1 )

        print "   + " + 'T' + str(task) + '.def'
    
        FILE = open( defdir + '/' + tdef + '.def', 'w' )
     
        FILE.write(
                """
# THIS IS A cyclon TASK CLASS DEFINITION FILE
# See full_template.def for documented entries

%NAME
""" )
        FILE.write( tdef + '\n' )

        FILE.write(
            """
%VALID_HOURS
    0,6,12,18

%EXTERNAL_TASK
    null

%PREREQUISITES
""")

        if task == 1:
            FILE.write('\n\n')

        else:
            FILE.write( '    ' + prev_tdef + ' finished for $(MY_REFERENCE_TIME)\n' )
            
        FILE.write( 
            """
%OUTPUTS
    # defaults only
    
        FILE.close() 

    # write config file
    print '\n> writing user config file for this system: '
    print '  + ' + topdir + '/user_config.py'

    FILE = open( topdir + '/user_config.py', 'w' )

    FILE.write(
            """
#!/usr/bin/python

# cyclon user configuration file
# see config.py for other options

# DO NOT REMOVE THE FOLLOWING TWO LINES >>>>
import logging  # for logging level
config = {}
####################################### <<<<

config[ 'system_name' ] = 'scaling-test'

config[ 'start_time' ] = '2009030200'
config[ 'stop_time' ] = '2009030300'

config[ 'logging_level' ] = logging.DEBUG

#config[ 'use_broker' ] = False

config[ 'dummy_mode' ] = True
config[ 'dummy_clock_rate' ] = 10      
config[ 'dummy_clock_offset' ] = 10 

config[ 'use_qsub' ] = False
config[ 'job_queue' ] = 'default'

config['task_list'] = [\n""" )

    for task in range( 1, int(n_tasks) + 1 ):

        tdef = 'T' + str( task )
        FILE.write( '    \'' + tdef + '\',\n' )

    FILE.write(
            """]
""")

    FILE.close()

    # write readme file
    print "\n> writing " + topdir + "/README" 
    FILE = open( topdir + '/README', 'w' )

    FILE.write( "The user_config.py and the taskdef files in this directory were autogenerated\n" )
    FILE.write( "by " + sys.argv[0] + "\n" )
    FILE.write( "and therefore should not be added to the revision control repository.\n\n" )
    FILE.close()

    print
    print "> Now you need to generate task classes and environment script:"
    print "  $ configure-system " + topdir
    print 

if __name__ == '__main__':
    main( sys.argv )
