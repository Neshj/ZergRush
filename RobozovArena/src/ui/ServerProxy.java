package ui;

import java.util.logging.Level;
import java.util.logging.Logger;

import logic.RobozovArenaUtility;

public class ServerProxy {

	protected static ServerProxy theProxy = null; 

	private Logger theLogger;
	
	
	/* 
	 * Singletone get function
	 */
	public static ServerProxy getObject() {
		
		if (theProxy == null) {
			theProxy = new ServerProxy();
		}
		
		return theProxy;
	}
	
	
	protected ServerProxy() {
	
		// Get the system log object
		theLogger = RobozovArenaUtility.getSystemLog();
		
		theLogger.log(Level.INFO, "ServerProxy init", this);
		theLogger.log(Level.INFO, "In ServerProxy()::ServerProxy()", this);
		
	}
	
	public void sendConfiguration(String jsonData) {
		
		// Send the arena configuration to the server
		theLogger.log(Level.INFO, "In ServerProxy()::sendConfiguration()", this);
	
		
	}
}
