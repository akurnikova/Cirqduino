import pandas as pd
import numpy as np
import glob
import scipy.signal as sig
import os
from scipy import interpolate

SIG_COLS = ['ax','ay','az','gx','gy','gz']

def rescale_values(df):
    ''' Rescale accelerometer and gyro measurements to g and dps
        undoes the preprocessing done on the arduino before conversion to shorts '''
    
    for col in df.columns:
        if col in ['ax','ay','az']:
            df[col] = df[col]/1000
            #df[col + '_medfilt'] = sig.medfilt(df[col],15)
        if col in ['gx','gy','gz']:
            df[col] = df[col]/10
            #df[col + '_medfilt'] = sig.medfilt(df[col],15)
    return df        
    
def load_and_preproc_data_single(file_name = '/home/asya/Desktop/Gyro_Data/bluepy_data/*salto_pancake*'):
    ''' Process single file to a dataframe:
            -- parse the button press information
            -- update the time if there are resets 
            -- rescale the values '''
    df = pd.read_csv(file_name, sep = ',')

    # process buttons
    df['button1'] = (df.button == 2) | (df.button == 0)
    df['button2'] = (df.button == 1) | (df.button == 0)
    df['button1'] = df['button1'].astype(int)
    df['button2'] = df['button2'].astype(int)

    ## preproc time
    df['rec_time_ms'] = round(1000*(df['rec_time'] - df.rec_time.loc[0]))

    t_wrap = np.where(df.t.diff()<-32767)[0]
    for ti in t_wrap:
        df.loc[ti:len(df),'t'] = df.loc[ti:len(df),'t']+2*32768

    ### process reset times
    for i in range(2):
        t_reset = np.where((df.rec_time_ms-df.t).diff()>2000)[0]
        #print(t_reset)
        for tr in t_reset:
            diff_reset = df.loc[tr,'rec_time_ms'] - df.loc[tr,'t']
            t_rec_reset = diff_reset#df.loc[tr,'rec_time_ms'] - df.loc[(tr-1),'rec_time_ms']
            df.loc[tr:len(df),'t'] = df.loc[tr:len(df),'t']+max(diff_reset,t_rec_reset)

    button_press_idx = np.where(df.button2.diff()==-1)[0]
    b2_press_t = df.loc[button_press_idx, 't'].values/1000
    button_press_idx = np.where(df.button1.diff()==-1)[0]
    b1_press_t = df.loc[button_press_idx, 't'].values/1000

    #set index as time
    df['t'] = df['t']/1000
    df.set_index('t', inplace = True)

    ## rescale the values to original magnitudes
    df = rescale_values(df)
    
    return df, b1_press_t, b2_press_t


def load_and_preproc_data_batch(file_type = 'silks_preproc/*salto_pancake*'):
    ''' Process a batch of files to a single dataframe:
            -- parse the button press information
            -- update the time if there are resets 
            -- rescale the values '''
    base = '/home/asya/Desktop/Gyro_Data/bluepy_data/'
    flist = glob.glob(base+file_type)

    arr = []
    t_arr = []
    for fle in flist:
        df_temp = pd.read_csv(fle)
        df_temp['from_file'] = os.path.basename(fle)
        arr.append(df_temp)
        t_arr.append(arr[-1].rec_time.mean())
    arr = sorted(zip(t_arr, arr))
    arr = [element for _, element in arr]

    df = pd.concat(arr)
    df = df.reset_index()

    # process buttons
    df['button1'] = (df.button == 2) | (df.button == 0)
    df['button2'] = (df.button == 1) | (df.button == 0)
    df['button1'] = df['button1'].astype(int)
    df['button2'] = df['button2'].astype(int)

    ## preproc time
    df['rec_time_ms'] = round(1000*(df['rec_time'] - df.rec_time.loc[0]))

    t_wrap = np.where(df.t.diff()<-32767)[0]
    for ti in t_wrap:
        df.loc[ti:len(df),'t'] = df.loc[ti:len(df),'t']+2*32768

    ### process reset times
    for i in range(2):
        t_reset = np.where((df.rec_time_ms-df.t).diff()>2000)[0]
        #print(t_reset)
        for tr in t_reset:
            diff_reset = df.loc[tr,'rec_time_ms'] - df.loc[tr,'t']
            t_rec_reset = diff_reset#df.loc[tr,'rec_time_ms'] - df.loc[(tr-1),'rec_time_ms']
            df.loc[tr:len(df),'t'] = df.loc[tr:len(df),'t']+max(diff_reset,t_rec_reset)

    button_press_idx = np.where(df.button2.diff()==-1)[0]
    b2_press_t = df.loc[button_press_idx, 't'].values/1000
    button_press_idx = np.where(df.button1.diff()==-1)[0]
    b1_press_t = df.loc[button_press_idx, 't'].values/1000

    #set index as time
    df['t'] = df['t']/1000
    df.set_index('t', inplace = True)

    ## rescale the values to original magnitudes
    df = rescale_values(df)
    
    return df, b1_press_t, b2_press_t

