#coding:utf-8

import os
from .bcitypes import *
# from bcitypes import *
import scipy.io
from multiprocessing import Queue
import time

class Storage(object):
    def __init__(self,expset,statekeys,que):
        self.expset = expset
        head = self.expset.subject_name +'-S%iR'%(self.expset.session)
        #extension = '.mat'
        extension = '.npz'
        filenum = self.expset.run
        filename = head+str(filenum)+extension
        newfilename = self.expset.path+'//'+filename
        if not os.path.exists(self.expset.path):
            os.makedirs(self.expset.path)
        else:
            files = os.listdir(self.expset.path)
            nums = [self.getnum(f,head,extension) for f in files if self.getnum(f,head,extension)>-1]
            if nums!=[]:    newfilename = self.expset.path+'//'+head+str(max(nums)+1)+extension
        self.data_file = newfilename

        self.buf = {}
        self.buf['ExperimentName'] = self.expset.experiment_name
        self.buf['SubjectName'] = self.expset.subject_name
        self.buf['Time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.buf['SamplingRate'] = int(expset.samplingrate)
        self.buf['EEGChannels'] = int(expset.eegchannels)

        self.statekeys = statekeys

        self.runing = True
        self.que = que

    def getnum(self,file,head,extension):
        hi = file.find(head)
        ei = file.find(extension)
        if hi==-1 or ei==-1:
            return -1
        else:
            try:
                num = int(file[hi+len(head):ei])
                return num
            except:
                return -1

    def save(self,eegarray, statearray):
        ss = ""
        for key in self.statekeys:
            ss += "%s = statearray['%s'][0]," % (key, key)

        cmd = "np.savez(self.data_file,ExperimentName = self.buf['ExperimentName'],\
                                SubjectName = self.buf['SubjectName'],\
                                Time = self.buf['Time'],\
                                SamplingRate = self.buf['SamplingRate'],\
                                EEGChannels = self.buf['EEGChannels'],\
                                eeg = eegarray[0], %s)" % (ss)

        exec(cmd)

    def mainloop(self):
        while self.runing:
            flg,eegarray,statearray = self.que.get()
            self.save(eegarray,statearray)
            if flg:
                break
        print('[storage] process ended')


def storage_process(expset,statekeys,que):
    store = Storage(expset,statekeys,que)
    store.mainloop()




