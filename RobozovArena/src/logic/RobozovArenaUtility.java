/**
 * @authors: Amir Krayden
 * @date: 21/03/15 
 */
package logic;

import java.io.IOException;
import java.util.logging.FileHandler;
import java.util.logging.Logger;

public class RobozovArenaUtility {

	public static final String SystemLog = "SystemLog";
	public static final String SystemLogFileName = "SystemLog.log";
	public static final String SystemConfigFileName = "RobozovArenaConfig.xml";
	
	private static Logger theLogger;
	private static boolean fLogInit = false;
	
	/*
	 * Get the system log
	 */
	public static Logger getSystemLog() {
		
		if (fLogInit == false) {
			theLogger = Logger.getLogger(RobozovArenaUtility.SystemLog);
			initSystemLog();
			
			fLogInit = true;
		}
	
		return theLogger;
	}
	
	private static void initSystemLog() {

		FileHandler theHandler;
		
		try {
			theHandler = new FileHandler(RobozovArenaUtility.SystemLogFileName);
			//theHandler.setFilter(new ObjectFilter(this));
			theHandler.setFormatter(new LogFormatter());
			theLogger.addHandler(theHandler);
		} catch (SecurityException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
}
