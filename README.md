# Kivy-mediapipe-multiprocessing
Thanks to RobertFlatt on the Kivy Discord for helping me make multiprocessing work

How to run FINALTEST_mediapipe_kivy_multiprocessing.py: <br />
#0a. Make sure you have a camera that can be opened by OpenCV VideoCapture() <br />
#0b. git clone this repo <br />
#0c. cd to the folder you cloned <br />
#1. Install poetry (https://python-poetry.org/) <br />
#2: In your terminal, `poetry install` <br />
#3: In your terminal, `poetry shell` <br />
#4: In your terminal, `python FINALTEST_mediapipe_kivy_multiprocessing.py` <br />
#4b: If you are still missing dependencies, `poetry install` again <br />
#5. Kivy will run after 10 seconds, wait 40 seconds for mediapipe to start running, and then you will have instantaneous pose estimation with no lag! Everything is a subprocess so python GIL is not a problem and you can run the Kivy loop and Mediapipe loop at the same time. <br />
