import pandas as pd
import numpy as np
import glob
import scipy.signal as sig
import os

from preproc_6ax_data import load_and_preproc_data_batch

def plot_potential_flips():
    fig, ax = plt.subplots(2,2, figsize = (10,5))

    df, b1_press_t, b2_press_t = load_and_preproc_data_batch(file_type = 'silks_preproc/*salto_nopancake*')

    potential_flips = np.concatenate(([0],np.where(df.ax <-3.7)[0]))
    #potential_flips = np.concatenate(([0],np.where(df.gy >300)[0]))
    potential_flips_loc = np.where(np.diff(potential_flips)>100)[0]+1
    potential_flips_t = df.index[potential_flips[potential_flips_loc]].values

    for t_i in potential_flips_t:
        df_clip = df.query('t > {} and t <{}'.format(t_i-3, t_i+5))
        df_clip.index = df_clip.index- df_clip.index[0]

        df_clip.gy.plot(ax = ax[0,0], color = 'r')
        df_clip.button2.plot(ax = ax[0,0], color = 'k')
        df_clip.ax.plot(ax = ax[1,0], color = 'r')
        df_clip.button2.plot(ax = ax[1,0], color = 'k')

        df_clip.plot.scatter(ax = ax[0,1],x = 'gy', y = 'ax', color = 'r')    

    df, b1_press_t, b2_press_t = load_and_preproc_data_batch(file_type = 'silks_preproc/*salto_pancake*')

    potential_flips = np.concatenate(([0],np.where(df.ax <-3.7)[0]))
    #potential_flips = np.concatenate(([0],np.where(df.gy >300)[0]))

    potential_flips_loc = np.where(np.diff(potential_flips)>100)[0]+1
    potential_flips_t = df.index[potential_flips[potential_flips_loc]].values

    for t_i in potential_flips_t:
        df_clip = df.query('t > {} and t <{}'.format(t_i-3, t_i+5))
        df_clip.index = df_clip.index- df_clip.index[0]

        df_clip.gy.plot(ax = ax[0,0], color = 'b')
        df_clip.button2.plot(ax = ax[0,0], color = 'k')
        df_clip.ax.plot(ax = ax[1,0], color = 'b')
        df_clip.button2.plot(ax = ax[1,0], color = 'k')
        df_clip.plot.scatter(ax = ax[0,1],x = 'gy', y = 'ax', color = 'b')  