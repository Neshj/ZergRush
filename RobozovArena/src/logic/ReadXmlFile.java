package logic;

import java.io.File;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

public class ReadXmlFile {
	
	private RobozovArena robozovArena;
	
	public ReadXmlFile(String filePath) {
		
		try {
			
			robozovArena = new RobozovArena();
			
			File fXmlFile = new File(filePath);
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(fXmlFile);
			
			doc.getDocumentElement().normalize();
			readArenaData(doc);
			readServerData(doc);
			readNetworksData(doc);
			readTeamsData(doc);
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}			
		
	}
	
    public RobozovArena getRobozovArena()
    {
    	return robozovArena;
    }
    
    private void readArenaData(Document doc) {
    	
    	
    	NodeList nList = doc.getElementsByTagName("ArenaNetwork");
    	Node nNode = nList.item(0);
    	
    	robozovArena.setArenaIp(getAttribute(nNode, "ip"));
    	robozovArena.setArenaPort(getAttribute(nNode, "rx_port"));
    	
    }
    
    private void readServerData(Document doc) {
    	
    	
    	NodeList nList = doc.getElementsByTagName("ServerNetwork");
    	Node nNode = nList.item(0);
    	
    	robozovArena.setServerIp(getAttribute(nNode, "ip"));
    	robozovArena.setServerPort(getAttribute(nNode, "rx_port"));
    	
    }
    
    private void readNetworksData(Document doc) {
    	
    	NodeList nList = doc.getElementsByTagName("RemotesNetwork");
    	Node nNode = nList.item(0);
    	
    	robozovArena.setRemotesNetworkSubnet(getAttribute(nNode, "subnet"));
    	
    	
    	nList = doc.getElementsByTagName("RobotsNetwork");
    	nNode = nList.item(0);
    	
    	robozovArena.setRobotsNetworkSubnet(getAttribute(nNode, "subnet"));
    }
    
    private void readTeamsData(Document doc) {
    	   	
    	NodeList nList = doc.getElementsByTagName("team");
    
    	for(int i=0;i<nList.getLength();i++)
    	{
    		Team team = new Team();
    		
    		Node nNode = nList.item(i);
    		team.setId(getAttribute(nNode, "id"));
    		team.setName(getAttribute(nNode, "name"));
    		team.setRemoteIp(getAttribute(nNode, "Remote_ip"));
    		team.setRemoteRxPort(getAttribute(nNode, "Remote_rx_port"));
    		team.setRobotIp(getAttribute(nNode, "Robot_ip"));
    		team.setRobotRxPort(getAttribute(nNode, "Robot_rx_port"));
    		
    		robozovArena.addTeam(team);
    	}
    	
    }
    
   
    
    private String getAttribute(Node nNode,String name) {
    	
    	// get a map containing the attributes of this node
    	NamedNodeMap attributes = nNode.getAttributes();
    	
    	// get the number of nodes in this map
    	int numAttrs = attributes.getLength();
    	
    	for (int i = 0; i < numAttrs; i++) {
    		
    		Attr attr = (Attr) attributes.item(i);
    		String attrName = attr.getNodeName();
    		String attrValue = attr.getNodeValue();
            
    		if(attrName == name) {
    			return attrValue;
    		}
    	}
    	
    	return null;
    }
    
}
