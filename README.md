# BCIF-Lite
Copyright (C) 2018, Mrtang, All Rights Reserved

Author: Mrtang

Email: mrtang_cs@163.com

## BCIF-Lite是什么?
一个简洁的BCI开发框架。使用python代码编写，以package的方式发布，是您通过pip install bciflite一条命令就可以完成包的安装并开始工作。

## BCIF-Lite框架整体情况
一个完整的脑机接口一般包括**信号采集**、**刺激/反馈**、**信号处理**、**应用/控制**四个模块，其中**刺激/反馈**模块构成脑机接口中的反馈部分，如反馈信号处理的结果给用户，（学习者需要理解脑机接口一定是一个闭环系统），在诱发型脑机接口中**刺激/反馈**它还是提供如光、声等形式的刺激信号来诱发大脑产生不同的认知响应。

在信号传递方面，涉及到**信号采集**->**信号处理**的流动，**刺激反馈**模块与**信号采集**、**信号处理**模块间的同步等，因此，一个脑机接口具有固定的组成模块和固定的链接关系。脑机接口框架的目标就是提供标准的组件和协议组织这些模块，使得用户只需要关心功能实现而非底层细节。优秀的脑机接口框架包括BCI2000,OpenVibe等，本文所推荐的是一款足够轻量化和简洁的脑机接口框架，其使用风格和BCI2000极为接近。

## 如何安装？环境依赖？
BCIF-Lite使用python3版本运行。可首先下载bciflite-0-0.wheel文件，然后通过pip install bciflite-0-0.wheel安装

同时BCIF-Lite还依赖于匹配的图形刺激库visualstimuli,稍后会进行介绍

## 以一个例子开始介绍BCIF-Lite的使用
**请注意逐行阅读注释，以下代码仅展示BCIF-Lite框架基本结构，实验过程并没有实际含义**

```javascript
# -*-coding:utf-8-*-

#FileName: main.py
#Version: 1.0
#Author: mrtang

from bciflite.bcicore import BciCore          # 从bciflite包导入BciCore类，这是BCIF-Lite的核心类
from visualstimuli.sinblock import sinBlock   # 从visualstimuli导入sinBlock，sinBlock提供了灰度被正弦波调整的方块图形
from ssvep_detector import *                  # ssvep信号处理函数，用户自定义

class BciApplication(BciCore):      # 我们需要完成的工作就是实现一个类（BciApplication）,它一定是继承自BciCore的一个类
    def Initialize(self):   #初始化函数（系统函数）
        self.STATES['trial'] = BciState(value = 1,samplingrate = 250)   #定义STATES,这是系统变量（type:dict），其元素为BciState类，该类用于记录实验状态用于给信号记录标记等

        self.expset.experiment_name = 'p3 exp'  #expset为系统变量（type:class）用于记录与实验设置相关的参数，如实验名称，编号，放大器的设置等
        self.expset.subject_name = 'sub'
        self.expset.session = 1
        self.expset.run = 1
        self.expset.path = '.\data'
        
        # self.expset.Amp = 'signal_generator'  #可适用模拟的信号发生器，可用于调试程序
        # self.expset.eegchannels = 9
        # self.expset.samplingrate = 250
        # self.expset.save_data = False
        
        self.expset.Amp = 'cyton'            
        self.expset.eegchannels = 8
        self.expset.samplingrate = 250      #cyton 8通道放大器
        self.expset.save_data = False
        self.expset.COM = 'COM14'
        
        self.sigprocess = SigPro(srate = 250)   #信号处理，用户自定义
        
        self.GUIsetup() #定制图形界面
   
   def GUIsetup(self):  #用户自定义函数
        scrw,scrh = self.screen.get_size()
        
        # stimuli为系统变量（type:dict），用来存放所有刺激图形
        # 这里定义了一个名为prompt的sinBlock图形，该图形的尺寸、位置、定位锚等属性均被定义，较为关键的参数为frequency
        self.stimuli['prompt'] = sinBlock(self.screen,siz=(300,100),position=(scrw/2,scrh/2),anchor='center',textcolor=(255,255,255),
                                       visible=True,forecolor0=(0,0,0),forecolor1=(255,255,255),frequency = 5,start = True)
        self.stimuli['prompt'].reset()  #使参数生效

    def Phase(self):  #状态机（系统函数），注意一定是从start开始到stop结束，注意流程的完整性
        self.phase(name='start',       next='p1',        duration=5)  #含义是从start状态跳转到p1状态，间隔5秒
        self.phase(name='p1',           next='p2',        duration=5)
        self.phase(name='p2',          next='p3',       duration=1)
        self.phase(name='p3',         next='p4',        duration=5)
        self.phase(name='p4',         next='stop',        duration=1)
        self.phase(name='stop')

    def Transition(self,phase): #传递函数（系统函数，由状态机触发执行），即对应上面的状态机中的每一个状态该做什么
        if phase == 'p1':
            self.stimuli['prompt'].start = True   #在p1中让prompt块开始闪烁start = True
            self.stimuli['prompt'].reset()
            self.STATES['trial'].setvalue(1)      #同时记录当前状态trial为1
        
        elif phase == 'p2':                       #在p2中让prompt块停止
            self.stimuli['prompt'].start = False
            self.stimuli['prompt'].reset()
        
        elif phase == 'p3':                       #在p3中让prompt块开始闪烁，频率调整为10Hz
            self.stimuli['prompt'].start = True
            self.stimuli['prompt'].frequency = 10
            self.stimuli['prompt'].reset()
            self.STATES['trial'].setvalue(2)      ##同时记录当前状态trial为2  
        
        elif phase == 'p4':
            self.stimuli['prompt'].start = False
            self.stimuli['prompt'].reset()
            
        elif phase == 'stop':
            pass

    def Process(self,sig):  #处理函数（系统函数，循环执行，由信号采集模块来驱动，即每收到一个信号包，该函数被调用一次，sig参数即为当前收到的信号）
        s_r = self.sigprocess(sig)
        print(s_r)
        
class SigPro: #用户定义的处理函数
    def __init__(self,srate):
        self.srate = srate
        self._data = []
    
    def process(self,sig):
        #notch filter
        #bandpass filter
        #feature extraction
        #classification
        pass
        return 1

if __name__ == '__main__':
    app = BciApplication()  #实例化
    app.StartRun()          #调用StartRun开始执行，你可以看到会出现一个闪烁的小方框，同时命令行还会打印出处理的结果。
```

