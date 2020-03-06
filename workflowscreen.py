import pyautogui as auto
import time
from tinydb import TinyDB, Query

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

WAIT_AHEAD = 0.005

db_procedure = TinyDB("procedure.json", indent=2)
query = Query()


class MainButton(Button):
    pass


class Procedure:

    def __init__(self, **kwargs):
        self.steps = kwargs.pop("steps")

    @classmethod
    def load_all_name(cls):
        return [each["name"] for each in db_procedure.all()]

    @classmethod
    def load(cls, name):
        steps = db_procedure.get(query.name == name)["steps"]
        return cls(steps=steps)


class ToolBar(BoxLayout):

    step_count = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_do_line = None
        self.schedule_wait_for_defocus = None
        self.time_last = None

    def do_line(self, dt):
        steps = self.procedure.steps
        step = steps[self.step_count]
        if len(step) > 1:
            key, wait = steps[self.step_count]
            self.schedule_do_line = Clock.schedule_once(self.do_line, wait - WAIT_AHEAD)
        else:  # last line of procedure
            key = steps[self.step_count][0]
        time_delta = time.time() - self.time_last
        if self.step_count > 0 and time_delta < steps[self.step_count-1][1]:
            wait_justify = steps[self.step_count-1][1] - time_delta
            time.sleep(wait_justify)
        self.time_last = time.time()
        auto.press(key)
        self.step_count += 1

    def play(self):
        self.step_count = 0
        self.stop()
        self.schedule_do_line = Clock.schedule_once(self.do_line, 0.5)
        self.time_last = time.time()

    def stop(self):
        if self.schedule_do_line:
            self.schedule_do_line.cancel()

    def wait_for_defocus(self, action):
        if not Window.focus:
            action()
            self.schedule_wait_for_defocus.cancel()

    def play_on_defocus(self):
        self.schedule_wait_for_defocus = Clock.schedule_interval(lambda _: self.wait_for_defocus(self.play), 0)


class ProcedureDropDown(DropDown):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name in Procedure.load_all_name():
            btn = Button(text=name, size_hint_y=None, height=44)
            btn.bind(on_release=lambda selection: self.select(selection.text))
            self.add_widget(btn)


class ProcedureButton(MainButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drop_down = ProcedureDropDown()
        self.bind(on_release=self.drop_down.open)
        self.drop_down.bind(on_select=self.on_select)

    def on_select(self, instance, value):
        self.text = value
        self.tool_bar.stop()
        self.tool_bar.line_count = 0
        self.tool_bar.procedure = Procedure.load(value)
