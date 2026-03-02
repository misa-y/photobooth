import cv2
import time

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QImage

import sys

class Window(QWidget):
    def __init__(window):
        super().__init__()

        window.setWindowTitle("ASIJ Photobooth")
        
        layout = QVBoxLayout()
        window.setLayout(layout)
        window.resize(1000,600)   
        
        label = QLabel("Welcome")
        layout.addWidget(label)

        window.button = QPushButton("Start", window)
        window.button.clicked.connect(window.clicked)
        layout.addWidget(window.button)

    def clicked(window):
        window.button.setText("camera loading...")
        window.button.setEnabled(False)
        
        startCamera()

        #enable button again after taking the pics
        window.button.setEnabled(True)
        window.button.setText("Start")

def main():
     app = QApplication(sys.argv)
     window = Window()
     window.show()
     sys.exit(app.exec())

    
def startCamera():
    video = cv2.VideoCapture(0)
    photo_count = 0 #total number of photostrips

    if not video.isOpened():
        print("Error Opening the Camera")
        return

    while True:
        ret, frame = video.read()
        frame = cv2.flip(frame,1)

        cv2.imshow("ASIJ Photobooth", frame)
                         
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            #countdown(video)
            captureImages(video)
            photo_count+=1

            print(photo_count)
        
        elif key == ord('q'):
            break
   
    video.release()
    cv2.destroyAllWindows()

def captureImages(video):
    for i in range (4):
                start_time= time.time()
              
                while time.time() - start_time < 2: 
                    ret, frame = video.read()
                    frame = cv2.flip(frame, 1)
                    cv2.imshow("ASIJ Photobooth", frame)
                    cv2.waitKey(1)

                # take photo
                ret, frame = video.read()
                frame = cv2.flip(frame, 1)
                timestamp = time.strftime("%Y%m%d%H%M%S")
                filename = f"photo_{timestamp}.png"
                cv2.imwrite(filename, frame)

                print (f"Saved {filename}")

#run
if __name__ == "__main__":
    main()






 