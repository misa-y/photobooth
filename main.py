import cv2
import time
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt

class Window(QWidget):
    def __init__(window):
        super().__init__()

        window.photo_count = 0 #total number of photostrips
        window.captureIndex = 0 #number of photos taken in current photostrip
        window.setWindowTitle("ASIJ Photobooth")
        
        window.layout = QVBoxLayout()
        window.setLayout(window.layout)
        window.setFixedSize(1470,895)   
        
        label = QLabel("Welcome to ASIJ Photobooth")
        window.layout.addWidget(label)

        window.button = QPushButton("Start", window)
        window.button.clicked.connect(window.clicked)
        window.layout.addWidget(window.button)

        window.timer = QTimer()
        window.timer.timeout.connect(window.cameraLoop)
        
        window.imageLabel = QLabel()
        window.imageLabel.setFixedSize(510, 420)
        window.layout.addWidget(window.imageLabel)

    def clicked(window):
        window.button.setText("camera loading...")
        window.button.setEnabled(False)
        
        startCamera(window)

    def cameraLoop(window):
        ret, window.frame = window.video.read()
        if not ret:
            return
        
        window.frame = cv2.flip(window.frame,1)
       
        height, width, channels = window.frame.shape
        image = QImage(window.frame.data, width, height, QImage.Format.Format_BGR888)

        pixmap = QPixmap.fromImage(image)
        window.imageLabel.setPixmap(pixmap.scaled(window.imageLabel.width(), window.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
   
    def keyPressEvent(window, event):
        if event.key() == Qt.Key.Key_P:
            window.captureIndex = 0 #reset capture index for new photostrip
            window.captureImages()
        
        elif event.key() == Qt.Key.Key_Q:
            window.timer.stop()
            window.video.release()
            window.close()
            exit

    def captureImages(window):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"photo_{timestamp}.png"
        cv2.imwrite(filename, window.frame)
        print (f"Saved {filename}")

        window.captureIndex += 1 

        if window.captureIndex < 4:
            QTimer.singleShot(2000, window.captureImages)            
        elif window.captureIndex == 4:
            print ("Done capturing photos")
            window.captureIndex = 0
            window.photo_count+=1
            print(f"Current # of Photo Strips: {window.photo_count}")
            return

def main():
     app = QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec())

def startCamera(window):
     window.video = cv2.VideoCapture(0)
     window.video.set(cv2.CAP_PROP_FRAME_WIDTH, 510)
     window.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 420)
     
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