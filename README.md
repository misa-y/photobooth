# Interactive Photo Booth for School Events
A real-time, webcam-based interactive photobooth built with Python that captures images, applies AI-powered visual effects, and generates downloadable photostrips. Designed for school events and interactive installations.

## Features
- Live webcam preview using OpenCV
- Countdown-based photo capture system
- Automatic photostrip generation
- Custom frame color selection
- Real-time AR-style visual effects
- Gesture-controlled filters (hand + face tracking)
- AI-based face and hand detection for interaction
- Photo/video preview system before download

## Controls
Q → Quit application

## Requirements
Python 3.9+
OpenCV
PyQt6
NumPy
MediaPipe
HTTP Server

## User Flow
User launches the application and starts the program
The user is directed to the ModePage where they can select which mode to use for the photobooth (regular, brightness, filters, instructions availavle via hovering over the card)
Live webcam feed starts and displays the user in real time
System continuously detects faces and hand gestures in the background
Depending on gestures, real-time effects may appear if in "filters" mode(e.g. sunglasses, horse filter, sparkles, confetti)
User starts the capture sequence (pressing "take pictures")
A countdown runs before each photo is taken
Multiple photos are captured in a timed sequence
Captured images are shown in a preview screen
Photos are automatically combined into a photostrip layout with selected frame styling
The user can customize their photostrip by choosing the frame color, applying a coloring filter over the photostrip, and adding stickers
A local server is activated to host the output files
A QR code is generated so users can instantly download the photo and the video from their phone
WARNING: Sometimes the video takes longer to load so please be patient when downloading!

## Roadmap
Pre-Project
Goal: Research on the necessary skills needed to start. (like finding tools, e.g., open source libraries, etc.)
Include…
- Find tools to possibly use, name them & explain potential uses
- Start documentation notebook
- Outline how the photobooth should look visually

Core Photobooth Functionality 
Goal: Code a reliable photobooth that behaves like a traditional booth.
Include..
- Live webcam feed using OpenCV
- Camera orientation correction
- Windowing application using PyQt6
- Countdown timer before capture
- Capture a sequence of pictures
- Have the photo previews before download
- Generate photostrip with short preview

Visual Effects & Custom Filters
Goal: Add intelligence and interaction beyond a normal photobooth. Filters, gesture signals, etc! 
Include..
- Make basic photobooth visually appealing
- School-themed designs
- Gesture detection
- Map gestures for filters
- Filter preview before capture
- Explore computer vision techniques for face-based effects
- Apply real-time visual effects to the live camera feed
- Update README to include usage instructions

Hardware Integration 
Goal: Build a physical booth where users can use it. 
Include..
- Prepare the system for deployment on a standalone display
- Integrate external hardware components (e.g., LEDs, sensors, etc)
- Explore running the system on embedded platforms (Raspberry Pi)
- Optimize performance for real-time, public-facing use

## Project Status
The software portion of the photobooth is fully developed and functional.
Immediate Next Step: Cut paper to fit in our printer to be able to print the right size for the photostrips!