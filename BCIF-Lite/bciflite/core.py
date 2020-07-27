#coding:utf-8

import numpy as np
import time
import threading
import multiprocessing
from multiprocessing import Queue

from .ampclient import SigGen
from .storage import Storage
from .bcitypes import *


from .ampclient import SigGen,CythonClient
from .storage import *
from .bcitypes import *


try:    __INF__ = float('inf')
except: __INF__ = 0xFFFF

class core(threading.Thread):
    def __init__(self,phase_ev,sig,bci_sts,expset,stp):
        self.stp = stp
        self.phase_ev = phase_ev
        self.sig = sig
        self.bci_sts = bci_sts
        self.expset = expset


        self.sample_interval = 1/self.sig.samplingrate

        self.currentphase = 'start'
        self.PHASES = {'start':{'next':'','duration':__INF__},'stop':0}
        self.param = EEGparam()
        threading.Thread.__init__(self)

    def addphase(self,name='',next='',duration=__INF__):
        self.PHASES[name]={'next':next,'duration':duration}

    def inphase(self,phase):
        return phase==self.currentphase

    def changephase(self,phase):
        if phase in self.PHASES:
            self.currentphase=phase
            self.__clk = time.clock()
            self.phase_ev.set()
        else:
            raise(IOError,'no phase: %s found!'%(phase))

    def run(self):
        print('\n[core] thread started!')
        
        stskeys = list(self.bci_sts.keys())   #state的名字集合

        
        stats_array = {}
        for key in self.bci_sts:
            stats_array[key] = None


        if self.expset.Amp == 'signal_generator': self.amp = SigGen(self.expset)
        elif self.expset.Amp == 'cython':   self.amp = CythonClient(self.expset)
        else:raise(IndexError,'unrecognized amplifier: ' + self.expset.Amp)

        #param cheack
        if self.amp.param.eegchannels != self.expset.eegchannels or\
            self.amp.param.samplingrate != self.expset.samplingrate:
            raise(IndexError,'dismatch between amplifier and experiment set!')

        if self.expset.save_data:
            self.store_que = Queue()
            pro = multiprocessing.Process(target = storage_process,args=(self.expset,stskeys,self.store_que))
            pro.start()

            eegbuffer = []
            statbuffer = {}
            for key in stskeys:
                statbuffer[key] = []
        
        if self.expset.Amp == 'cython':
          self.amp.start()
        else:
          while not self.amp.getdata()[0]:  
            time.sleep(0.1)

        SAVEONCE = False
        self.storeclk = self.__clk = time.clock()
        self.phase_ev.set()

        while True:
            clk = time.clock()
            if clk - self.storeclk > 3: #2秒保存一次数据
                SAVEONCE = True
                self.storeclk = clk

            valid,data,stamp = self.amp.getdata()

            if valid:
                r,c = data.shape
                for key in self.bci_sts:
                    stat = self.bci_sts[key]
                    stats_array[key] = stat.gen_array(c,stamp)

                self.sig.eeg = data
                self.sig.state = stats_array
                self.sig.event.set()

                if self.expset.save_data:
                    eegbuffer.append(data)
                    dat = np.hstack(eegbuffer)
                    eegbuffer = [dat]

                    for key in stskeys:
                        statbuffer[key].append(stats_array[key])
                        _ = np.hstack(statbuffer[key])
                        statbuffer[key] = [_]

                    if SAVEONCE:
                        SAVEONCE = False
                        self.store_que.put([0,eegbuffer,statbuffer])

            if clk-self.__clk>self.PHASES[self.currentphase]['duration']:
                self.currentphase=self.PHASES[self.currentphase]['next']
                self.__clk = clk
                self.phase_ev.set()
            
            time.sleep(0.001)
            if self.inphase('stop'):break

        if self.expset.save_data:
            self.store_que.put([1,eegbuffer, statbuffer])
        self.stp.set()
        if self.expset.Amp == 'cython':
          self.amp.stop()
        time.sleep(2)
        print('\n[core] thread ended!')

