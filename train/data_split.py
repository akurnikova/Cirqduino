"""


"""
import json
import os
import random
import glob
import csv
import argparse
import numpy as np

LABEL_NAME = "movement"
DATA_NAME = "accel_gyro_6ax"

def read_data(file_to_read, mvmnt_type):
    """Read collected data from files."""
    with open(file_to_read, "r") as f:
        data_new = {}
        data_new[LABEL_NAME] = mvmnt_type
        data_new[DATA_NAME] = []
        for line in csv.reader(f):
            if line[0] != "ax":
                data_new[DATA_NAME].append([float(i) for i in line])
    return data_new

def write_data_json(data_to_write, path):
    ''' Write data to single json file '''
    with open(path, "w") as f:
        for idx, item in enumerate(data_to_write):
            dic = json.dumps(item, ensure_ascii=False)
            f.write(dic)
            f.write("\n")

def check_variance_threshold(clip):
    ''' input clip as a list of all the values (6 values per list entry) '''
    var_row = [np.var([a[i] for a in clip]) for i in range(6)]
    cutoff = (var_row[0] < .5) & (var_row[1] < .5) &(var_row[2] < .5) &\
             (var_row[3] < 5e3) & (var_row[4] < 5e3) &(var_row[5] < 5e3)
    keep = not cutoff
    return keep

def check_minmax_threshold(clip):
    ''' input clip as a list of all the values (6 values per list entry) '''
    min_row = [np.min([a[i] for a in clip]) for i in range(6)]
    max_row = [np.max([a[i] for a in clip]) for i in range(6)]
    cutoff = (max_row[0]-min_row[0] < .5) &\
             (max_row[1]-min_row[1] < .5) &\
             (max_row[2]-min_row[2] < .5) &\
             (max_row[3]-min_row[3] < 50) &\
             (max_row[4]-min_row[4] < 50) &\
             (max_row[5]-min_row[5] < 50)
    keep = not cutoff
    return keep

def read_and_split_data(file_to_read, mvmnt_type, seq_len):
    """Read collected data from files."""
    
    data_full = read_data(file_to_read, mvmnt_type)
    data_clips = []
    
    ## make N clips proportional to the data length
    max_len = len(data_full[DATA_NAME])
    N = int(3*max_len/seq_len)
    
    for i in range(N):
        data_new = {}
        data_new['segment_type'] = 'random'
        data_new[LABEL_NAME] = data_full[LABEL_NAME]
        ni = random.randint(0, max_len-seq_len)
        data_new[DATA_NAME] = data_full[DATA_NAME][ni:(ni+seq_len)]
        
        if check_minmax_threshold(data_new[DATA_NAME]):
            data_clips.append(data_new)
    
    ## for testing, create a separate set of salto clips with predefined offsets
    if 'salto' in mvmnt_type:
        for i_offset in [0, 20, 100, 500]:
            data_new = {}
            data_new['segment_type'] = 'init_{}'.format(i_offset)
            data_new[LABEL_NAME] = data_full[LABEL_NAME]
            data_new[DATA_NAME] = data_full[DATA_NAME][i_offset:(i_offset+seq_len)]
            data_clips.append(data_new)    
            
    return data_clips
    
    
def split_data(seq_len, train_ratio=0.6, valid_ratio=0.2, combine_salto = True, interp_type = 'linear'):
    """
       Splits data into train, validation and test according to ratio.
       Do the split before generating short segments on the data
    """

    train_data = []
    valid_data = []
    test_data = []
    
    movement_names = ['salto_pike', 'salto_drop', 'ground', 'silks']
    if combine_salto:
        movement_names = ['salto', 'ground', 'silks']
    
    ## count the items in the input folders:
    num_dict = {mvmnt_type: len(glob.glob('../Gyro_Data/modeling/{}*_{}/*'.format(mvmnt_type, interp_type)))
            for mvmnt_type in movement_names}
    
    filename_dict = {mvmnt_type: glob.glob('../Gyro_Data/modeling/{}*_{}/*'.format(mvmnt_type, interp_type))
            for mvmnt_type in movement_names}
    
    train_num_dict = {k:int(train_ratio * num_dict[k]) for k in num_dict}
    valid_num_dict = {k:int(valid_ratio * num_dict[k]) for k in num_dict}
        
    ## shuffle the file indexes for the split
    random.seed(42)
    datafile_index = {k: list(range(v)) for k,v in num_dict.items()}
    for k in datafile_index:
        random.shuffle(datafile_index[k])
    
    for m in movement_names:
        for i in range(train_num_dict[m]):
            fle_idx = datafile_index[m].pop(0)
            train_data.extend(\
                              read_and_split_data(filename_dict[m][fle_idx], m, seq_len))
            
        for i in range(valid_num_dict[m]):
            fle_idx = datafile_index[m].pop(0)
            valid_data.extend(\
                              read_and_split_data(filename_dict[m][fle_idx], m,  seq_len))
            
        while len(datafile_index[m])>0:
            fle_idx = datafile_index[m].pop(0)
            test_data.extend(\
                              read_and_split_data(filename_dict[m][fle_idx], m, seq_len))
    #print(train_num_dict)
    return train_data, valid_data, test_data
    
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seq_len", "-s")
    parser.add_argument("--combine_salto", "-combinesalto")
    parser.add_argument("--interp_type", "-interp")
    args = parser.parse_args()

    seq_len = int(args.seq_len)
    combine_salto = args.combine_salto != 'n'
    interp_type = args.interp_type

    basedir = '../Gyro_Data/'
    os.makedirs(basedir+"test_train_split", exist_ok = True)
    
    train_data, valid_data, test_data =  split_data(seq_len = seq_len, combine_salto = combine_salto, interp_type = interp_type)
    
    write_data_json(train_data, basedir + "test_train_split/train")
    write_data_json(valid_data, basedir + "test_train_split/valid")
    write_data_json(test_data,  basedir + "test_train_split/test")