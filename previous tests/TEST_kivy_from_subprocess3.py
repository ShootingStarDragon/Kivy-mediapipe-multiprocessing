# https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from datetime import datetime

class MainApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device_index = 0
        self.frame_int = 0
        #remember that the KV string IS THE ACTUAL FILE AND MUST BE INDENTED PROPERLY TO THE LEFT!
        self.KV_string = '''
<FCVA_screen_manager>:
    id: FCVA_screen_managerID
    StartScreen:
        id: start_screen_id
        name: 'start_screen_name'
        manager: 'FCVA_screen_managerID'

<StartScreen>:
    id: start_screen_id
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: image_textureID
        Label:
            text: "hello world!"

FCVA_screen_manager: #remember to return a root widget
'''
    def build(self):
        self.title = "Fast CV App v0.1.0 by Pengindoramu"
        build_app_from_kv = Builder.load_string(self.KV_string)
        # Window.bind(on_request_close=self.on_request_close)
        return build_app_from_kv
    
    def on_start(self):
        # opening a camera here is laggy and delays the startup time so start after the gui is loaded with this
        print("schedule interval 0", datetime.now().strftime("%H:%M:%S"))
        Clock.schedule_interval(self.blit_from_shared_memory, 1/30)

    # def build(self):
    #     return Label(text='Main App Window')
    def run(self):
        '''Launches the app in standalone mode.
        '''
        self._run_prepare()
        from kivy.base import runTouchApp
        runTouchApp()
        # self.stop()
    def blit_from_shared_memory(self, *args):
        # ret, frame = self.stream.read(0)
        #problem is I don't think you can pickle the stream for multiprocessing (it's a tuple, idk if you can send tuples in a tuple), so send the frame instead
        # https://stackoverflow.com/questions/17872056/how-to-check-if-an-object-is-pickleable
        # import dill
        # # print("dill pickles!", dill.pickles(self.stream)) #says false, so I can't send the stream, but I can still send the individual frame
        # dilling = dill.pickles(parallelize_cv_func)
        # # print(dilling)
        # if dilling:
        #     self.what = FCVApool.apply_async(parallelize_cv_func, args=(cv_func_mp, ret, frame, shared_analysis_dict, self.frame_int)) 
        # else:
        #     print(f"dill says function is unpickleable")
        # self.frame_int += 1
        # print("what are blit args?", args, flush= True)
        shared_analysis_dict = self.shared_analysis_dictVAR
        if len(shared_analysis_dict) > 0:
            max_key = max(shared_analysis_dict.keys())
            frame = shared_analysis_dict[max_key]
            buf = frame.tobytes()
            #texture documentation: https://github.com/kivy/kivy/blob/master/kivy/graphics/texture.pyx
            #blit to texture
            #blit buffer example: https://stackoverflow.com/questions/61122285/kivy-camera-application-with-opencv-in-android-shows-black-screen
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = texture1
            #after blitting delete some key/value pairs if dict has more than 10 frames:
            if len(shared_analysis_dict) > 5:
                min_key = min(shared_analysis_dict.keys())
                del shared_analysis_dict[min_key]

class OtherApp(App):
    def build(self):
        return Label(text='Other App Window')

class FCVA_screen_manager(ScreenManager):
    pass

class StartScreen(Screen):
    pass


def open_parent(*args):
    # print("what args?", args, flush = True)
    MainApp.shared_analysis_dictVAR = args[0]
    MainApp().run()

if __name__ == '__main__':
    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support()
    # FCVApool = FCVA_mp.Pool(1)
    shared_mem_manager = FCVA_mp.Manager()
    shared_analysis_dict = shared_mem_manager.dict()
    a = FCVA_mp.Process(target=open_parent, args=(shared_analysis_dict,))
    # b = multiprocessing.Process(target=open_child)
    a.start()

    # https://www.youtube.com/watch?v=We1uB79Ci-w
    # https://github.com/nicknochnack/Body-Language-Decoder/blob/main/Body%20Language%20Decoder%20Tutorial.ipynb
    # why is this so fast? 0.06673789024353027 0.016666666666666666

    #import list:
    import mediapipe as mp # Import mediapipe
    import cv2 # Import opencv

    import time
    mp_drawing = mp.solutions.drawing_utils # Drawing helpers
    mp_holistic = mp.solutions.holistic # Mediapipe Solutions

    cap = cv2.VideoCapture(0)

    # Initiate holistic model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            # Recolor Feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False        
            
            time_1 = time.time()
            # Make Detections
            results = holistic.process(image)
            time_2 = time.time()

            # Recolor image back to BGR for rendering
            image.flags.writeable = True   
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 2. Right hand
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                    )

            # 3. Left Hand
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                    )

            # 4. Pose Detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )
                            
            shared_analysis_dict[1] = cv2.flip(image,0)
            print("why is this so fast? fps:", 1/(time_2 - time_1), len(shared_analysis_dict),  flush= True)
            # cv2.imshow('Raw Webcam Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


    #problem was I get here and then it kills kivy
    import time
    time.sleep(1000)


    