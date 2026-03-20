from curses import window

import cv2
import numpy as np
import time
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt

class Window(QWidget):
    """
    Main GUI window for the Photobooth.
    
    Responsibilities:
    - Display the camera feed
    - Manage countdown timers
    - Capture photos
    - Show previews 
    - Generate photostrips

    Attributes:
    - photo_count : int
        Total number of photostrips created during the session.
    - photos : list
        Stores filenames of captured images used to generate the photostrip.
    - captureIndex : int
        Tracks number of photos captured in the current photostrip. Acts as a counter.
    - countdown : int
        Number of seconds before capturing each photo.
    - countdownLabel : QLabel
        Label widget used to display the countdown timer before each photo is taken.
    - video : cv2.VideoCapture
        Webcame camera object used for live camera feed.
    - frame : numpy.ndarray
        Current frame captured from the webcam.
    - imageLabel : QLabel
        Label widget used to display the live camera feed and photo previews.
    - feed : QPixmap
        Current camera feed converted to a QPixmap for display in the GUI.
    - welcome : QLabel
        Label widget displaying the welcome message at the start of the program.
    - button : QPushButton
        Button widget that starts the photobooth process when clicked.
    - photostripImage : numpy.ndarray
        The final photostrip image generated from the captured photos.
    """
    def __init__(window):
        """
         Initializes the Photobooth window and user interface. 
         Initializes variables used for photostrip tracking and prepares the camera timer that continuously updates the feed.

         Function: creates the GUI layout including welcome text, start button, countdown display, camerafeed display, preview displays

         Preconditions: 
         - PyQt application must be initialized before creating this window.
         
         Postconditions:
         - The GUI is fully initialized and ready for user interaction.
        """
        super().__init__()

        window.photo_count = 0 #total number of photostrips
        window.photos = [] #array to save filenames for photostrip generation
        window.captureIndex = 0 #number of photos taken in current photostrip
        window.countdown = 3 #7 seconds between each picture
        window.frameColor = (255,255,255) #default photostrip frame color is white
        
        window.video = None
        window.setWindowTitle("Photobooth")
        
        #GUI Layout
        window.layout = QVBoxLayout()
        window.setLayout(window.layout)
        window.setFixedSize(1470,895)   
        
        #welcome text
        window.welcome = QLabel("Welcome to my Photobooth") #welcome message displayed at the start of the program
        window.welcome.setStyleSheet("font-size: 36px; font-weight: bold;")
        window.layout.addWidget(window.welcome, alignment = Qt.AlignmentFlag.AlignCenter)

        #start button
        window.startButton = QPushButton("Start", window)
        window.startButton.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #fdbe15; color: white; border: none; border-radius: 4px;""")
        window.startButton.clicked.connect(window.clicked)
        window.layout.addWidget(window.startButton, alignment = Qt.AlignmentFlag.AlignCenter)

        #next button
        window.nextButton = QPushButton("Next", window)
        window.nextButton.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #fdbe15; color: white; border: none; border-radius: 4px;""")
        window.nextButton.clicked.connect(window.printPhotostrip)
        window.nextButton.setHidden(True)
        window.layout.addWidget(window.nextButton, alignment = Qt.AlignmentFlag.AlignRight)

        #countdown label
        window.countdownLabel = QLabel("") #widget to display countdown before each photo is taken 
        window.layout.addWidget(window.countdownLabel, alignment = Qt.AlignmentFlag.AlignCenter)

        #timer
        window.timer = QTimer()
        window.timer.timeout.connect(window.cameraLoop) #runs cameraLoop when timer is connected
        
        #image label
        window.imageLabel = QLabel() #widget to display camera feed and previews
        window.imageLabel.setFixedSize(867, 714)
        window.layout.addWidget(window.imageLabel, alignment = Qt.AlignmentFlag.AlignCenter)

        #standard color frames buttons
        window.white = QPushButton("        ", window) #white
        window.white.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #ffffff; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.white, alignment = Qt.AlignmentFlag.AlignRight)
        window.white.setHidden(True)

        window.black = QPushButton("        ", window) #black
        window.black.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #000000; color: white; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.black, alignment = Qt.AlignmentFlag.AlignRight)
        window.black.setHidden(True)

        window.pink = QPushButton("        ", window) #pink
        window.pink.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #ffdbe9; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.pink, alignment = Qt.AlignmentFlag.AlignRight) 
        window.pink.setHidden(True)

        window.yellow = QPushButton("        ", window) #yellow
        window.yellow.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #fff6b7; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.yellow, alignment = Qt.AlignmentFlag.AlignRight) 
        window.yellow.setHidden(True)

        window.mint = QPushButton("        ", window) #mint
        window.mint.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #b7e6df; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.mint, alignment = Qt.AlignmentFlag.AlignRight) 
        window.mint.setHidden(True)
        
        window.lavender = QPushButton("        ", window) #lavender
        window.lavender.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #e6e6fa; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.lavender, alignment = Qt.AlignmentFlag.AlignRight) 
        window.lavender.setHidden(True)

        #when color button is pressed, show photostrip with that color frame
        window.white.clicked.connect(lambda: window.showFrame((255,255,255)))
        window.black.clicked.connect(lambda: window.showFrame((0,0,0)))
        window.pink.clicked.connect(lambda: window.showFrame((233,219,255)))
        window.yellow.clicked.connect(lambda: window.showFrame((183,246,255)))
        window.mint.clicked.connect(lambda: window.showFrame((223,230,183)))
        window.lavender.clicked.connect(lambda: window.showFrame((250,230,230)))

        #filter buttons
        window.bw = QPushButton("B&W", window) #black and white filter
        window.bw.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #FFFFFF; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.bw, alignment = Qt.AlignmentFlag.AlignRight) 
        window.bw.setHidden(True)

        window.vintage = QPushButton("Vintage", window) #vintage filter
        window.vintage.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #FFFFFF; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.vintage, alignment = Qt.AlignmentFlag.AlignRight) 
        window.vintage.setHidden(True)

        window.sixteen = QPushButton("2016", window) #vintage filter
        window.sixteen.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #FFFFFF; color: black; border: none; border-radius: 2px;""")
        window.layout.addWidget(window.sixteen, alignment = Qt.AlignmentFlag.AlignRight) 
        window.sixteen.setHidden(True)

        #when color button is pressed, show photostrip with that color frame
        window.bw.clicked.connect(lambda: window.applyFilter("bw"))
        window.vintage.clicked.connect(lambda: window.applyFilter("vintage"))
        window.sixteen.clicked.connect(lambda: window.applyFilter("2016"))


    def clicked(window):
        """
         Triggered when the Start button is pressed.

         Function: Hides the welcome message and start button, then initializes the camera system.
        """
        window.welcome.setHidden(True)
        window.startButton.setHidden(True)
        
        window.startCamera()

    def startCamera(window):
        """
         Initializes the webcam and begins displaying the live camera feed.

         Function: Sets the camera frame size and starts a timer that continuously updates the camera frame displayed in the GUI.

         Preconditions: 
         - A webcam is connected and accessible by OpenCV.
         
         Postconditions:
         - The camera feed is displayed in the application window.
        """
        if window.video is None:
            window.video = cv2.VideoCapture(0) #open webcam
     
        window.video.set(cv2.CAP_PROP_FRAME_WIDTH, 867) #510*1.7
        window.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 714) #420*1.7
     
        window.timer.start (30) #update every 30ms

        if not window.video.isOpened(): #check if camera opened successfully
            print("Error Opening the Camera")
            return

    def cameraLoop(window):
        """
         Starts when timer is connected and runs repeatedly through a QTimer to simulate a live video feed inside the PyQt interface.

         Function: Continuously captures frames from the webcam and updates the GUI display.

         Preconditions: 
         - Timer must be running and connected to this function.
         - Webcam must be initialized and accessible.
         
         Postconditions:
         - Displays the current camera frame in the imageLabel widget.
        """

        if window.video is None:
            return
        
        ret, window.frame = window.video.read()
        if not ret:
            print("Failed to read frame from camera.")
            return
        
        window.frame = cv2.flip(window.frame,1)
       
        height, width, channels = window.frame.shape
        image = QImage(window.frame.data, width, height, QImage.Format.Format_BGR888)

        window.feed = QPixmap.fromImage(image)
        window.imageLabel.setPixmap(window.feed.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
   
    def keyPressEvent(window, event):
        """
         Handles keyboard input for controlling the photobooth.

         Function: Listens for specific key presses to trigger actions:
         - 'P' key: Starts the photo capture process by resetting the capture index and starting the countdown.
         - 'Q' key: Stops the timer, releases the webcam, and closes the application.

         Preconditions: 
        - The application window must be active.
         
         Postconditions:
        - Pressing 'P' initiates the photo capture sequence and pressing 'Q' closes the application.    
        """
        if event.key() == Qt.Key.Key_P:
            window.captureIndex = 0 #reset capture index for new photostrip
            window.startCountdown() 
        
        elif event.key() == Qt.Key.Key_Q:
            window.timer.stop()
            
            if window.video is not None:
                window.video.release()
            
            window.close()
            sys.exit()

    def startCountdown(window):
        """
         Displays a countdown timer before capturing a photo.

         Function: Updates the countdownLabel with the current countdown value every second. When the countdown reaches zero, it triggers the image capture process.  
        """
        if window.countdown > 0:
            window.countdownLabel.setText(str(window.countdown))
            window.countdown -= 1
            QTimer.singleShot(1000, window.startCountdown)
        
        elif window.countdown == 0:
            window.countdownLabel.setText("")
            window.captureImages()

    def captureImages(window):
        """
         Captures the current camera frame and saves it as an image file.

         Function: Saves the current frame from the webcam to a file with a timestamped filename to prevent overwriting existing images. It then updates the list of captured photos and manages the flow of capturing multiple photos for a photostrip, including showing previews and generating the final photostrip after 4 photos are taken.
        """
        timestamp = time.strftime("%Y%m%d%H%M%S")
        window.filename = f"photo_{timestamp}.png"
        cv2.imwrite(window.filename, window.frame)
        print (f"Saved {window.filename}")
        window.photos.append(window.filename)
        window.captureIndex += 1 

        if window.captureIndex < 4:
            window.timer.stop()
            window.preview()
            QTimer.singleShot(2500,window.resumeCamera)

        elif window.captureIndex == 4:
            window.timer.stop()
            window.preview()
            print ("Done capturing photos")
            QTimer.singleShot(2500,window.photostripHelper)
            
            window.photo_count+=1
            print(f"Current # of Photo Strips: {window.photo_count}")
            return
   
    def preview(window):
        """
         Displays the most recently captured photo in the GUI.

         Function: Loads the most recently captured image file and displays it in the imageLabel widget as a preview for the user for 2.5 seconds before resuming the camera feed for the next photo capture.
        """
        window.countdownLabel.setText("Preview")
        previewImage = QPixmap(window.filename)
        window.imageLabel.setPixmap(previewImage.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def resumeCamera(window):
        """
         Restarts the camera feed after displaying a preview image.

         Function: Clears the countdown label and restarts the camera timer to continue showing the live feed in preparation for the next photo capture in the photostrip sequence. This function is called after the preview of each captured photo, except after the fourth photo when the photostrip is generated instead.
        """
        window.countdown = 3
        window.timer.start(30)
        window.startCountdown()

    def chooseFrame(window):
        window.nextButton.setHidden(False)
        window.white.setHidden(False)
        window.black.setHidden(False)
        window.pink.setHidden(False)
        window.yellow.setHidden(False)
        window.mint.setHidden(False)
        window.lavender.setHidden(False)

    def showFrame(window, color):
        window.frameColor = color
        window.photostrip()
    
    def applyFilter(window, filter):
        if filter == "bw":
            window.photostripImage = cv2.cvtColor(window.photostripImage, cv2.COLOR_BGR2GRAY)
            window.photostripImage = cv2.cvtColor(window.photostripImage, cv2.COLOR_GRAY2BGR)
        elif filter == "vintage":
            sys.exit("vintage filter not implemented yet")
        elif filter == "2016":
            sys.exit("2016 filter not implemented yet")

    def photostripHelper(window):
        window.photostrip()
        window.chooseFrame()

    def photostrip(window):
        """
         Generates a photostrip from the captured photos.

         Function: Loads the captured image files and arranges them in a grid to create a photostrip.

         Preconditions:
         - Four photos must have been captured and saved in the photos list.
        
         Postconditions:
         - A photostrip image is generated and saved to disk, and previewPhotostrip is called where a preview of the photostrip is then displayed in the GUI.
        """
        readPhotos = [] 

        for file in window.photos:
            read = cv2.imread(file)
            readPhotos.append(read)

        height, width, channels = readPhotos[0].shape
        spacing = 60
        stripheight = (height * 4) + (spacing * 5)

        window.photostripImage = np.full((stripheight, width+220, 3), window.frameColor, dtype=np.uint8)

        y = 60
        x = 110

        for photo in readPhotos:
            window.photostripImage[y:y+height, x: x+width] = photo
            y += height + spacing
        
        #preview photostrip
        height, width, channels = window.photostripImage.shape
        previewPhotostrip = QImage(window.photostripImage.data, width, height, QImage.Format.Format_BGR888)
        pixmapPhotostrip = QPixmap.fromImage(previewPhotostrip)
        window.imageLabel.setPixmap(pixmapPhotostrip.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
       
    def printPhotostrip(window): 
        """
         Displays the generated photostrip in the GUI and saves it.

         Function: Converts the generated photostrip image into a format suitable for display in the PyQt interface and updates the imageLabel widget to show the photostrip preview to the user. This function is called after the photostrip is generated and saved to disk, allowing the user to see the final result of their photobooth session before everything is reset for the next session.
         """
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"photostrip_{timestamp}.png"
        cv2.imwrite(filename, window.photostripImage)
        window.reset()

    def reset(window):
        """
        Resets the photobooth application to its initial state after showing the photostrip preview.

        Function: Clears all captured photos, resets counters and timers, releases the webcam if it's still active, and shows the welcome message and start button again to allow for a new photobooth session to begin.

        """
        window.nextButton.setHidden(True)
        window.white.setHidden(True)
        window.black.setHidden(True)
        window.pink.setHidden(True)
        window.yellow.setHidden(True)
        window.mint.setHidden(True)
        window.lavender.setHidden(True)
       
        #resets everything after showing photostrip
        window.welcome.setHidden(False)
        window.startButton.setHidden(False)

        if window.video is not None:
            window.video.release()
            window.video = None
            
        window.countdownLabel.clear()
        window.imageLabel.clear()

        window.captureIndex = 0
        window.countdown = 3
       
        window.photos.clear()

        
def main():
# Initializes the PyQt application and creates the main window for the photobooth.
     app = QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec())

#run
if __name__ == "__main__":
    main()