def write_clip_to_file(df_clip, clip_type, fle_ind):
    ''' Write clip to file '''
    
    if len(df_clip) < 30: return
    if df_clip.index.max() < df_clip.index.min()+1: return
    
    # make the directory it it doesn't exist
    basedir = '../Gyro_Data/modeling/'
    os.makedirs(os.path.join(basedir, clip_type), exist_ok=True)
    
    # zero the time
    df_clip.index = df_clip.index- df_clip.index[0]
    
    if len(np.where(np.diff(df_clip.index) <0)[0]) > 0:
        ## need to investigate why this occurs
        raise ValueError('Timing Error in clip {}'.format(fle_ind))
        
    df_clip.to_csv('{}/{}/{}.csv'.format(basedir, clip_type, fle_ind))

def write_10s_clips(df, t0,t1, label, ind_s):
    ''' Write clip to file in segments of max 10 seconds'''
    while (t1 - t0) >1: ## avoid segments under 1 seconds
        if t1-t0 > 10: ## want to split into 10 s clips
            write_clip_to_file(df.query('t >= {} and t <= {}'.format(t0, t0+10)), label, ind_s)
            t0 += 10
            ind_s+= 1
        else:
            write_clip_to_file(df.query('t >= {} and t <= {}'.format(t0, t1)), label, ind_s)
            ind_s+=1
            break
    return ind_s

def get_silks_time_range(df, b1_press_t):
    ''' Return the probable time range of the active signal based on button presses'''
    if len(b1_press_t)>1:
        t_range = (b1_press_t[0]+3, df.index.max()-5) #b1_press_t[1]-3)
    elif len(b1_press_t)==1: ## most typical
        t_range = (b1_press_t[0]+3, df.index.max()-5)
    elif len(b1_press_t)==0:
        t_range = (df.index.min()+10, df.index.max()-5)
    return t_range

