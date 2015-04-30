package logic;

import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/*
 * Robozov arena class
 */

public class RobozovArena {

	// Logger
	private Logger theLogger;
	
	// Data members
	private String arenaIp;
	private String arenaRxPort;
	private String serverIp;
	private String serverRxPort;
	private String remotesNetworkSubnet;
	private String robotsNetworkSubnet;
	
	private List<Team> teamsList;

	public RobozovArena() {
		
		// Get the system log object
		theLogger = RobozovArenaUtility.getSystemLog();
		
		theLogger.log(Level.INFO, "RobozovArena", this);
		theLogger.log(Level.INFO, "In RobozovArenaMain()::RobozovArenaMain()", this);
	
		
		teamsList = new ArrayList<Team>();
		
	}
	
	public void setArenaIp(String ip) {
		this.arenaIp = ip;
	}
	
	public String getArenaIp() {
		return this.arenaIp;
	}
	
	public void setArenaPort(String port) {
		this.arenaRxPort = port;
	}
	
	public String getArenaPort() {
		return this.arenaRxPort;
	}
	
	public void setServerIp(String ip) {
		this.serverIp = ip;
	}
	
	public String getServerIp() {
		return this.serverIp;
	}
	
	public void setServerPort(String port) {
		this.serverRxPort = port;
	}
	
	public String getServerPort() {
		return this.serverRxPort;
	}
	
	public String getRemotesNetworkSubnet() {
		return remotesNetworkSubnet;
	}

	public void setRemotesNetworkSubnet(String remotesNetworkSubnet) {
		this.remotesNetworkSubnet = remotesNetworkSubnet;
	}

	public String getRobotsNetworkSubnet() {
		return robotsNetworkSubnet;
	}

	public void setRobotsNetworkSubnet(String robotsNetworkSubnet) {
		this.robotsNetworkSubnet = robotsNetworkSubnet;
	}
	
	public void addTeam(Team t) {
		
		teamsList.add(t);
		
	}
	
	public Team getTeamAt(int index) {
		return teamsList.get(index);
	}
	
	public int getNumOfTeams() {
		return teamsList.size();
	}
	
	
}
