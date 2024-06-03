# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 14:13:14 2022

@author: TFord
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import numpy as np

class Settings:
    """-"""
    
    def __init__(self):
        self.serial_port = '/dev/ttyACM0'
        
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)
        
        self.screen_board_center = (300, 300)
        self.screen_scale = 0.8  # pixel / mm
        self.overhead_scale = 2  # pixel / mm
        self.carriage_scale = 16 # pixel / mm
        
        self.screen_colors = {'red': Qt.red,
                              'blue': Qt.blue,
                              'green': Qt.darkGreen,
                              'black': Qt.black,
                              'gray': Qt.gray}
        self.math_colors = dict(zip(self.screen_colors.values(), self.screen_colors.keys()))
        self.grav = 9810  # mm/s**2
        self.mu = 0.2
        self.C_R = 0.9
        self.C_R_post = 0.9
        self.inches = 25.4 # mm
        
        # board dimensions to the outside of hte lines
        self.r_posts = 7.625/2 * self.inches
        self.r_1 = 7.75/2 * self.inches
        self.r_2 = 15.3125/2 * self.inches
        self.r_3 = 22.375/2 * self.inches
        self.r_4 = 23.625/2 * self.inches # gutter
        self.r_0 = 11/16 * self.inches
        self.r_post = 1/8 * self.inches
        self.r_puck = 31.67/2  # mm
        self.mass_puck = 1/1000 # kg
        
        self.nom_puck_diameters = {
            "red": 29.75,
            "green": 31.6,
            "blue": 31.6
            }  
        self.puck_img_colors = {
            "red": [np.array(d) for d in [[130, 140, 60], [256, 256, 256],
                                        [0, 140, 60], [4, 256, 256]]],
            "green": [np.array(d) for d in [[60, 140, 60], [90, 256, 256]]],
            "blue": [np.array(d) for d in [[94, 140, 70], [120, 256, 256]]]
            }
        self.board_image_center = (983, 459)
        
