#!/usr/bin/env python
#-*- coding:utf-8 -*-


import pygame
from .pygame_anchors import *
import os
import time
import math
from time import clock


class sinBlock(object):
    def __init__(self, root,
              siz = (5,5),
              position = (0,0),
              anchor = 'center',
              forecolor0 = (0,0,0),
              forecolor1 = (255,255,255),

              bordercolor = (0,0,0,0),
              borderon = False,
              borderwidth = 1,

              textcolor = (0,255,255,0),
              textfont = 'arial',
              
              textanchor = 'center',
              textsize = 10,
              textbold = False,
              text = '',

              frequency = 10,
              init_phase = 0,
              duration = float('inf'),
              start = False,
              layer = 0,
              visible = False):
              
              
        self.siz = siz
        self.position = position
        self.anchor = anchor
        self.forecolor0 = forecolor0
        self.forecolor1 = forecolor1

        self.bordercolor = bordercolor
        self.borderon = borderon
        self.borderwidth = borderwidth

        self.textcolor = textcolor
        self.textfont = textfont
        self._textfont = 'arial'
        self.textanchor = textanchor
        self.textsize = textsize
        self.textbold = textbold
        self.text = text

        self.frequency = frequency
        self.init_phase = init_phase
        self.duration = duration
        self.__start = False
        self.layer = start
        self.visible = visible
        
        self.__fcolor = None
        self._textfont = 'arial'

        self.coef = np.array([0,0,0])
        self.parmkeys = ['siz','position','anchor',
                    'forecolor0','forecolor1','textcolor','textfont','textanchor','textsize','textbold',
                    'text','layer','visible','frequency','init_phase','duration','start',
                    'borderon', 'borderwidth', 'bordercolor',]
        self.sur = None
        self.blitp = (0,0)
        self.clk = clock()

        self.txtsur = None
        self.txtblitp = (0,0)

        pygame.font.init()
        self.root = root
        self.gen_textfont()
        self.reset()

    def gen_textfont(self):
        if not os.path.isfile(self.textfont):
            self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont, self.textsize)
        self.font_object.set_bold(self.textbold)
        
    def show(self):
        if self.visible:
            if self.__start:
                tt = clock()
                if tt - self.clk > self.duration:
                    self.__start = False
                    self.sur.fill(self.forecolor0)
                t = tt-self.clk
                f = (math.sin(2*math.pi*self.frequency*t + self.init_phase - 0.5*math.pi)+1)*0.5   #0-1
                self.__fcolor = self.coef * f + self.forecolor0
                self.sur.fill(self.__fcolor)
            else:
                self.sur.fill(self.forecolor0)
                pass

            if self.txtsur is not None:
                self.sur.blit(self.txtsur,self.txtblitp)

            self.root.blit(self.sur,self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root, self.bordercolor, pygame.Rect(
                    self.blitpborder, self.siz), self.borderwidth)

    def reset(self): #接受主控的控制
        self.blitp = self.blitpborder = blit_pos1(self.siz,self.position,self.anchor)
        self.coef = np.array(self.forecolor1)-np.array(self.forecolor0)
        self.sur = pygame.Surface(self.siz)
        self.sur.fill(self.forecolor0)

        if self.textfont != self._textfont or self._textsize != self.textsize or self._textbold != self.textbold:  # font重设了
            self.gen_textfont()
            self._textfont = self.textfont
            self._textbold = self.textbold
            self._textsize = self.textsize

        if self.text != '':
            self.txtsur = self.font_object.render(self.text, 1, self.textcolor)
            p0 = getcorner(self.sur.get_size(), self.textanchor)
            self.txtblitp = blit_pos(self.txtsur, p0, self.textanchor)
        else:
            self.txtsur = None
            
    def start(self):
        self.clk = clock()
        self.__start = True
    
    def stop(self):
        self.__start = False

