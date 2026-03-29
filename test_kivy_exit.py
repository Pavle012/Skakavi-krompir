from kivy.app import App
from kivy.uix.button import Button
class TestApp(App):
    def build(self):
        b = Button(text="Exit")
        b.bind(on_release=lambda x: App.get_running_app().stop())
        return b
TestApp().run()
