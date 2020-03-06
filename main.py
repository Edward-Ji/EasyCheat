import kivy

from kivy.app import App
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager

from workflowscreen import *


Window.size = 720, 450

Builder.load_file("workflowscreen.kv")


class EasyCheatScreenManager(ScreenManager):
    pass


class EasyCheatApp(App):
    pass


EasyCheatApp().run()
