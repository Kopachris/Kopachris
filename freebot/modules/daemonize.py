# copied from http://daemonize.sourceforge.net/daemonize.txt

# Copyright 2007 Jerry Seutter yello (*a*t*) thegeeks.net

import fcntl
import os
import sys
import time

def start(fun_to_start, debug=False):
    logger = open("/var/daemonize.log", 'w')
    logger.write("daemonize.start() function called")
    logger.close()
    std_pipes_to_logger = True
    # Used docs by Levent Karakas 
    # http://www.enderunix.org/documents/eng/daemon.php
    # as a reference for this section.

    # Fork, creating a new process for the child.
    process_id = os.fork()
    if process_id < 0:
        # Fork error.  Exit badly.
        logger = open("/var/daemonize.log", 'w')
        logger.write("Fork error, line 18")
        logger.close()
        sys.exit(1)
    elif process_id != 0:
        # This is the parent process.  Exit.
        sys.exit(0)
    # This is the child process.  Continue.

    # Stop listening for signals that the parent process receives.
    # This is done by getting a new process id.
    # setpgrp() is an alternative to setsid().
    # setsid puts the process in a new parent group and detaches its
    # controlling terminal.
    process_id = os.setsid()
    if process_id == -1:
        # Uh oh, there was a problem.
        logger = open("/var/daemonize.log", 'w')
        logger.write("Problem getting new process id, line 35")
        sys.exit(1)

    # Close file descriptors
    devnull = '/dev/null'
    if hasattr(os, "devnull"):
        # Python has set os.devnull on this system, use it instead 
        # as it might be different than /dev/null.
        devnull = os.devnull
    null_descriptor = open(devnull, 'rw')
    if not debug:
        for descriptor in (sys.stdin, sys.stdout, sys.stderr):
            descriptor.close()
            descriptor = null_descriptor

    # Set umask to default to safe file permissions when running
    # as a root daemon. 027 is an octal number.
    os.umask(027)

    # Change to a known directory.  If this isn't done, starting
    # a daemon in a subdirectory that needs to be deleted results
    # in "directory busy" errors.
    # On some systems, running with chdir("/") is not allowed,
    # so this should be settable by the user of this library.
    os.chdir('/')

    # Create a lockfile so that only one instance of this daemon
    # is running at any time.  Again, this should be user settable.
    lockfile = open('/tmp/daemonize.lock', 'w')
    # Try to get an exclusive lock on the file.  This will fail
    # if another process has the file locked.
    fcntl.lockf(lockfile, fcntl.LOCK_EX|fcntl.LOCK_NB)

    # Record the process id to the lockfile.  This is standard
    # practice for daemons.
    lockfile.write('%s' %(os.getpid()))
    lockfile.flush()

    # Logging.  Current thoughts are:
    # 1. Attempt to use the Python logger (this won't work Python < 2.3)
    # 2. Offer the ability to log to syslog
    # 3. If logging fails, log stdout & stderr to a file
    # 4. If logging to file fails, log stdout & stderr to stdout.
    
    logger = open("/var/daemonize.log", 'w')
    logger.write("Daemonized successfully.")
    logger.close()

    fun_to_start()
