import cv2
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
import sys

def main():
     app = QApplication(sys.argv)

     window = QWidget()
     window.setWindowTitle("ASIJ Photobooth")
     
     layout = QVBoxLayout()
     label = QLabel("Welcome")
     
     layout.addWidget(label)
     window.setLayout(layout)
     window.resize(300,150)
     
     window.show()
     sys.exit(app.exec())



     #startCamera()

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

        cv2.createButton("Start", onChange=onChange)
                         
        key = cv2.waitKey(1) & 0xFF
        if key == ord('l'):
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

def onChange():
     print ("hi")


#run
if __name__ == "__main__":
    main()






 