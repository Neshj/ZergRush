package logic;

public class Team {

	private String id;
	private String name;
	private String remoteIp;
	private String remoteRxPort;
	private String robotIp;
	private String robotRxPort;
	
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getRemoteIp() {
		return remoteIp;
	}
	public void setRemoteIp(String remoteIp) {
		this.remoteIp = remoteIp;
	}
	public String getRemoteRxPort() {
		return remoteRxPort;
	}
	public void setRemoteRxPort(String remoteRxPort) {
		this.remoteRxPort = remoteRxPort;
	}
	public String getRobotIp() {
		return robotIp;
	}
	public void setRobotIp(String robotIp) {
		this.robotIp = robotIp;
	}
	public String getRobotRxPort() {
		return robotRxPort;
	}
	public void setRobotRxPort(String robotRxPort) {
		this.robotRxPort = robotRxPort;
	}
	
	
}
