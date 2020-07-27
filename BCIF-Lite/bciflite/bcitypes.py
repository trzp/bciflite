#coding:utf-8

import os
from threading import Event
from timeext import timestamp
import numpy as np

class Expset:
    experiment_name = '312 bci experiment'
    subject_name = 'shuaiguo'
    session = 1
    run = 1
    path = os.path.split(os.sys.argv[0])[0]
    Amp = 'actichamp' #or 'signal_generator',cython
    save_data = False
    eegchannels = 4
    samplingrate = 200
    signal_generator_waveform = 'sin'
    signal_generator_frequency = 20
    signal_generator_gain = 50
    COM = 'COM14'


class EEG:
    event = Event()
    eeg = None
    state = None
    samplingrate = 250
    eegchs = 0

class EEGparam:
    samplingrate = 250
    eegchannels = 0
    point = 10

    
class BciState:
    def __init__(self,value,samplingrate):
        self.shift = True
        self.stamps = []
        self.values = [value]
        self.samplingrate = samplingrate

        self.sample_interval = 1/self.samplingrate
    
    def setvalue(self,v = None):
        if v != self.values[-1]:
            self.values.append(v)
            self.stamps.append(timestamp.getstamp())
            self.shift = True

    def gen_array(self,len,startstamp): #给定一个序列长度和起始时间戳，来生成序列
        if self.shift:
            inds = [self._cal(startstamp,stamp,len) for stamp in self.stamps]
            ay = self.values[0] * np.ones(len)
            for i,ind in enumerate(inds):
                ay[ind:] = self.values[i+1]

            self.shift = False
            self.values = self.values[-1:]
            self.stamps = []
            return ay
        else:
            return self.values[-1]*np.ones(len)


    def _cal(self,start,stamp,len):
        ind = round((stamp - start)/self.sample_interval)
        if ind <= 0:
            ind = 0
        elif ind >= len:
            ind = len - 1
        else:
            ind -= 1

        return ind





