# -*- coding: utf-8 -*-

#   Raz Karl
#   28/04/15
#

from subprocess import Popen, PIPE

SERVER_PROCESS_PATH = "../RobozovServer/server"

class RoboServer():

    # Constructor
    def __init__(self, team_name, remote_ip, robot_ip, remote_port, robot_port):

        self.team_name		= team_name
        self.remote_ip      = remote_ip
        self.robot_ip		= robot_ip

        # Ports for control messages to robot
        self.robot_port = robot_port

        # Ports for communication with driver's remote
        self.remote_port = remote_port

    def Launch(self):
        cmd  =  [SERVER_PROCESS_PATH, self.remote_ip, self.robot_ip, \
                self.remote_port, self.robot_port]

        print cmd

        try:
            self.server_process = Popen(cmd)
            print "RoboServer - process launched!"
            
        except OSError, err:
            print 'RoboServer - process got execption : %s' % (err)

    def Terminate(self):
        if (self.server_process):
            self.server_process.terminate()
            print "RoboServer - process terminated."

        else:
            print "RoboServer - process not running, unable to terminate."

    

class Team:
    """docstring for Team"""
    def __init__(self, name):
        self.name = name