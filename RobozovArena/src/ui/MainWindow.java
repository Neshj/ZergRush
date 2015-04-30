package ui;

import java.awt.EventQueue;
import java.awt.image.BufferedImage;
import java.io.File;

import javax.imageio.ImageIO;
import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;


public class MainWindow extends JDialog {

	/**
	 * Launch the application.
	 */
	public static void ShowDialog() {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					MainWindow dialog = new MainWindow();
					dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
					dialog.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the dialog.
	 */
	public MainWindow() {
		setBounds(100, 100, 559, 458);
		//getContentPane().setLayout(new BoxLayout(getContentPane(), BoxLayout.X_AXIS));
		
		JPanel panel = new JPanel();
				
		//JButton btnConnectToServer = new JButton("Connect to Server");
	
		//getContentPane().add(btnConnectToServer);

		try {
			BufferedImage myPicture = ImageIO.read(new File("Graphics/Robo510.png"));
			System.out.println("loaded picture");
			JLabel picLabel = new JLabel(new ImageIcon(myPicture));
			panel.add(picLabel);
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		
		getContentPane().add(panel);
		
	}

	
	
}
