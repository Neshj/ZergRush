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

    

"""
class RoboClient(RoboEntity):

    # Constructor
    def __init__(self, RoboTeam, ip, rx_port_program, tx_port_program, rx_port_server, tx_port_server):
        super(RoboEntity, self).__init__("Client", RoboTeam, ip)

        # Ports for communication with the team's program
        self.rx_port_program = rx_port_program
        self.tx_port_program = tx_port_program

        # Ports for communication with the server
        self.rx_port_server  = rx_port_server
        self.tx_port_server  = tx_port_server

class RoboRemote(RoboEntity):

    # Constructor
    def __init__(self, RoboTeam, ip, rx_port_server, tx_port_server):
        super(RoboEntity, self).__init__("RoboRemote", RoboTeam, ip)

        #init members
        self.rx_port_server = rx_port_server
        self.tx_port_server = tx_port_server

class RoboProgram(RoboEntity):

    # Constructor
    def __init__(self, RoboTeam, ip, rx_port_client, tx_port_client):
        super(RoboEntity, self).__init__("RoboProgram", RoboTeam, ip)

        #init members
        self.rx_port_client = rx_port_client
        self.tx_port_client = tx_port_client

"""

class Team:
    """docstring for Team"""
    def __init__(self, name):
        self.name = name

class RoboLauncher:
    
    def Launch(self):

        team = Team("RazTeam")
        ip = "1.2.3.4"
    
        # Ports for control messages to robot
        rx_port_control = 10000
        tx_port_control = 20000
    
        # Ports for communication with driver's remote
        rx_port_remote = 30000
        tx_port_remote = 40000
    
        # Ports for communication with client on the robot
        rx_port_client  = 50000
        tx_port_client  = 60000
    
        a = RoboServer( team, ip,                       \
                        tx_port_remote, rx_port_remote, \
                        tx_port_client, rx_port_client, \
                        tx_port_control, rx_port_control)
    
        a.Launch()
        from time import sleep
    
        for i in range(10):
            sleep(1)
            print "%d..." % (10 - i)
    
        a.Terminate()
