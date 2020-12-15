"""Load data from the specified paths and format them for training."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import numpy as np
import tensorflow as tf

LABEL_NAME = "movement"
DATA_NAME = "accel_gyro_6ax"

class DataLoader(object):
    """Loads data and prepares for training."""

    def __init__(self, train_data_path, valid_data_path, test_data_path, seq_length = 60, combine_salto = True):
        self.dim = 6
        self.seq_length = seq_length
        if combine_salto:
            self.label2id = {"ground": 0, "silks": 1, "salto": 2}
        else:
            self.label2id = {"ground": 0, "silks": 1, "salto_drop": 2, "salto_pike": 3}
        self.train_data, self.train_label, self.train_len = self.get_data_file(train_data_path, "train")
        self.valid_data, self.valid_label, self.valid_len = self.get_data_file(valid_data_path, "valid")
        self.test_data, self.test_label, self.test_len = self.get_data_file(test_data_path, "test")
        self.test_data_0, self.test_label_0, self.test_len_0 = self.get_data_file(test_data_path, "test0")
        
    def get_data_file(self, data_path, data_type):
        """Get train, valid and test data from files."""
        data = []
        label = []
        segment_type = 'random'
        if data_type == 'test0': ## special case for evaluating the saltos
            segment_type = 'init_0'
            
        with open(data_path, "r") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):  # pylint: disable=unused-variable
                dic = json.loads(line)
                if dic['segment_type'] == segment_type:
                    data.append(dic[DATA_NAME])
                    label.append(dic[LABEL_NAME])
        return data, label, len(data)

    def format_support_func(self, length, data, label):
        """Support function for format.(Helps format train, valid and test.)"""
        labels = np.asarray([self.label2id[i] for i in label])
        # Turn into tf.data.Dataset
        dataset = tf.data.Dataset.from_tensor_slices(
            (data, labels.astype("int32")))
        return length, dataset

    def format(self):
        """Format data(including padding, etc.) and get the dataset for the model."""
        self.train_len, self.train_data = self.format_support_func(
            self.train_len, self.train_data, self.train_label)
    
        self.valid_len, self.valid_data = self.format_support_func(
            self.valid_len, self.valid_data, self.valid_label)
    
        self.test_len, self.test_data = self.format_support_func(
            self.test_len, self.test_data, self.test_label)
        
        self.test_len_0, self.test_data_0 = self.format_support_func(
            self.test_len_0, self.test_data_0, self.test_label_0)
