import sys, os
import cv2
import numpy as np
import pandas as pd
sys.path.append('../train/')
from preproc_6ax_data import load_and_preproc_data_single, resample_df

def reshape_function(data, label):
    reshaped_data = tf.reshape(data, [-1, 6, 1])
    return reshaped_data, label

def pad_predictions(predictions, seq_length):
    return np.vstack((np.zeros((seq_length,4)),np.asarray(predictions)))

def predict_from_df(df, model, seq_length):
    data = df[['ax','ay','az','gx','gy','gz']].values
    data_batch = []
    labels = []
    for i in range(len(data)-seq_length):
        data_batch.append(data[i:(seq_length+i)])
        labels.append(-1)
    batch_size = 64
    dataset = tf.data.Dataset.from_tensor_slices((data_batch, np.asarray(labels).astype("int32")))
    dataset = dataset.map(reshape_function).batch(batch_size)
    predictions = model.predict(dataset)
    return pad_predictions(predictions, seq_length)


class video_reader:
    def __init__(self, filename_vid, synchframe = 0, filename_silks = None, model_predict = False):
        self.cap = cv2.VideoCapture(filename_vid)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.synchframe = synchframe
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        ## read in the inertial sensor data
        if filename_silks:
            df, b1_press_t, b2_press_t = load_and_preproc_data_single(filename_silks)
            buttons_t = sorted(list(b1_press_t) + list(b2_press_t))
        
            ## filter the values after buttons_t button press (synchronization cue)
            df = df.loc[df.index > buttons_t[0]]
            df.index = df.index - buttons_t[0]
            buttons_t = [a-buttons_t[0] for a in buttons_t]
        
            self.buttons_t = buttons_t
            self.t_vid = np.arange(0, df.index[-1], 1/self.get_fps())
            self.df = df
    
    def make_model_predictions(self):
        model, model_path = build_cnn(60)
        model.load_weights('../train/{}/weights.h5'.format(model_path))
        
        df = self.df
        df.reset_index(inplace = True)
        
        if not 'p_select' in df:
            df = resample_df(df, 'linear', 119.)
        else:
            df.drop(['p0','p1','p2','p3'], axis = 1, inplace = True)
            
        predictions = predict_from_df(df,model, 60)
        df = pd.concat((df.reset_index(), pd.DataFrame(predictions, columns = ['p0','p1','p2','p3'])), axis = 1)
        df['p_select'] = np.argmax(predictions, axis=1)
        df['p_color'] = df['p_select'].apply(lambda x: sns.color_palette("tab10", 10)[x if x<2 else 2*x])
        df.set_index('t', inplace = True)
        self.df = df
        
    def get_nframes(self):
        return self.frame_count - self.synchframe
    def get_width(self):
        return self.frame_width
    def get_height(self):
        return self.frame_height
    def get_fps(self):
        return self.fps
    def get_buttons_t(self):
        return self.buttons_t
    def get_df(self):
        return self.df
    
    def read_frames(self, init_frame, N_frames, limit_field = False, bbox = [0,800,550,1250]):
        self.cap.set(1,init_frame+self.synchframe)
        
        frames = []
        j = 0
        while(self.cap.isOpened()):
            ret, frame = self.cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            j+=1
            if j > N_frames: break
                
            if limit_field:
                frames.append(frame[bbox[0]:bbox[1],bbox[2]:bbox[3],:])
            else:
                frames.append(frame)
        cv2.destroyAllWindows()
        return frames
    
    def read_data_timerange(self, init_time, N_frames):
        init_frame = np.where(self.t_vid > init_time)[0][0]
        max_time = init_time+N_frames/(self.get_fps())

        frames = self.read_frames(init_frame, N_frames)        
        df_clip = self.df.query('t >= {} and t <={}'.format(init_time, max_time))
        df_clip.index = df_clip.index - df_clip.index[0]
        return frames, df_clip