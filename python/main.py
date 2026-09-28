from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


class WordleApp(App):
    pass


def main() -> None:
    App = WordleApp()
    App.build()
    App.run()


if __name__ == "__main__":
    main()