def proc_parse_salto_clips_custom(t_pre = 1.5, t_post = 4, base = '/home/asya/Desktop/Gyro_Data/bluepy_data/', proc_nonsalto = True):
    ''' Custom function to rewrite clips of the salto traces from the files 
    it looks like saltos can be identified based on a threshold on ax. 
    There is only the correct salto type in the clip files, so it should be okay.
    
    pancake = controlled drop with pike
    nopancake = drop, no pike
    
    t_pre:  select seconds before the salto
    t_post: select seconds after the salto
    base:   silks_preproc folder location 
    
    if proc_nonsalto is true, the other parts of the clips are also written out
    '''
    
    #flist = [a for a in glob.glob(base+'silks_preproc/*salto*') if (('_pancake' in a)&('_nopancake' in a))]
    flist = glob.glob(base+'silks_preproc/*salto*')

    ind_sp = 0
    ind_snp = 0
    
    ind_s = 0 #flist = glob.glob(base+'silks_preproc/*salto*')
        
    for fle in flist:
        df, b1_press_t, b2_press_t = load_and_preproc_data_single(fle)

        potential_flips = np.concatenate(([0],np.where(df.ax <-3.7)[0]))
        potential_flips_loc = np.where(np.diff(potential_flips)>100)[0]+1
        potential_flips_t = df.index[potential_flips[potential_flips_loc]].values

        if '0729_1salto_pancake_2_nopancake_preproc.txt' in fle:
            for t_i in [potential_flips_t[0]]:
                write_clip_to_file(df.query('t > {} and t <{}'.format(t_i-t_pre, t_i+t_post)), 'salto_pike_raw', ind_sp)
                ind_sp+= 1
                
                if proc_nonsalto: df = df.query('t < {} or t > {}'.format(t_i-t_pre-1, t_i+t_post+1))## drop the part of the signal with the salto
                    
            for t_i in potential_flips_t[1:]:
                write_clip_to_file(df.query('t > {} and t <{}'.format(t_i-t_pre, t_i+t_post)), 'salto_drop_raw', ind_snp)
                ind_snp+= 1
                
                if proc_nonsalto: df = df.query('t < {} or t > {}'.format(t_i-t_pre-1, t_i+t_post+1))## drop the part of the signal with the salto


        elif '_pancake' in fle: ## will remap name to pike
            assert not '_nopancake' in fle
            for t_i in potential_flips_t:
                write_clip_to_file(df.query('t > {} and t <{}'.format(t_i-t_pre, t_i+t_post)), 'salto_pike_raw', ind_sp)
                ind_sp+= 1
                
                if proc_nonsalto: df = df.query('t < {} or t > {}'.format(t_i-t_pre-1, t_i+t_post+1))## drop the part of the signal with the salto
                
        elif '_nopancake' in fle: ## will remap name to drop
            assert not '_pancake' in fle
            for t_i in potential_flips_t:
                write_clip_to_file(df.query('t > {} and t <{}'.format(t_i-t_pre, t_i+t_post)), 'salto_drop_raw', ind_snp)
                ind_snp+= 1
                
                if proc_nonsalto: df = df.query('t < {} or t > {}'.format(t_i-t_pre-1, t_i+t_post+1))## drop the part of the signal with the salto

        else:
            for t_i in potential_flips_t:
                if proc_nonsalto: df = df.query('t < {} or t > {}'.format(t_i-t_pre-1, t_i+t_post+1))## drop the part of the signal with the salto

            print(fle)
            
        if proc_nonsalto:
            # find the signal droupouts more than 300 ms
            ind_breaks = np.where(np.diff(df.index.values)>0.3)[0]

            ## preprocess the button presses (in case of imperfect recording)
            t_range = get_silks_time_range(df, b1_press_t)

            min_i_range = np.where(df.index.values>t_range[0])[0][0]
            max_i_range = np.where(df.index.values<t_range[1])[0][-1]

            ind_breaks = np.concatenate(([min_i_range, max_i_range], ind_breaks), axis=0)
            ind_breaks.sort()

            ## write out signal portions around the salto clips
            ind_s = write_clips_from_signal(df, ind_breaks, t_range, ind_s, 'silks_raw')
                

def write_clips_from_signal(df, ind_breaks, t_range, ind_s, label):
    ''' Process breaks in the signal and write out clips '''
    for t_bi, t_bi2 in zip(ind_breaks[:-1], ind_breaks[1:]):
        tb = df.index.values[t_bi+1]
        tb2 = df.index.values[t_bi2]

        if (tb<=t_range[0]): continue
        if (t_range[1]<=tb2): continue
            
        write_clip_to_file(df.query('t > {} and t <{}'.format(tb, tb2)), label, ind_s)
        ind_s += 1
        #ind_s = write_10s_clips(df, tb, tb2, 'silks_raw', ind_s)
        
    return ind_s

        
