package logic;

import java.util.logging.Level;
import java.util.logging.Logger;

import ui.ServerProxy;

public class ArenaLogic extends Thread {

	// Logger
	private Logger theLogger;
	
	// The arena
	private RobozovArena arena;
	private String arenaConfig;
	
	public ArenaLogic() {
		
		// Get the system log object
		theLogger = RobozovArenaUtility.getSystemLog();
		
		theLogger.log(Level.INFO, "ArenaLogic init", this);
		theLogger.log(Level.INFO, "In ArenaLogic()::ArenaLogic()", this);
		
	}

	
	public void loadConfig() {
		theLogger.log(Level.INFO, "In ArenaLogic()::loadConfig()", this);
		
		try {
			arena = (ConfigArenaParser.ParseXMLFile(RobozovArenaUtility.SystemConfigFileName));
		}
		catch (Exception e) {
			e.printStackTrace();
		}
		
	}
	
	public void run() {
		theLogger.log(Level.INFO, "In ArenaLogic()::run()", this);
		
		try { 
			Thread.sleep(1000);
		}
		catch(InterruptedException e) {
			
		}
		
		theLogger.log(Level.INFO, "In ArenaLogic()::Start Execution", this);
		
		RobozovArenaJSON arenaJson = new RobozovArenaJSON();
		
		arenaConfig = arenaJson.getArenaConfigAsJson(arena);
		
		System.out.print(arenaConfig);
		
		theLogger.log(Level.INFO, "In ArenaLogic()::Sending configuration to server", this);
		// Send the configuration to the server
		ServerProxy.getObject().sendConfiguration(arenaConfig);
	}
	
}
