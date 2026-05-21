from fileinput import filename

import cv2
import mediapipe as mp
from matplotlib.pyplot import gray, hsv
import numpy as np
import time
import sys
import subprocess

from cvzone.HandTrackingModule import HandDetector

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PyQt6.QtGui import QImage, QPixmap, QIcon, QPainter
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal

from skimage import exposure
from playsound3 import playsound

#bg class to help with printing signal
class PrintThread(QThread):
    done = pyqtSignal()
   
    def __init__(self, filename):
            super().__init__()
            self.filename = filename

    def run(self):
        subprocess.run(["lpr", self.filename]) #prints
        time.sleep(8)
        self.done.emit() #sends signal

class Window(QWidget):
    """
    Main GUI window for the Photobooth.
    
    split into 3 pages:
    - Homepage: Displays welcome message and start button.
    - Camera Page: Shows live camera feed, countdown timer, and photo previews.
    - Customization Page: Allows users to customize their photostrip with frame colors, filters, and stickers.
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
    - pixmapPhotostrip : QPixmap
        The photostrip image converted to a QPixmap for display in the GUI.
    - frameColor array
        standard frame colors for photostrips, default is white
    - filter array
        standard filters for photostrips, default is none
    - sticker buttons
        standard stickers to add to photostrips, default is none
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
        window.filter = "Regular" #default filter is none
        window.mode = "regular"
    
        window.video = None
        window.setWindowTitle("Photobooth")

        #mouse tracking
        window.setMouseTracking(True)
        
        #GUI Layout
        window.setStyleSheet("background-color: #ffffff;")
        window.setFixedSize(1470,895)   
        window.stack = QStackedWidget()
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(window.stack)
        window.setLayout(mainLayout)

        #BRIGHTNESS ADJUSTMENT
        window.hd = HandDetector()
        window.brightness = 0
        window.brightnessMode = "idle"

        #HOMEPAGE (header, photobooth text, start button)
        homePage = QWidget()
        homeLayout = QVBoxLayout()
        homeLayout.setContentsMargins(0, 0, 0, 0)
        homeLayout.setSpacing(0)
        homePage.setLayout(homeLayout)

        #top header
        window.header= QLabel("ASIJ") 
        window.header.setStyleSheet("""background-color: #000000; color: #febe15; font-size: 26px; font-weight: bold; padding: 4px 10px;""")
        window.header.setFixedHeight(60)
        homeLayout.addWidget(window.header)

        homeLayout.addSpacing(260)

        #photobooth text
        window.photoboothText = QLabel("PHOTOBOOTH")
        window.photoboothText.setStyleSheet("""color: #000000; font-size: 96px; font-weight: 900;""")
        window.photoboothText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        homeLayout.addWidget(window.photoboothText)

        #start button
        window.startButton = QPushButton("Start", window)
        window.startButton.setStyleSheet("""QPushButton{background-color: #febe15; color: white; font-size: 34px; font-weight: bold; padding: 12px} QPushButton:hover{background-color: #ffcc33;}""")
        window.startButton.clicked.connect(window.clicked)
        homeLayout.addWidget(window.startButton, alignment = Qt.AlignmentFlag.AlignCenter)

        #CAMERA PAGE (countdown, camera feed, previews)
        cameraPage = QWidget()
        cameraMainLayout = QVBoxLayout()
        cameraMainLayout.setContentsMargins(0, 0, 0, 0)
        cameraMainLayout.setSpacing(10)
        cameraPage.setLayout(cameraMainLayout)

        # TEST FILTER BUTTON
        # window.testButton = QPushButton("Test Filter", cameraPage)
        # cameraMainLayout.addWidget(window.testButton)
        # window.testButton.clicked.connect(window.testFilter)
        # window.filter = "Regular"
       
        #take pictures button
        window.pictureButton = QPushButton("Take Pictures", cameraPage)
        window.pictureButton.setStyleSheet("""font-size: 18px; padding: 8px 36px; background-color: #fdbe15; color: #ffffff; border: none; border-radius: 0px;""")
        window.pictureButton.clicked.connect(window.takePicture)
        window.pictureButton.setHidden(True)
        cameraMainLayout.addSpacing(10)
        cameraMainLayout.addWidget(window.pictureButton, alignment = Qt.AlignmentFlag.AlignCenter)

        #mode button
        window.modeButton = QPushButton("Regular", cameraPage)
        window.modeButton.setStyleSheet("""QPushButton {font-size: 18px; padding: 8x 36px; background-color: #000000; color:white; border: none; border-radius 6px;} QPushButton:hover {background-color: #222222;}""")
        window.modeButton.clicked.connect(window.toggleMode)
        
        cameraMainLayout.addWidget(window.modeButton, alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        #face mesh
        window.faceMesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        window.sunglasses = cv2.imread("sunglasses.png", cv2.IMREAD_UNCHANGED)
        window.mustangEars = cv2.imread("mustang_ears.png", cv2.IMREAD_UNCHANGED)
        window.mustangNose = cv2.imread("mustang_nose.png", cv2.IMREAD_UNCHANGED)

        #countdown label
        window.countdownLabel = QLabel("") 
        window.countdownLabel.setStyleSheet("""color: #000000; font-size: 30px; font-weight:380; padding: 10px;""")
        cameraMainLayout.addWidget(window.countdownLabel, alignment = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        #timer
        window.timer = QTimer()
        window.timer.timeout.connect(window.cameraLoop) #runs cameraLoop when timer is connected
  
        #image label
        window.imageLabel = QLabel() #widget to display camera feed and previews
        window.imageLabel.setStyleSheet("background-color: black; border-radius: 26px; border: 4px solid #febe15; padding: 8px;""")
        window.imageLabel.setFixedSize(867, 714)
        cameraMainLayout.addWidget(window.imageLabel, alignment = Qt.AlignmentFlag.AlignCenter)
                                        
        #CUSTOM PAGE (frame, filter, sticker options)
        customPage = QWidget()
        customMainLayout = QHBoxLayout()
        customMainLayout.setContentsMargins(40, 40, 40, 40)
        customMainLayout.setSpacing(40)
        customPage.setLayout(customMainLayout)

        #left panel (photostrip preview)
        leftPanel = QWidget()
        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(0)
        leftPanel.setLayout(leftLayout)

        #image label for photostrip preview
        window.customImageLabel = QLabel()
        window.customImageLabel.setFixedSize(435,714)
        leftLayout.addWidget(window.customImageLabel, alignment = Qt.AlignmentFlag.AlignCenter)
        customMainLayout.addWidget(leftPanel)

        #right panel (customization options)
        rightPanel = QWidget()
        rightPanel.setStyleSheet("background-color: #ffffff; border-radius: 24px; padding: 20px;") 
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(50, 40, 50, 40)
        rightLayout.setSpacing(24)
        rightPanel.setLayout(rightLayout)

        #next button
        window.nextButton = QPushButton("Next", customPage)
        window.nextButton.setStyleSheet("""font-size: 24px; padding: 10px; background-color: #fdbe15; color: white; border: none; border-radius: 4px;""")
        window.nextButton.clicked.connect(window.printPhotostrip)
        rightLayout.addWidget(window.nextButton, alignment = Qt.AlignmentFlag.AlignRight)
        window.nextButton.setFixedWidth(100)

        #standard color frames buttons
        frameLabel = QLabel("Frame Color")
        frameLabel.setStyleSheet("""color: #000000; font-size: 20px; font-weight: 400;""")
        rightLayout.addWidget(frameLabel)

        frameRow = QHBoxLayout()
        frameRow.setSpacing(12)
        framecolors = [
            ("white",    "#ffffff", "black",  (255,255,255)),
            ("black",    "#000000", "white",  (0,0,0)),
            ("pink",     "#ffdbe9", "black",  (233,219,255)),
            ("yellow",   "#fff6b7", "black",  (183,246,255)),
            ("mint",     "#b7e6df", "black",  (223,230,183)),
            ("lavender", "#e6e6fa", "black",  (250,230,230)),
           ]

        window.frameButtons = []
        for name, background, text, rgb in framecolors:
            button = QPushButton("        ", cameraPage)
            button.setStyleSheet(f"""font-size: 24px; padding: 10px; background-color: {background}; color: {text}; border: none; border-radius: 2px;""")
            button.clicked.connect(lambda checked, c=rgb: window.showFrame(c))
            frameRow.addWidget(button)
            window.frameButtons.append(button)
        frameRow.addStretch()
        rightLayout.addLayout(frameRow)

        #filter buttons
        filterLabel = QLabel("Filter")
        filterLabel.setStyleSheet("""color: #000000; font-size: 20px; font-weight: 400;""")
        rightLayout.addWidget(filterLabel)

        filterRow = QHBoxLayout()
        filterRow.setSpacing(12)
        filters = ["Regular", "B&W", "Vintage", "2016"]
        
        window.filterButtons = []
        for filter in filters:
            button = QPushButton(filter, cameraPage)
            button.setStyleSheet("QPushButton {background-color: white; color: black; border: 2px solid #dddddd; border-radius: 12px; padding: 10px 18px; font-size: 16px;} QPushButton:hover {border: 2px solid #febe15;}")
            button.clicked.connect(lambda checked, f=filter: window.showFilter(f))
            filterRow.addWidget(button)
            window.filterButtons.append(button)
        rightLayout.addLayout(filterRow)

        #sticker buttons
        stickerLabel = QLabel("Stickers")
        stickerLabel.setStyleSheet("""color: #000000; font-size: 20px; font-weight: 400;""")
        rightLayout.addWidget(stickerLabel)

        stickerRow = QHBoxLayout()
        stickerRow.setSpacing(12)
        stickers = [
            ("asij", 600),
            ("gradyear", 800),
            ("gradhat", 700),
            ("goldstar", 250),
            ("goldcrown", 600),
            ("sparkle", 200),
            ("glitter", 400),
            ("mustangbob", 580),
            ("mustangbob2", 580),
            ]

        window.stickerButtons = []
        for sticker, size in stickers:
            pixmap = QPixmap(f"{sticker}.png")
            scaledpixmap = pixmap.scaled(100,100, Qt.AspectRatioMode.KeepAspectRatio)
            button = QPushButton()
            button.setIcon(QIcon(scaledpixmap))
            button.setIconSize(scaledpixmap.size())
            button.setStyleSheet("""background-color: transparent; border: none;""")
            button.clicked.connect(lambda checked, p=pixmap, sz=size: window.selectSticker(p, sz))
            stickerRow.addWidget(button)
            window.stickerButtons.append(button)
        rightLayout.addLayout(stickerRow)
        
        customMainLayout.addWidget(rightPanel)

        #FACIAL ENHANCER MODEL
        

        #PRINTING PAGE 
        #shows "printing..." text while photostrip is being sent to the printer to print
        printPage = QWidget()
        printPage.setStyleSheet("background-color: #ffffff;")
        printLayout = QVBoxLayout()
        printLayout.setContentsMargins(0, 0, 0, 0)
        printLayout.setSpacing(0)
        printPage.setLayout(printLayout)

        printLayout.addSpacing(100)

        window.mascotLabel = QLabel()
        window.mascotLabel.setStyleSheet("background-color: #febe15; border-radius:10px; padding:20px;")
        mascotPixmap = QPixmap("mascot.png")
        scaledMascot = mascotPixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        window.mascotLabel.setPixmap(scaledMascot)
        window.mascotLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        printLayout.addWidget(window.mascotLabel)

        printLayout.addSpacing(20)

        #asij label text
        asijLabel = QLabel("ASIJ Photobooth")
        asijLabel.setStyleSheet("color: #febe15; font-size: 75px; font-weight: bold;")
        asijLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        printLayout.addWidget(asijLabel)

        printLayout.addSpacing(10)

        #printing... text
        printingLabel = QLabel("Your photostrip is printing...")
        printingLabel.setStyleSheet("color: #000000; font-size: 36px;")
        printingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        printLayout.addWidget(printingLabel)

        printLayout.addSpacing(20)

        #loading dots
        window.dotsLabel = QLabel("●")
        window.dotsLabel.setStyleSheet("color: #febe15; font-size: 24px;")
        window.dotsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        printLayout.addWidget(window.dotsLabel)

        printLayout.addSpacing(20)

        #ALL PAGES
        window.stack.addWidget(homePage)
        window.stack.addWidget(cameraPage)
        window.stack.addWidget(customPage)
        window.stack.addWidget(printPage)

    def clicked(window):
        """
         Triggered when the Start button is pressed.

         Function: Hides the welcome message and start button, then initializes the camera system.
        """
        window.stack.setCurrentIndex(1)       
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
       
        window.pictureButton.setHidden(False)

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
        window.frame = window.enhanceFace(window.frame)

        if window.mode == "regular":
            window.frame = window.adjustBrightness(window.frame)

        if window.mode == "filters":
            window.frame = window.liveFilter(window.frame)

        height, width, channels = window.frame.shape
        image = QImage(window.frame.data, width, height, QImage.Format.Format_BGR888)

        window.feed = QPixmap.fromImage(image)
        window.imageLabel.setPixmap(window.feed.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
   
    def takePicture(window):
        window.captureIndex = 0 #reset capture index for new photostrip
        window.startCountdown() 
        window.pictureButton.setHidden(True)

    def keyPressEvent(window, event):
        """
         Handles keyboard input for controlling the photobooth.

         Function: Listens for specific key presses to trigger actions:
         - 'Q' key: Stops the timer, releases the webcam, and closes the application.

         Preconditions: 
        - The application window must be active.
         
         Postconditions:
        - pressing 'Q' closes the application.    
        """   
        
        if event.key() == Qt.Key.Key_Q:
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
            if window.countdown == 1:
                QTimer.singleShot(500, lambda: playsound('camerasound.mp3', block=False))
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

    def toggleMode(window):
        if window.mode == "regular":
            window.mode = "filters"
            window.modeButton.setText("Filters")
        else:
            window.mode = "regular"
            window.modeButton.setText("Regular")

#facial enhancer/ live feed filters
    def enhanceFace(window, frame):
        
        return frame

    def overlay(window, frame, overlay, x, y, width, height):
        overlay = cv2.resize(overlay, (width, height))

        h, w, c = frame.shape

        if x < 0 or y < 0 or x + width > w or y + height > h:
            return frame
        
        if overlay.shape[2] == 4:
            transparency = overlay[:, :, 3] / 255.0

            for c in range(0, 3):
                frame[y:y+height, x:x+width, c] = (transparency*overlay[:, :, c] + (1-transparency) * frame[y:y+height, x:x+width, c])
        else:
            frame[y:y+height, x:x+width] = overlay
        
        return frame
    
    def sunglass(window, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = window.faceMesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame
        
        h,w,c = frame.shape
        
        for face in results.multi_face_landmarks:
            leftEye = face.landmark[33]
            rightEye = face.landmark[263]
            nose = face.landmark[168]

            leftX = int(leftEye.x * w)
            rightX = int(rightEye.x * w)
            noseX = int(nose.x * w)
            noseY = int(nose.y * h)

            glassesWidth = int((rightX - leftX) * 1.75) #wider/narrower
            glassesHeight = int(glassesWidth * 0.5) #taller/shorter
            x = int(noseX-glassesWidth/2) #left/right
            y = int(noseY-glassesHeight/2+60) #up/down 
            frame = window.overlay(frame, window.sunglasses, x, y, glassesWidth, glassesHeight)
        
        print("sunglasses filter applied")
        return frame
    
    def sparkle(window, frame):
        print("sparkle filter applied")
        return frame
    
    def confetti(window, frame):
        print("confetti filter applied")
        return frame
   
    def horse(window, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = window.faceMesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame
        
        h,w,c = frame.shape
        
        for face in results.multi_face_landmarks:
            leftEye = face.landmark[33]
            rightEye = face.landmark[263]
            forehead = face.landmark[10]
            nose = face.landmark[1]

            leftX = int(leftEye.x * w)
            rightX = int(rightEye.x * w)
            foreheadX = int(forehead.x * w)
            foreheadY = int(forehead.y * h)
            noseX = int(nose.x * w)
            noseY = int(nose.y * h)

            faceWidth = abs(rightX - leftX)
            
            earsWidth = int(faceWidth * 2.4) #wider/narrower for ears
            earsHeight = int(earsWidth * 0.6) #taller/shorter for ears
            earsX = int(foreheadX - earsWidth/2) #left/right
            earsY = int(foreheadY - earsHeight*0.78) #up/down

            noseWidth = int(faceWidth * 0.65) #wider/narrower for nose
            noseHeight = int(noseWidth * 0.65) #taller/shorter for nose
            noseX = int(noseX - noseWidth/2) #left/right
            noseY = int(noseY - noseHeight/2-40) #up/down
            
            frame = window.overlay(frame, window.mustangEars, earsX, earsY, earsWidth, earsHeight)
            frame = window.overlay(frame, window.mustangNose, noseX, noseY, noseWidth, noseHeight)
        
        print("horse filter applied")
        return frame

#gesture triggered brightness adjustment
    def adjustBrightness(window, frame):

        #LEFT HAND: 
        #fist --> enables adjusting brightness
        #open hand --> disables adjusting brightness, keeps it the adjusted brightness

        #RIGHT HAND
        #thumb to index finger --> #adjust brightness by changing distance between thumb and index finger (closer = darker, farther = brighter)
        #fist --> resets brightness to default and disables adjusting brightness

        hands, frame = window.hd.findHands(frame, draw=False)
        
        if hands:
            rightHand = False
            leftHand = False

            for hand in hands:
                if hand['type'] == 'Right':
                    leftHand= True
                elif hand['type'] == 'Left':
                    rightHand = True
                    
            for hand in hands:
                lm = hand['lmList']
                fingers = window.hd.fingersUp(hand)
                fist = fingers == [0,0,0,0,0]
                open = fingers == [1,1,1,1,1]
                
                if hand['type'] == 'Right':
                    if window.brightnessMode == "idle" and fist:
                        window.brightnessMode = "adjusting"
                    elif window.brightnessMode == "adjusting" and open and rightHand is True:
                        window.brightnessMode = "idle"

                elif hand['type'] == 'Left':
                    rightHand = True
                    if window.brightnessMode == "adjusting" and leftHand is True:
                        length, info, frame = window.hd.findDistance(lm[8][0:2], lm[4][0:2], frame)
                        target = int(np.interp(length, [25, 200], [-80, 80]))
                        window.brightness = int(window.brightness + (target - window.brightness) * 0.12)
                    elif window.brightnessMode == "adjusting" and fist: 
                        window.brightness = 0
                        window.brightnessMode = "idle"
            
        frame = cv2.convertScaleAbs(frame, alpha=1, beta=window.brightness)

    
        return frame

    def liveFilter(window, frame):
        #two rock signs --> sunglasses
        #two mini heart signs --> anime sparkles
        #two thumbs up --> confetti effect
        #two peace signs --> (mustang) horse filter

        #sunglasses + horse: facial overlays
        #confettit + sparkles: animated effects

        hands, frame = window.hd.findHands(frame, draw=False)
        
        if len(hands) <2:
            return frame
        
        hand1 = hands[0]
        hand2 = hands[1]

        fingers1 = window.hd.fingersUp(hand1)
        fingers2 = window.hd.fingersUp(hand2)

        peace = fingers1 == [0,1,1,0,0] and fingers2 == [0,1,1,0,0]
        rock = fingers1 == [0,1,0,0,1] and fingers2 == [0,1,0,0,1]
        thumbs = fingers1 == [1,0,0,0,0] and fingers2 == [1,0,0,0,0]
        hearts = window.detectHearts(hands, frame)

        if rock:
            frame = window.sunglass(frame)
        elif hearts:
            frame = window.sparkle(frame)
        elif thumbs:
            frame = window.confetti(frame)
        elif peace:
            frame = window.horse(frame)
        
        frame = cv2.convertScaleAbs(frame, alpha=1, beta=window.brightness)
        return frame

    def detectHearts(window, hands, frame):
        if len(hands) < 2:
            return False
        
        heartCount = 0

        for hand in hands [:2]:
            lm = hand['lmList']
            fingers = window.hd.fingersUp(hand)

            wrist = lm[0][0:2]
            thumbTip = lm[4][0:2]
            index = lm[8][0:2]
            middle = lm[9][0:2]

            handSize = np.hypot(wrist[0]-middle[0], wrist[1]-middle[1])
            thumbIndexDist = np.hypot(thumbTip[0]-index[0], thumbTip[1]-index[1])

            miniHeart = (fingers == [1,1,0,0,0] and thumbIndexDist)
            if miniHeart:
                heartCount += 1

        return heartCount == 2

#frame 
    def showFrame(window, color):
        """
        Updates the frame color for the photostrip.
        """
        window.frameColor = color
        window.photostrip()

#filter 
    def showFilter(window, filter):
        """
        Updates the filter applied to the photos in the photostrip.
        """
        window.filter = filter
        window.photostrip()

    def applyFilter(window, photo):
        """
        applies the selected filter to the given photo.
        Function: Takes an input photo and applies the currently selected filter to it based on the value of window.filter. The function supports multiple filters including "Regular" (no filter), "B&W" (black and white), "Vintage" (a combination of contrast, color adjustments, grain, blur, and overlay), and "2016" (a combination of blur, color adjustments, and overlay). The processed photo is then returned for use in the photostrip generation.

        B&W => grayscale conversion
        Vintage => grayscale, contrast/brightness adjustment, color tinting, grain effect, blur, and vintage overlay
        2016 => blur, color adjustments, and overlay 
        """
        if window.filter == "Regular":
            return photo
        elif window.filter == "B&W":
            photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
            photo = cv2.cvtColor(photo, cv2.COLOR_GRAY2BGR)
            return photo
        elif window.filter == "Vintage":
            grey = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
            grey = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
            photo = cv2.addWeighted(photo, 0.05, grey, 0.95, 0)

            #contrast and brightness
            photo = cv2.convertScaleAbs(photo, alpha = 1.2, beta = 15) 
            photo = photo.astype(np.float32)/ 255.0
            p14, p95 = np.percentile(photo, (10, 95))
            photo = exposure.rescale_intensity(photo, in_range=(p14, p95))

            # #coloring adjustments 
            photo[:,:,2] *= 1.1 #red
            photo[:,:,1] *= 1.03 #green
            photo[:,:,0] *= 0.97 #blue
            photo = np.clip(photo, 0, 255)
            photo = np.clip(photo, 0, 1)  
            photo = (photo*255).astype(np.uint8)

            #grain and blur 
            gphoto = photo / 255.0
            grain = np.random.normal(0, 0.05, (gphoto.shape[0], gphoto.shape[1])) #array of random values with mean 0 and std 0.05 for each pixel
            for i in range(3):
                gphoto[:, :, i] += grain #add to each color channel to create the grain effect
            gphoto = np.clip(gphoto, 0, 1) 
            photo = (gphoto * 255).astype(np.uint8)

            blur = cv2.GaussianBlur(photo, (3,3), 0) #blur
            photo = cv2.addWeighted(photo, 0.2, blur, 0.8, 0)

            #overlay
            overlay = cv2.imread("vintageoverlay.png")
            overlay = cv2.resize(overlay, (photo.shape[1], photo.shape[0]))
            photo = cv2.addWeighted(photo, 0.85, overlay, 0.15, 0)

            return photo
            
        
        elif window.filter == "2016":
            blur = cv2.GaussianBlur(photo, (21,21), 0) #blur
            photo = cv2.addWeighted(photo, 0.75, blur, 0.25, 0)
            
            #coloring
            photo = photo.astype(np.float32) 
            hsv = cv2.cvtColor(photo.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:,:,1] *= 1.1 #saturation
            
            photo[:, :, 2] *= 1.25
            photo[:, :, 1] *= 1.1
            photo[:, :, 0] *= 1

            photo = np.clip(photo, 0, 255).astype(np.uint8)

            #overlay
            overlay = cv2.imread("2016overlay.png")
            overlay = cv2.resize(overlay, (photo.shape[1], photo.shape[0]))
            photo = cv2.addWeighted(photo, 0.7, overlay, 0.3, 0)

            #contrast and brightness
            photo = cv2.convertScaleAbs(photo, alpha = 1.2, beta = 12) 
            return photo

#sticker     
    def mousePressEvent(window, event):
        """
        Mouse event handler for placing stickers on the photostrip.
        """
        sticker = getattr(window, "currentSticker", None)
        image = getattr(window, "pixmapPhotostrip", None)

        if sticker is None or image is None:
            return
       
        position = window.customImageLabel.mapFromGlobal(event.globalPosition().toPoint())

        scaledPixmap = window.pixmapPhotostrip.scaled(
        window.customImageLabel.width(),
        window.customImageLabel.height(),
        Qt.AspectRatioMode.KeepAspectRatio
        )   

        w = scaledPixmap.width()
        h = scaledPixmap.height()

        offsetY = (window.customImageLabel.height() - h) / 2

        imgx = position.x() 
        imgy = position.y() - offsetY

        if imgx < 0 or imgy < 0 or imgx > w or imgy > h:
            return

        x = int(imgx * window.pixmapPhotostrip.width() / w)
        y = int(imgy * window.pixmapPhotostrip.height() / h)
    
        window.showSticker(x, y)

    def selectSticker(window, sticker, size):    
        """
        Selects a sticker to be placed on the photostrip.
        """
        window.currentSticker = sticker
        window.currentStickerSize = int(size)

    def showSticker(window, x, y):
        """
        Places the selected sticker on the photostrip at the specified coordinates.
        """ 
        if not hasattr(window, "currentSticker"):
            return

        stickersize = window.currentStickerSize
        scaledSticker = window.currentSticker.scaled(stickersize, stickersize, Qt.AspectRatioMode.KeepAspectRatio)
        painter = QPainter(window.pixmapPhotostrip)
        painter.drawPixmap(int(x - stickersize/2), int(y - stickersize/2), scaledSticker)
        painter.end()

        qimage = window.pixmapPhotostrip.toImage().convertToFormat(QImage.Format.Format_BGR888)
        width = qimage.width()
        height = qimage.height()
        p = qimage.bits()
        p.setsize(height * width * 3) 
        array = np.frombuffer(p, dtype=np.uint8).reshape((height, width, 3))
        window.photostripImage = array[:, :, :3].copy() 

        window.customImageLabel.setPixmap(window.pixmapPhotostrip.scaled(window.customImageLabel.width(), window.customImageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))

#photostrip generation        
    def photostripHelper(window):
        """
        helper function to transition from camera page to customization page and generate the photostrip.
        """
        window.stack.setCurrentIndex(2)
        window.photostrip()

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
        window.stripHeight = (height * 4) + (spacing * 5)
        window.stripWidth = width + 220

        window.photostripImage = np.full((window.stripHeight, window.stripWidth, 3), window.frameColor, dtype=np.uint8)

        y = 60
        x = 110

        for photo in readPhotos:
            filteredPhoto = window.applyFilter(photo)
            window.photostripImage[y:y+height, x: x+width] = filteredPhoto
            y += height + spacing

        #preview photostrip
        height, width, channels = window.photostripImage.shape
        previewPhotostrip = QImage(window.photostripImage.data, width, height, QImage.Format.Format_BGR888)
        window.pixmapPhotostrip = QPixmap.fromImage(previewPhotostrip)
        window.customImageLabel.setPixmap(window.pixmapPhotostrip.scaled(window.customImageLabel.width(), window.customImageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
       
    def printPhotostrip(window): 
        """
         Displays the generated photostrip in the GUI and saves it.

         Function: Converts the generated photostrip image into a format suitable for display in the PyQt interface and updates the imageLabel widget to show the photostrip preview to the user. This function is called after the photostrip is generated and saved to disk, allowing the user to see the final result of their photobooth session before everything is reset for the next session.
         """
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"photostrip_{timestamp}.png"
        cv2.imwrite(filename, window.photostripImage)

        window.stack.setCurrentIndex(3)

        window.mascotFrame = 0
        window.dotsCount = 0

        window.mascotTimer = QTimer()
        window.mascotTimer.timeout.connect(window.animateMascot)
        window.mascotTimer.start(500)

        window.dotsTimer = QTimer()
        window.dotsTimer.timeout.connect(window.animateDots)
        window.dotsTimer.start(500)

        window.printThread = PrintThread(filename)
        window.printThread.done.connect(window.reset)
        window.printThread.start()

    def animateMascot(window):
        mascots = ["mascot.png", "mascot2.png"]
        window.mascotFrame = (window.mascotFrame + 1) % 2
        pixmap = QPixmap(mascots[window.mascotFrame])
        scaledMascot = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        window.mascotLabel.setPixmap(scaledMascot)

    def animateDots(window):
        dots = ["●", "● ●", "● ● ●"]
        window.dotsCount = (window.dotsCount + 1) % 3
        window.dotsLabel.setText(dots[window.dotsCount])

    def reset(window):
        """
        Resets the photobooth application to its initial state after showing the photostrip preview.

        Function: Clears all captured photos, resets counters and timers, releases the webcam if it's still active, and shows the welcome message and start button again to allow for a new photobooth session to begin.

        """

        #hide all the customization buttons
        window.stack.setCurrentIndex(0)

        if window.video is not None:
            window.video.release()
            window.video = None
            
        window.countdownLabel.clear()
        window.imageLabel.clear()
        window.customImageLabel.clear()
        window.captureIndex = 0
        window.countdown = 3
        window.photos.clear()
        window.filter = "Regular"
        window.frameColor = (255,255,255)
        window.currentSticker = None

    def testFilter(window):
        if window.frame is None:
         return
    
        window.timer.stop()
        filtered = window.applyFilter(window.frame.copy())

        height, width, channels = filtered.shape
        image = QImage(filtered.data, width, height, QImage.Format.Format_BGR888)

        window.imageLabel.setPixmap(
            QPixmap.fromImage(image).scaled(
                window.imageLabel.width(),
                window.imageLabel.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
        )
        

def main():
# Initializes the PyQt application and creates the main window for the photobooth.
     app = QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec())

#run
if __name__ == "__main__":
    main()


