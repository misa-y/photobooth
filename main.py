import cv2  # OpenCV library for accessing camera and image processing

def startCamera():
    """
   startCamera function to run the webcam feed.
   Opens the default camera, and handles quitting. 
    """

    cap = cv2.VideoCapture(0) # 0 is the defaul cam, usually the built-in webcam

    # Check if the webcam is opened correctly, exits if not
    if not cap.isOpened():
        print("Cannot open camera")
        return

    # Main loop to continuously capture frames from the webcam
    while True: 
        ret, frame = cap.read()

        if not ret:
            print("Failed to receive frame")
            break

        frame = cv2.flip(frame, 1) # to mirror horizontally (selfie view, desired camera orientation)
        cv2.imshow("ASIJ Photobooth", frame) # Displays the frame in a window named "ASIJ Photobooth"

        # exits when "q" is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break 

    # When everything done, release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()


startCamera()