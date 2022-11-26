from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from icecream import ic
import trio
import os
import numpy as np
import cv2

import time

Builder.load_string("""
<MainScreen>:
    img: img.__self__
    lbl: lbl.__self__
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: img
        Button:
            id: lbl
            text: "hello world!"
""")

class MainScreen(F.Screen):
    pass

class Main(App):
    our_texture = F.ObjectProperty(None)
    frame_number = F.NumericProperty()
    times = F.ListProperty()

    def __init__(self, nursery):
        super().__init__()
        self.nursery = nursery

    def build(self):
        self.screen_manager = F.ScreenManager()
        self.main_screen = MainScreen(name='main_screen')
        self.screen_manager.add_widget(self.main_screen)
        Clock.schedule_once(self.start_camera, 1)
        Window.bind(on_request_close=self.on_request_close)
        return self.screen_manager

    def on_request_close(self, *args):
        self.stream.release()

    def start_camera(self, dt):
        print('Loading camera...')
        self.main_screen.lbl.text = "Loading modules"
        # Clock.schedule_once(self.load_modules)
        Clock.schedule_interval(self.update_texture, 1/30)

    def update_texture(self, dt):
        # load frame_n.raw, which is numpy.ndarray from frames folder
        print(f'Updating texture... {self.frame_number}')
        t1 = time.time()
        try:
            image = np.load(f'frames/frame_{len(os.listdir("frames"))-1}.raw.npy')
            # print(image)
            # frame = cv2.flip(frame, 0)
            # frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            buf = image.tobytes()

            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            texture1.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            texture1.flip_vertical()
            self.main_screen.img.texture = texture1

            self.frame_number += 1
        except Exception as e:
            pass
        t2 = time.time()
        self.times.append(t2-t1)
        total_time = sum(self.times)
        fps = len(self.times)/total_time
        print(f'FPS: {fps}')
        

    def load_modules(self, dt):
        global cv2
        import mediapipe as mp # Import mediapipe
        import cv2
        self.mp_drawing = mp.solutions.drawing_utils 
        self.mp_holistic = mp.solutions.holistic 
        self.stream = cv2.VideoCapture(0)

        # import numpy as np 
        return_of, image = self.stream.read()

        # self.main_screen.img.texture = frame

        # ic(return_of, frame)

        # image = np.full((400,400, 3), [255, 255, 255], dtype=np.uint8)
        # buf = image.tobytes()
        # texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr') 
        # texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # self.main_screen.img.texture = texture1

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        buf = image.tobytes()
        texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb') 
        texture1.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.main_screen.img.texture = texture1



        self.main_screen.lbl.text = "mediapipe and cv2 loaded"
        print('mediapipe and cv2 loaded')

        # Clock.schedule_interval(self.create_trio_f, 1/60)
        Clock.schedule_interval(self.anti_trio_texture, 1/60)

    def create_trio_f(self, *args):
        self.nursery.start_soon(self.update_textureee)
        # Clock.schedule_interval(self.read_and_analyze_camera, 1/5)
        # Clock.schedule_interval(self.update_textureee, 1/30)

    def anti_trio_texture(self, *args):
        time_1 = time.time()
        frame = self.stream.read()[1]
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            frame = cv2.flip(frame, 0)
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



            image.flags.writeable = False
            results = holistic.process(image)
            image.flags.writeable = True
            # print("timedelta wtf why is this so fast!", time_2 - time_1, 1/60,  flush= True)

            self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                 self.mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                 self.mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                 )
            self.mp_drawing.draw_landmarks(image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                    self.mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                    self.mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                    )
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS, 
                                    self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )

            buf = image.tobytes()
            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            texture1.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.our_texture = texture1
            self.main_screen.img.texture = self.our_texture

        time_2 = time.time()
        self.times.append(time_2-time_1)
        print("fps", 1/(sum(self.times)/len(self.times)), flush=True)

    async def update_textureee(self, *args):
        time_1 = time.time()
        frame = self.stream.read()[1]
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            # frame = cv2.flip(frame, 0)
            # frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



            image.flags.writeable = False
            results = holistic.process(image)
            image.flags.writeable = True
            # print("timedelta wtf why is this so fast!", time_2 - time_1, 1/60,  flush= True)

            # self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
            #                      self.mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
            #                      self.mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
            #                      )
            # self.mp_drawing.draw_landmarks(image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
            #                         self.mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
            #                         self.mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
            #                         )
            # self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS, 
            #                         self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
            #                         self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            #                         )

            buf = image.tobytes()
            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            texture1.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.our_texture = texture1
            self.main_screen.img.texture = self.our_texture

        time_2 = time.time()
        self.times.append(time_2-time_1)
        print("fps", 1/(sum(self.times)/len(self.times)), flush=True)
        # ic(self.times)
        # ic(len(self.times))
        # ic(sum(self.times))

            # print('Updated texture to: ', self.our_texture)
                
            # if self.our_texture:
            #     print('Updating texture')
            #     self.main_screen.img.texture = self.our_texture
            # else:
            #     print('No texture to update')
            
            # return True

    async def read_camera(self, *args):
        while True:
            frame = self.stream.read()[1]
            # frame = cv2.flip(frame, 0)
            # frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            buf = image.tobytes()

            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
            texture1.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            texture1.flip_vertical()
            self.our_texture = texture1
            
            print('Updated texture to: ', self.our_texture)
            

    
    # def read_and_analyze_camera(self, *args):
    async def read_and_analyze_camera(self, *args):
        print('Starting camera...')
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while True:
                ret, frame = self.stream.read()
                if ret:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    time_1 = time.time()
                    # results = holistic.process(image)
                    time_2 = time.time()
                    print("timedelta wtf why is this so fast!", time_2 - time_1, 1/60,  flush= True)            
                    image.flags.writeable = True
                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    # self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                    #              self.mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                    #              self.mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                    #              )

                    buf = image.tobytes()
                    texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr') 
                    texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                    self.main_screen.img.texture = texture1



# Start kivy app as an asynchronous task
async def main() -> None:
    async with trio.open_nursery() as nursery:
        server = Main(nursery)
        await server.async_run('trio')
        nursery.cancel_scope.cancel()

try:
    trio.run(main)
except Exception as e:
    import traceback
    ic(traceback.format_exc())
    print('\n Matando o APP ************** ?')
    raise

