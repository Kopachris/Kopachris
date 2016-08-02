from kivy.app import App
from kivy.uix.button import Button
import sys

class TestApp(App):
    def build(self):
        def btn_callback(btn):
            if btn.press_counter == 3:
                sys.exit()
            else:
                btn.text = btn.press_texts[btn.press_counter]
                btn.press_counter += 1
        btn = Button(text='Hello World')
        btn.press_counter = 0
        btn.press_texts = ['Hey!', 'Stop that!', 'If you push me again, I quit.']
        btn.bind(on_press=btn_callback)
        return btn

TestApp().run()