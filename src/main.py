from typing import Any
from kivy.app import App
from kivy.properties import ColorProperty
from kivy.uix.label import Label

COLORS = {
    "empty": "#121213",
    "correct": "#538d4e",
    "present": "#b59f3b",
    "absent": "#3a3a3c",
}


class BoardTile(Label):
    bg_color = ColorProperty(COLORS["empty"])


class WordleApp(App):
    rows: int = 6
    cols: int = 5

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tiles: list[BoardTile] = []

    def on_start(self) -> None:
        board = self.root.ids["game_board"]
        # Kivy stores children in reverse order, so flip them
        self.tiles = board.children[::-1]
        self.rebuild_board()

    def set_board_tile(self, pos: int, color: str, letter: str) -> None:
        tile = self.tiles[pos]
        tile.bg_color = color
        tile.text = letter

    def rebuild_board(self) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                pos = row * self.cols + col
                self.set_board_tile(pos, COLORS["absent"], "O")


def main() -> None:
    App = WordleApp()
    App.run()


if __name__ == "__main__":
    main()
