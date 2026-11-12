"""
Farm Implement Advisor - phone app (Kivy)

The rules live in advisor.py (the same code as the Python version).
This file only draws the screen and passes the answers to recommend().

Test on a computer:  pip install kivy  then  python main.py
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from advisor import (
    CROPS,
    DRIVES,
    NEEDS_CROP,
    OPERATIONS,
    SIZE_TO_HP,
    SOIL_CONDITIONS,
    SOIL_TYPES,
    recommend,
)

DARK = (0.10, 0.16, 0.10, 1)
SOFT = (0.35, 0.40, 0.35, 1)
GREEN = (0.16, 0.46, 0.22, 1)
GREY = (0.45, 0.48, 0.45, 1)
RED = (0.75, 0.15, 0.10, 1)
PLACEHOLDER = "Tap to choose"

SIZE_LABELS = {
    "Small (under 40 HP)": "s",
    "Medium (40 to 75 HP)": "m",
    "Large (75 to 110 HP)": "l",
    "Very large (over 110 HP)": "x",
}


def short(text):
    """'Dry - dusty or hard...' -> 'Dry'"""
    return text.split(" - ")[0].split(" (")[0]


class WrapLabel(Label):
    """A label that wraps long text and grows to fit it."""

    def __init__(self, **kwargs):
        kwargs.setdefault("color", DARK)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.bind(width=self._wrap, texture_size=self._fit)

    def _wrap(self, *_):
        self.text_size = (self.width, None)

    def _fit(self, *_):
        self.height = self.texture_size[1] + dp(4)


class Choice(BoxLayout):
    """A question, a drop-down list, and a small hint under it."""

    def __init__(self, title, options, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, spacing=dp(4), **kwargs)
        # short name -> (key used by the logic, full description)
        self.options = {short(text): (key, text) for key, text in options.items()}
        self.add_widget(WrapLabel(text=title, bold=True, font_size=sp(17)))
        self.spinner = Spinner(
            text=PLACEHOLDER,
            values=list(self.options),
            size_hint_y=None,
            height=dp(52),
            font_size=sp(17),
            background_normal="",
            background_color=GREEN,
        )
        self.hint = WrapLabel(text="", font_size=sp(14), color=SOFT)
        self.add_widget(self.spinner)
        self.add_widget(self.hint)
        self.spinner.bind(text=self._changed)
        self.bind(minimum_height=self.setter("height"))

    def _changed(self, _spinner, text):
        pick = self.options.get(text)
        self.hint.text = pick[1] if pick else ""

    def key(self):
        pick = self.options.get(self.spinner.text)
        return pick[0] if pick else None

    def reset(self):
        self.spinner.text = PLACEHOLDER


class AdvisorApp(App):
    title = "Farm Advisor"

    def build(self):
        Window.clearcolor = (0.96, 0.97, 0.93, 1)
        Window.softinput_mode = "below_target"

        self.scroll = ScrollView(do_scroll_x=False)
        self.form = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(16),
            spacing=dp(16),
        )
        self.form.bind(minimum_height=self.form.setter("height"))
        self.scroll.add_widget(self.form)

        self.op = Choice("What job do you want to do?", OPERATIONS)
        self.crop = Choice("Which crop?", CROPS)  # shown only for planting / harvesting
        self.cond = Choice("How is the soil right now?", SOIL_CONDITIONS)
        self.soil = Choice("What type of soil is it?", SOIL_TYPES)
        self.drive = Choice("Does the tractor drive all four wheels?", DRIVES)

        self.form.add_widget(WrapLabel(text="Farm Implement Advisor", bold=True, font_size=sp(26)))
        self.form.add_widget(
            WrapLabel(text="Answer a few easy questions and get the right implement.",
                      font_size=sp(15), color=SOFT)
        )
        self.form.add_widget(self.op)
        self.form.add_widget(self.cond)
        self.form.add_widget(self.soil)
        self.form.add_widget(self._tractor_box())
        self.form.add_widget(self.drive)

        find = Button(
            text="Find the implement",
            size_hint_y=None,
            height=dp(58),
            font_size=sp(19),
            bold=True,
            background_normal="",
            background_color=GREEN,
        )
        find.bind(on_release=self.find)
        again = Button(
            text="Start over",
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
            background_normal="",
            background_color=GREY,
        )
        again.bind(on_release=self.start_over)
        self.form.add_widget(find)
        self.form.add_widget(again)

        self.card = self._make_card()
        self.op.spinner.bind(text=self._job_changed)
        return self.scroll

    # ----- pieces of the screen -------------------------------------------

    def _tractor_box(self):
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(WrapLabel(text="How strong is your tractor?", bold=True, font_size=sp(17)))
        self.hp_input = TextInput(
            hint_text="Type the horsepower (HP), for example 60",
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            font_size=sp(17),
            padding=[dp(10), dp(14), dp(10), dp(10)],
        )
        self.size_spinner = Spinner(
            text="Do not know the HP? Pick a size",
            values=list(SIZE_LABELS),
            size_hint_y=None,
            height=dp(52),
            font_size=sp(16),
            background_normal="",
            background_color=GREY,
        )
        box.add_widget(self.hp_input)
        box.add_widget(self.size_spinner)
        return box

    def _make_card(self):
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(8),
        )
        card.bind(minimum_height=card.setter("height"))
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *_: setattr(rect, "pos", card.pos),
            size=lambda *_: setattr(rect, "size", card.size),
        )
        return card

    # ----- behaviour ------------------------------------------------------

    def _job_changed(self, _spinner, _text):
        needs_crop = self.op.key() in NEEDS_CROP
        if needs_crop and self.crop.parent is None:
            # put the crop question right under the job question
            self.form.add_widget(self.crop, index=self.form.children.index(self.op))
        elif not needs_crop and self.crop.parent is not None:
            self.form.remove_widget(self.crop)
            self.crop.reset()

    def _horsepower(self):
        typed = self.hp_input.text.strip()
        if typed:
            try:
                value = float(typed)
            except ValueError:
                return None
            return value if 5 <= value <= 500 else None
        size = SIZE_LABELS.get(self.size_spinner.text)
        return SIZE_TO_HP[size] if size else None

    def find(self, *_):
        op, cond, soil, drive = self.op.key(), self.cond.key(), self.soil.key(), self.drive.key()
        crop = self.crop.key() if op in NEEDS_CROP else None
        hp = self._horsepower()

        missing = []
        if not op:
            missing.append("the job")
        if op in NEEDS_CROP and not crop:
            missing.append("the crop")
        if not cond:
            missing.append("the soil condition")
        if not soil:
            missing.append("the soil type")
        if hp is None:
            missing.append("tractor power (5 to 500 HP, or pick a size)")
        if not drive:
            missing.append("2WD or 4WD")
        if missing:
            self._show_card("CHECK YOUR ANSWERS", "Please choose: " + ", ".join(missing) + ".",
                            [], ok=False, big=False)
            return

        result = recommend(op, cond, soil, hp, crop, drive)
        details = ["Why: " + result["why"]]
        if result["alternative"]:
            details.append("Second choice: " + result["alternative"])
        details += ["Note: " + note for note in result["warnings"]]
        self._show_card("USE THIS", result["implement"], details)

    def _show_card(self, heading, main, details, ok=True, big=True):
        self.card.clear_widgets()
        self.card.add_widget(WrapLabel(text=heading, bold=True, font_size=sp(13),
                                       color=GREEN if ok else RED))
        self.card.add_widget(WrapLabel(text=main, bold=True,
                                       font_size=sp(24) if big else sp(17)))
        for line in details:
            self.card.add_widget(WrapLabel(text=line, font_size=sp(16)))
        if self.card.parent is None:
            self.form.add_widget(self.card)
        Clock.schedule_once(lambda _dt: setattr(self.scroll, "scroll_y", 0), 0.2)

    def start_over(self, *_):
        for choice in (self.op, self.crop, self.cond, self.soil, self.drive):
            choice.reset()
        self.hp_input.text = ""
        self.size_spinner.text = "Do not know the HP? Pick a size"
        if self.card.parent is not None:
            self.form.remove_widget(self.card)
        self.scroll.scroll_y = 1


if __name__ == "__main__":
    AdvisorApp().run()