def proc_parse_silks_clips_custom():
    base = '../'
    flist = [f for f in glob.glob(base+'silks_preproc/*') if not 'salto' in f]

    ind_s = len(glob.glob('../Gyro_Data/modeling/silks_raw/*'))
    print("Starting file index: {}".format(ind_s))
    
    for fle in flist:
        df, b1_press_t, b2_press_t = load_and_preproc_data_single(fle)
        
        # find the signal droupouts more than 150 ms
        ind_breaks = np.where(np.diff(df.index.values)>0.15)[0]
        
        ## preprocess the button presses (in case of imperfect recording)
        t_range = get_silks_time_range(df, b1_press_t)
        
        ## need to add the initial times for the case there are no breaks
        min_i_range = np.where(df.index.values>t_range[0])[0][0]
        max_i_range = np.where(df.index.values<t_range[1])[0][-1]
        
        ind_breaks = np.concatenate(([min_i_range, max_i_range], ind_breaks), axis=0)
        ind_breaks.sort()
        
        try:
            ind_s = write_clips_from_signal(df, ind_breaks, t_range, ind_s, 'silks_raw')
        except ValueError as e:
            print("Error in file {}: {}".format(fle, e))
 
    
def proc_parse_ctrl_clips_custom():
    base = '../'
    flist = glob.glob(base+'ctrl_preproc/*')
    
    ind_s = 0 # len(glob.glob('../Gyro_Data/modeling/ctrl_raw/*'))
        
    for fle in flist:
        df, b1_press_t, b2_press_t = load_and_preproc_data_single(fle)
        
        # find the signal droupouts more than 150 ms
        ind_breaks = np.where(np.diff(df.index.values)>0.15)[0]
        
        ## button presses are irrelevant for the control data so use the full data
        ind_breaks = np.concatenate(([0, len(df)-1], ind_breaks), axis=0)
        ind_breaks.sort()
        
        t_range = [0, len(df)-1]
            
        ind_s = write_clips_from_signal(df, ind_breaks, t_range, ind_s, 'ground_raw')

                    
def resample_df(df, interpolation_kind, freq_new):
    ''' Interpolate and resample given df to new frequency'''
    
    # set the columns to process
    col_list = ['ax','ay','az','gx','gy','gz','button1','button2']
    #  alternatively could do all of df.columns

    ## Set new t values for resampling with an even rate.
    t_new = np.arange(df.t.min(), df.t.max(), 1/freq_new)
    df_resamp = pd.DataFrame(index = t_new, columns = col_list)
    df_resamp.index.name = 't'
    ## resample each column
    for col in col_list:
        if 'button' in col: # use nearest neighbor interp for the buttons
            f = interpolate.interp1d(df.t,df[col], kind='nearest', fill_value = 'extrapolate')
        else: 
            f = interpolate.interp1d(df.t,df[col], kind=interpolation_kind, fill_value = 'extrapolate')

        df_resamp[col] = f(t_new)
    return df_resamp
    
def resample_df_clips(input_dir, interpolation_kind = 'quadratic', freq_new = 119.):
    ''' Interpolate and resample input data to 100Hz (or other specified) Write to new folder. '''
    assert '_raw' in input_dir, ("input_folder expected to have 'raw' \
                                    in filename so output doesnt overwrite it")
    
    output_dir = input_dir.replace('raw', interpolation_kind)
    os.makedirs(output_dir, exist_ok = True)
    
    try:
        fle_clips = glob.glob(input_dir + '/*')
        for fle in fle_clips:
            file_base = os.path.basename(fle)
            df_resamp = resample_df(pd.read_csv(fle),\
                                    interpolation_kind = interpolation_kind,\
                                    freq_new = freq_new)
            df_resamp[SIG_COLS].to_csv(os.path.join(output_dir,file_base), index = False)
    except ValueError as e:
        print(e)
        print(fle)