## 设计细节
从上面的例子可以看到，BciCore类的核心函数包括**Initialize**、**Phase**、**Transition**、**Process**,在一般情况下，这几个函数每一个都必须实现。下面逐个进行介绍

## Initialize
功能：初始化，包括初始化**界面布局**，**实验配置**，**状态记录**，**界面布局**部分在visualstimuli中介绍

### 实验配置
由self.expset完成配置，是类ExpSet的示例，ExpSet类如下：
```javascript
class Expset:
  experiment_name = 'robot'
  subject_name = 'sub'
  session = 1
  run = 1
  path = os.path.split(os.sys.argv[0])[0]
  Amp = 'signal_generator' #or 'cyton'
  save_data = False
  amp_channels = 4
  amp_samplingrate = 200
  signal_generator_waveform = 'sin'
  signal_generator_frequency = 20
  signal_generator_gain = 50
  COM = 'COM14'
```

### 状态记录
由系统变量STATES（type:dict）来记录，其元素为BciState类
```javascript
class BciState:
    def __init__(self,value,samplingrate):  #设定初始值和信号采样率完成初始化
        ...
    
    def setvalue(self,v = None):    #调用setvalue来设置其值
        ...
```

## Phase
phase定义了系统运行的状态机，即实验步骤的流程

### *phase(name,next,duration)* 方法
用来定义一个phase
```javascript
self.phase(name='start',       next='p1',        duration=5)
```
phase函数包含三个参数，name,next,duration, **name**参数不可缺省，它定义了当前phase的名称，next,duration两个参数可缺省，当duration参数缺省时，duration为无穷大，当前phase不跳转

### *in_phase(phase)* 方法
用来判断当前是否在phase中

### *change_phase(phase)* 方法
立即从跳转到phase中，例如可定义一个缺省duration的phase，然后等待某个条件到达时利用change_phase方法跳转。即状态机的驱动有两种机制，一种是按照设计的时间推动，一种是按照条件来推动

## Transition(phase)
Transition定义了传递函数，即对应每一个状态机状态做什么事情，每当进入一个新的phase时被调用，参数为当前的phase名，该函数**不允许阻塞，不允许使用阻塞型函数**

## Process(sig)
处理函数，循环执行，由信号采集模块来驱动，即每收到一个信号包，该函数被调用一次，sig参数即为当前收到的信号。sig为EEG对象,主要包含eeg和state两部分，其中state为字典，对应系统设置的state,每一个元素为一维numpy.array序列，为state值序列。

**该函数大约0.1s执行一次，由于采取了弹性的处理机制，每次收到的信号包内sig和state的长度并不严格一致。**
```javascript
class EEG:
    eeg = None      #type: numpy.array, shape: channels x points
    state = None    #type: dict, 元素为np.array, 1 x points
    samplingrate = None
```

## 数据的保存和离线处理
* 将数据保存下来提供离线分析是研究脑机接口重要的手段。可通过expset的save_data属性来告知bciflite保存数据。
* 数据的格式：npz
* 数据的读取示例 以sub-S1R1.npz为例
```python
    import numpy as np
    data = np.load('sub-S1R1.npz')
    data['ExperimentName']
    data['SubjectName']
    data['Time']
    data['SamplingRate']
    data['EEGChannels']
    data['eeg']         #type:numpy.array  shape:channelsxpoints
    data['trial']       #对应系统设置的各个state序列,1xpoints
    data['statekey2']
    data['statekey3']
    data['statekey...']
```
