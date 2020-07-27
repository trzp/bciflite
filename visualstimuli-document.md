# visualstimuli
Copyright (C) 2020, mrtang, All Rights Reserved

Author: mrtang

Email: mrtang_cs@163.cn

## visualstimuli是什么?用来干什么？
一个简洁的图形刺激引擎，visualstimuli用于配合bciflite使用，提供脑机接口实验中的反馈和视觉刺激。


## GuiEngine运行环境和安装
visualstimuli运行在python3下

通过pip install visualstimuli-0.0.0-py3-none-any.wheel安装


## 从一个例子开始visualstimuli的使用
**请逐行阅读代码，以下代码仅展示与visualstimuli紧密相关的部分**

```pythonscript
# -*-coding:utf-8-*-

from bciflite.bcicore import BciCore
from visualstimuli.block import Block   #从block模块导入Block类


class BciApplication(BciCore):
    def Initialize(self):
        # initialize STATES
        # initialize expset
        # other initialize
        
        # gui setup 对图形界面进行相关的初始化
        self.GUIsetup()
        self.gui_fps = 60   #在系统中设置gui的刷新率，强烈建议先查看系统的刷新率，然后将其设置为一致
        
    def GUIsetup(self):
        # 初始化screen,参数为尺寸，和背景颜色
        scrw,scrh = 1200,800
        self.init_screen(screen_siz = (1200,800),screen_color = (0,0,0))
        
        # 使用Block类，用来显示提示字符
        self.stimuli['prompt'] = Block(self.screen,(300,100),(scrw/2,50),anchor='center',textcolor=(255,255,255),
                                       visible=True,text='task:',textsize=50,forecolor=(0,0,0,0))
        # 使参数生效
        self.stimuli['prompt'].reset()

        ax = np.linspace(100,scrw-100,4).astype(np.int32)
        ay = np.linspace(150,scrh-100,3).astype(np.int32)

        # 排列3行4列12个方块
        indx = 0
        for y in ay:
            for x in ax:
                self.stimuli['Flsh%d'%(indx)] = Block(self.screen,(100,100),(x,y),anchor='center',
                                                   borderon=True,bordercolor=(255,0,255),visible=True,textsize=25,
                                                   layer=1,forecolor=(0,0,0,0),text=str(indx))
                self.stimuli['Flsh%d'%(indx)].reset()
                indx+=1

    def Phase(self):
        ...

    def StimAct(self,i,type):
        if type=='on':  self.stimuli['Flsh%d'%(i)].forecolor = (255,255,255,255)
        else:           self.stimuli['Flsh%d'%(i)].forecolor = (0,0,0,0)
        self.stimuli['Flsh%d'%(i)].reset()

    def Transition(self,phase):        
        if phase == 'on':
            [self.StimAct(d,'on') for d in range(12) if d in self.currentbook]  #点亮对应的块
        
        elif phase == 'off':
            [self.StimAct(d,'off') for d in range(12)]  #所有块消失
        
        elif phase == 'result': # 使用prompt显示结果
            res = self.P3Cla.rc_estimate(self.signal,self.stim_code,self.cube_dim)
            self.stimuli['prompt'].text = 'result: %s'%(str(self.cube[res[0],res[1]]),)
            self.stimuli['prompt'].reset()
        
    def Process(self,sig):
        ...

if __name__ == '__main__':
    app = BciApplication()
    app.StartRun()
```

### screen初始化 *init_screen(siz,color)*
用来初始化screen,参数为尺寸（width,height）和背景颜色(r,g,b)。当siz = (0,0)时，启用全屏。

### 刺激对象的注册和行为控制？
在visualstimuli包中，目前包含有Block，sinBlock, imageBox三类。**所有刺激对象均需要注册在self.stimuli中，否则将被系统化忽略**。如：

**<font color=#ff0000 size=9>注意:刺激对象类初始化的首个参数为self.screen!!!代表在screen上绘制图形</font>**

```pythonscript
    self.stimuli['prompt'] = Block(self.screen,(300,100),(scrw/2,50),anchor='center',textcolor=(255,255,255),visible=True,text='task:',textsize=50,forecolor=(0,0,0,0))
    self.stimuli['prompt'].reset()

```
完成注册后的对象可以通过修改其属性来控制其行为，如：
```pythonscript
    self.stimuli['prompt'].text = 'result is 1'
    self.stimuli['prompt'].reset()
```

### class: Block
block实现的是方块、方块上的文字、边框，以及它们的组合。
```pythonscript
class Block(object):
    siz = (5,5),                    #尺寸
    position = (0,0)                #位置
    anchor = 'center'               #定位锚
    borderon = False                #边框
    borderwidth = 1                 #边框宽度
    bordercolor = (0,0,0)           #边框颜色
    forecolor = (255,255,255)       #前景色
    textcolor = (0,255,255)         #文字颜色
    textfont = 'arial'              #文字字体
    textanchor = 'center'           #文字定位锚
    textsize = 10                   #文字粗体
    text = ''                       #文字字符串
    layer = 0                       #图层
    visible = False                 #可见
```

### class: sinBlock
sinBlcok在Block的基础上实现方块颜色在**前景色0**和**前景色1**之间按正弦波方式变化。正弦波频率通过frequency和init_phase参数设置。方块的颜色自start开始正弦变化，至计时满duration时终止。

```pythonscript
class sinBlock(object):
  siz = (5,5)                   
  position = (0,0)                  
  anchor = 'center'                 
  forecolor0 = (0,0,0)              #前景色0
  forecolor1 = (255,255,255)        #前景色1

  bordercolor = (0,0,0,0)           
  borderon = False
  borderwidth = 1

  textcolor = (0,255,255,0)
  textfont = 'arial'
  
  textanchor = 'center'
  textsize = 10
  textbold = False
  text = ''
  
  frequency = 10                    #频率
  init_phase = 0                    #初始相位
  duration = float('inf')           #持续时间
  layer = 0                         
  visible = False
  
  def start(self):                  #开始刺激
    ...

  def stop(self):                   #停止刺激
    ...
```

### class: ImageBox
```
class Imagebox(object):
    image = impath,
    siz = (0,0)
    position = (0,0)
    anchor = 'center'
    text = ''
    textcolor = (0,255,255)
    textfont = 'arial'
    textsize = 10
    textanchor = 'lefttop'
    borderon = False
    borderwidth = 1
    bordercolor = (255,255,255)
    layer = 0
    visible = False
```

### 关于定位锚 anchor
* 定位锚是指坐标原点所在的位置。例如block设置中，anchor='center',position=(100,200),意味着放置block对象时其中心点对齐于position。
* 支持的定位锚包括：'lefttop'，'left'，'leftbottom'，'righttop'，'right'，'rightbottom'，'top'，'bottom'，'center'，




