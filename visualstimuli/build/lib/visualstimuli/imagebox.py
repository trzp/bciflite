#!user/bin/python
# -*-coding:utf-8-*-

#FileName: block.py
#Version: 1.0
#Author: Jingsheng Tang
#Date: 2017/8/12
#Email: mrtang@nudt.edu.cn
#Github: trzp

import pygame
from .pygame_anchors import *
import os,sys

#impath = os.path.split(sys.argv[0])[0]+'/VisualStimuli/template.bmp'

class Imagebox(object):
    def __init__(self,root,
                    image = impath,
                    siz = (0,0),
                    position = (0,0),
                    anchor = 'center',
                    text = '',
                    textcolor = (0,255,255),
                    textfont = 'arial',
                    textsize = 10,
                    textanchor = 'lefttop',
                    borderon = False,
                    borderwidth = 1,
                    bordercolor = (255,255,255),
                    layer = 0,
                    visible = False):

        pygame.font.init()
        self.root = root
        self.siz = siz
        self.position = position
        self.anchor = anchor
        self.textcolor = textcolor
        self.textfont = textfont
        self.textsize = textsize
        self.text = text
        self.textanchor = textanchor
        self.image = image
        self.borderon = borderon
        self.borderwidth = borderwidth
        self.bordercolor = bordercolor
        self.visible = visible
        self.layer = layer

        if not os.path.isfile(self.textfont): self.textfont = pygame.font.match_font(self.textfont)
        self.font_object = pygame.font.Font(self.textfont,self.textsize)

        self.blitp =blit_pos1(self.siz,self.position,self.anchor)

    def reset(self):
        if self.siz == (0,0):
            self.im = pygame.image.load(self.image).convert()
            self.siz = self.im.get_size()
        else:
            self.im = pygame.transform.scale(pygame.image.load(self.image).convert(),self.siz)

        if self.text != '':
            self.font_object = pygame.font.Font(self.textfont,self.textsize)
            self.textsur = self.font_object.render(self.text,1,self.textcolor)
            corner = getcorner(self.siz,self.textanchor)
            p = blit_pos(self.textsur,corner,self.textanchor)
            self.im.blit(self.textsur,p)
        self.blitp = blit_pos1(self.siz,self.position,self.anchor)
        return self.im,self.blitp

    def show(self):
        if self.visible:
            if self.im!=None:
                self.root.blit(self.im,self.blitp)
            if self.borderon:
                pygame.draw.rect(self.root,self.bordercolor,pygame.Rect(self.blitp,self.siz),self.borderwidth)
