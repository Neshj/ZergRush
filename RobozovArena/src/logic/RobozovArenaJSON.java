package logic;

import java.io.StringWriter;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.json.*;

public class RobozovArenaJSON {

	// Logger
	private Logger theLogger;
	
	public RobozovArenaJSON() {
		
		// Get the system log object
		theLogger = RobozovArenaUtility.getSystemLog();
		
		theLogger.log(Level.INFO, "RobozovArenaJSON", this);
		theLogger.log(Level.INFO, "In RobozovArenaJSON()::RobozovArenaJSON()", this);
	}
	
	public String getArenaConfigAsJson(RobozovArena arena) {
		
		 String strJson = "";
	
		 theLogger.log(Level.INFO, "In RobozovArenaJSON()::getArenaConfigAsJson()", this);
		 
		 JSONObject arena_obj = new JSONObject();
		 JSONArray teams_array = new JSONArray();
	
	     arena_obj.put("arena_ip",arena.getArenaIp());
	     arena_obj.put("arena_rx_port",arena.getArenaPort());
	     arena_obj.put("server_ip",arena.getArenaIp());
	     arena_obj.put("server_rx_port",arena.getArenaPort());
	     arena_obj.put("remotes_network_subnet",arena.getRemotesNetworkSubnet());
	     arena_obj.put("robots_network_subnet",arena.getRobotsNetworkSubnet());
	     
	     
	     for(int i = 0; i <  arena.getNumOfTeams(); i++) {
	    	 Team team = arena.getTeamAt(i);
	    	 JSONObject team_obj = new JSONObject();
	    	 
	    	 team_obj.put("id", team.getId());
	    	 team_obj.put("name", team.getName());
	    	 team_obj.put("remote_ip", team.getRemoteIp());
	    	 team_obj.put("remote_rx_port", team.getRemoteRxPort());
	    	 team_obj.put("robot_ip", team.getRobotIp());
	    	 team_obj.put("robot_rx_port", team.getRobotRxPort());
	    	 
	    	 // Add the team to te array
	    	 teams_array.put(team_obj);
	    	 
	     }
	
	     arena_obj.put("teams", teams_array);
	     
	     StringWriter out = new StringWriter();
	     arena_obj.write(out);
	      
	     
	     strJson = out.toString();

	     theLogger.log(Level.INFO, "In RobozovArenaJSON() - JSON:", this);
	     theLogger.log(Level.INFO, strJson, this);
	     
	     return strJson;
	}
	
}
