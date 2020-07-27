#coding:utf-8


import mmap
import struct
import numpy as np
# from .bcitypes import *
from bcitypes import *
import time
import random
from cyton2 import *
import multiprocessing
from multiprocessing import Queue
from timeext import timestamp


class CythonClient(object):
    def __init__(self,expset):
        self.param = EEGparam()
        self.param.samplingrate = expset.samplingrate
        self.param.eegchannels = expset.eegchannels
        
        port = expset.COM
        self.cmdque = Queue()
        self.dataque = Queue()
        
        p = multiprocessing.Process(target = cyton_function,args = (port,self.cmdque,self.dataque))
        p.start()
        
    def freshind(self):
        pass
        
    def start(self):
        self.cmdque.put('start')
        
    def stop(self):
        self.cmdque.put('stop')
        
    def getdata(self):
        data,stamp = self.dataque.get()     #阻塞型，约0.1s一次
        while not self.dataque.empty():
            tem,s = self.dataque.get()
            data.extend(tem)
        d = np.vstack(data).transpose()
        return 1,d,stamp


class SigGen(object):
    def __init__(self,expset):
        self.expset = expset
        self.param = EEGparam()
        self.param.samplingrate = expset.samplingrate
        self.param.eegchannels = expset.eegchannels
        self.param.point = int(self.param.samplingrate/10)
        self.F = expset.signal_generator_frequency
        self.G = expset.signal_generator_gain
        self.clk = time.clock()
        self.__baset = np.linspace(0,0.15,self.param.point+1)[:-1]

    def freshind(self):
        pass

    # def getdata(self):      #非阻塞型
    #     ct = time.clock()
    #     if ct-self.clk>0.05:
    #         ts = self.__baset + ct
    #         if self.expset.signal_generator_waveform == 'sin':  val = np.sin(2*np.pi*self.F*ts)*self.G
    #         else:   val = np.array([0.05*random.randint(-2000,2000) for i in range(self.param.point)])
    #         data = np.repeat(val,self.param.eegchannels).reshape(self.param.point,self.param.eegchannels).transpose()
    #         self.clk = ct
    #         return 1,data,timestamp.getstamp()
    #     else:
    #         return 0,0,0

    def getdata(self):
        while time.clock() - self.clk < 0.999:  #确保被调用的间隔为0.1s
            time.sleep(0.01)
        self.clk = time.clock()

        ts = self.__baset + self.clk
        if self.expset.signal_generator_waveform == 'sin':
            val = np.sin(2 * np.pi * self.F * ts) * self.G
        else:
            val = np.array([0.05 * random.randint(-2000, 2000) for i in range(self.param.point)])
        data = np.repeat(val, self.param.eegchannels).reshape(self.param.point, self.param.eegchannels).transpose()
        return 1, data, timestamp.getstamp()





