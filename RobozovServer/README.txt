--++== Robotzov README ==++--

This readme will help you understand how to compile and run the various versions of this code.
There are several modes of operation to this code: Normal and Emulated.
* Normal mode is for deploying the targets on the real architecture of the game. Where the remote
  control resides in WLan A and the RPi resides in WLan B. This simplifies port mapping for both
  the server and the client. Compiling this can be done like this:
  For the server, on an x86 machine:
	$ make server
  For the client, on the RPi:
	$ make client
  Here is an example schema of how this works out:
  In order to run the server (on an x86 machine), use:
	$ ./server 192.168.1.101 10.0.0.101 10001 10002
  In order to run the client (on a RPi), use:
	$ ./client 10.0.0.1 10002 10003 10004

  * Note: All given ports are Datagram ports (UDP)

				       +--------------------------------+		     +-----------------------------------------+
 IP: 192.168.1.101		       | IP: 192.168.1.1<->IP: 10.0.0.1 |		     | IP: 10.0.0.101			       |
 +----------------+  REMOTE <-> SERVER |			        |  SERVER <-> ROBOT  |	     udp ports through localhost       |
 | Remote Control | <== port 10001 ==> |	     SERVER	        | <== port 10002 ==> | CLIENT <- 10003 + 1004 -> Robot program |
 +----------------+		       +--------------------------------+		     +-----------------------------------------+

  Now, you can create your own processes on the remote control station and send and receive
  packets on port 10001, and create your engine control process on the RPi which receives data from
  the remote control through the system in port 10003 and sends data back on port 10004.

* Emulated mode is where you can emulate the above schenario on a single PC. All the packets are
  sent locally.
  In order to compile the code in emulated mode, use:
	$ make emulate
  In order to run the server, use:
	$ ./server localhost localhost 1330 1331 1332 1333
  In order to run the client, use:
	$ ./client localhost 1333 1332 1334 1335
  Here is a schema of how the layout should look like

	IPs: localhost
+---------------------------------------------------------------------------------------------------+
|		== port 1331 ==>	   == port 1332 ==>	    == port 1334 ==>		    |
| Remote Control		  SERVER		     CLIENT		     Robot program  |
|		<== port 1330 ==	   <== port 1333 ==	    <== port 1335 ==		    |
+---------------------------------------------------------------------------------------------------+
