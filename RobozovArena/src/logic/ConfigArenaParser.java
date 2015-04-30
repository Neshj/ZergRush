/**
 * @authors: Amir Krayden
 * @date: 21/03/15 
 */
package logic;


import java.util.logging.Level;
import java.util.logging.Logger;



public class ConfigArenaParser {

	private static Logger theLogger = RobozovArenaUtility.getSystemLog();
	
	public static RobozovArena ParseXMLFile(String filename) throws Exception {

		theLogger.log(Level.INFO, "In ConfigDOMParser::ParseXMLFile()");
		theLogger.log(Level.INFO, "ConfigurationDOMParser: Loading XML file: " + filename);
		
		ReadXmlFile rdxml = new ReadXmlFile(filename);
		
		RobozovArena arena = rdxml.getRobozovArena();
	    
	    theLogger.log(Level.INFO, "ConfigurationDOMParser: XML file loaded and parsed");
	    
	    return arena;
	    
	}
	 
}
