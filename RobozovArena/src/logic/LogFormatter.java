/**
 * @authors: Amir Krayden
 * @date: 21/03/15 
 */
package logic;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.logging.Formatter;
import java.util.logging.LogRecord;

public class LogFormatter extends Formatter {

	@Override
	public String format(LogRecord rec) {
		
		// Get current time and format it
		LocalDateTime datetime = LocalDateTime.now();
		DateTimeFormatter dtf = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
		
		String logdata = datetime.format(dtf) + ": " + rec.getMessage() + "\n";  
		return logdata;
	}
}
