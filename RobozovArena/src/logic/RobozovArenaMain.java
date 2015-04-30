/**
 * @authors: Amir Krayden
 * @date: 21/03/15 
 */
package logic;

import java.util.logging.Level;
import java.util.logging.Logger;

import ui.MainWindow;


public class RobozovArenaMain {

	protected static RobozovArenaMain theArena = null; 

	private Logger theLogger;
	
	/* 
	 * Main function
	 */
	public static void main(String[] args) {
		
		RobozovArenaMain.getObject().run();
		
	}
	
	
	/* 
	 * Singletone get function
	 */
	public static RobozovArenaMain getObject() {
		
		if (theArena == null) {
			theArena = new RobozovArenaMain();
		}
		
		return theArena;
	}
	
	/*
	 * Inner constructor
	 */
	protected RobozovArenaMain() {
		
		// Get the system log object
		theLogger = RobozovArenaUtility.getSystemLog();
		
		theLogger.log(Level.INFO, "System init", this);
		theLogger.log(Level.INFO, "In RobozovArenaMain()::RobozovArenaMain()", this);
		
	}
	
	/*
	 * UI changeover logic
	 */
	private void run() {
		
		theLogger.log(Level.INFO, "In RobozovArenaMain()::run()", this);
		
		// Init the arena logic
		ArenaLogic arenaLogic = new ArenaLogic();
		
		// Load the configuration
		arenaLogic.loadConfig();
		
		// Run
		arenaLogic.start();
		
		// Start the UI
		MainWindow.ShowDialog();
		
		theLogger.log(Level.INFO, "In RobozovArenaMain()::run()", this);
	}
	
}
