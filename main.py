import cv2
import numpy as np
import time
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt

class Window(QWidget):
    def __init__(window):
        super().__init__()

        window.photo_count = 0 #total number of photostrips
        window.photos = [] #array to save filenames for photostrip generation
        window.captureIndex = 0 #number of photos taken in current photostrip
        window.countdown = 3 #7 seconds between each picture
        
        window.video = None
        window.setWindowTitle("ASIJ Photobooth")
        
        window.layout = QVBoxLayout()
        window.setLayout(window.layout)
        window.setFixedSize(1470,895)   
        
        window.welcome = QLabel("Welcome to ASIJ Photobooth")
        window.layout.addWidget(window.welcome, alignment = Qt.AlignmentFlag.AlignCenter)

        window.button = QPushButton("Start", window)
        window.button.clicked.connect(window.clicked)
        window.layout.addWidget(window.button, alignment = Qt.AlignmentFlag.AlignCenter)

        window.countdownLabel = QLabel("")
        window.layout.addWidget(window.countdownLabel, alignment = Qt.AlignmentFlag.AlignCenter)

        window.timer = QTimer()
        window.timer.timeout.connect(window.cameraLoop)
        
        window.imageLabel = QLabel()
        window.imageLabel.setFixedSize(867, 714)
        window.layout.addWidget(window.imageLabel, alignment = Qt.AlignmentFlag.AlignCenter)

    def clicked(window):
        window.welcome.setHidden(True)
        window.button.setHidden(True)
        
        startCamera(window)

    def cameraLoop(window):
        ret, window.frame = window.video.read()
        if not ret:
            return
        
        window.frame = cv2.flip(window.frame,1)
       
        height, width, channels = window.frame.shape
        image = QImage(window.frame.data, width, height, QImage.Format.Format_BGR888)

        window.feed = QPixmap.fromImage(image)
        window.imageLabel.setPixmap(window.feed.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
   
    def keyPressEvent(window, event):
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
        if window.countdown > 0:
            window.countdownLabel.setText(str(window.countdown))
            window.countdown -= 1
            QTimer.singleShot(1000, window.startCountdown)
        
        elif window.countdown == 0:
            window.countdownLabel.setText("")
            window.captureImages()

    def preview(window):
        window.countdownLabel.setText("Preview")
        previewImage = QPixmap(window.filename)
        window.imageLabel.setPixmap(previewImage.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def photostrip(window):
        readPhotos = [] 

        for file in window.photos:
            read = cv2.imread(file)
            readPhotos.append(read)

        height, width, channels = readPhotos[0].shape
        spacing = 60
        stripheight = (height * 4) + (spacing * 5)

        photostrip = np.zeros((stripheight, width+220, 3), dtype=np.uint8)

        y = 60
        x = 110

        for photo in readPhotos:
            photostrip[y:y+height, x: x+width] = photo
            y += height + spacing
        
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"photostrip_{timestamp}.png"
        cv2.imwrite(filename, photostrip)
        
        #resets
        window.welcome.setHidden(False)
        window.button.setHidden(False)

        if window.video is not None:
            window.video.release()
            window.video = None
            
        window.countdownLabel.clear()
        window.imageLabel.clear()

        window.captureIndex = 0
        window.photo_count+=1
        window.countdown = 3
       
        window.photos.clear()

    def resumeCamera(window):
        window.countdown = 3
        window.timer.start(30)
        window.startCountdown()

    def captureImages(window):
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
            QTimer.singleShot(2500,window.photostrip)
            
            print(f"Current # of Photo Strips: {window.photo_count}")
            return
        
def main():
     app = QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec())

def startCamera(window):
     if window.video is None:
        window.video = cv2.VideoCapture(0)
     
     window.video.set(cv2.CAP_PROP_FRAME_WIDTH, 867) #510*1.7
     window.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 714) #420*1.7
     
     window.timer.start (30) #update every 30ms

     if not window.video.isOpened():
        print("Error Opening the Camera")
        return

#run
if __name__ == "__main__":
    main()

 # def captureImages(video):
    # for i in range (4):
    #             start_time= time.time()
              
    #             while time.time() - start_time < 2: 
    #                 ret, frame = video.read()
    #                 frame = cv2.flip(frame, 1)
    #                 cv2.imshow("ASIJ Photobooth", frame)
    #                 cv2.waitKey(1)

#                 # take photo
#                 ret, frame = video.read()
#                 frame = cv2.flip(frame, 1)
#                 timestamp = time.strftime("%Y%m%d%H%M%S")
#                 filename = f"photo_{timestamp}.png"
#                 cv2.imwrite(filename, frame)

#                 print (f"Saved {filename}")



 # def startCamera():
#     video = cv2.VideoCapture(0)
#     photo_count = 0 #total number of photostrips

#     if not video.isOpened():
#         print("Error Opening the Camera")
#         return

#     while True:
#         ret, frame = video.read()
#         frame = cv2.flip(frame,1)

#         cv2.imshow("ASIJ Photobooth", frame)
                         
#         key = cv2.waitKey(1) & 0xFF
#         if key == ord('p'):
#             #countdown(video)
#             captureImages(video)
#             photo_count+=1

#             print(photo_count)
        
#         elif key == ord('q'):
#             break
   
#     video.release()
#     cv2.destroyAllWindows()