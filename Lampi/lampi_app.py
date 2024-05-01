#!/usr/bin/env python3

import json
import pigpio
import lampi_util
import subprocess
import time
import signal
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window

from lampi_mixer import LampiMixer
from lampi_common import *
from main_screen import MainScreen
from settings_screen import SettingsScreen


class LampiApp(App):
    PLAY_PIN = 27 
    CLEAR_PIN = 23 
    SETTINGS_PIN = 22 

    play_button_pressed = BooleanProperty(False)
    clear_button_pressed = BooleanProperty(False)
    settings_button_pressed = BooleanProperty(False)

    TOGGLE_SCREEN = True

    def build(self):
        Window.clearcolor = (1, 1, 1, 1)

        self.sm = ScreenManager()

        self.main_screen = MainScreen(name="main")
        self.settings_screen = SettingsScreen(main_screen=self.main_screen, name="settings")

        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.settings_screen)

        self.setup_face_buttons()

        return self.sm

    def setup_face_buttons(self):
        Clock.schedule_interval(self._poll_GPIO, 0.05)

        self.pi = pigpio.pi()

        self.pi.set_mode(self.PLAY_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.PLAY_PIN, pigpio.PUD_UP)        

        self.pi.set_mode(self.CLEAR_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.CLEAR_PIN, pigpio.PUD_UP)

        self.pi.set_mode(self.SETTINGS_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SETTINGS_PIN, pigpio.PUD_UP)  

    def on_play_button_pressed(self, instance, value):
        if value:
            self.main_screen.toggle_play()

    def on_clear_button_pressed(self, instance, value):
        if value:
            self.main_screen.clear()

    def on_settings_button_pressed(self, instance, value):
        if value:
            if self.TOGGLE_SCREEN:
                self.sm.current = "settings"
            else:
                self.sm.current = "main"

            self.TOGGLE_SCREEN = not self.TOGGLE_SCREEN

    def _poll_GPIO(self, dt):
        self.play_button_pressed = not self.pi.read(self.PLAY_PIN)         # button 1
        self.clear_button_pressed = not self.pi.read(self.CLEAR_PIN)       # button 2
        self.settings_button_pressed = not self.pi.read(self.SETTINGS_PIN) # button 3

if __name__ == "__main__":
    LampiApp().run()
    