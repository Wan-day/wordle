import random
from pathlib import Path
from typing import Any
from kivy.app import App
from kivy.properties import ColorProperty
from kivy.uix.label import Label
from kivy.uix.button import Button

COLORS = {
    "empty": "#121213",
    "correct": "#538d4e",
    "present": "#b59f3b",
    "absent": "#3a3a3c",
}


class WordList():
    def __init__(self) -> None:
        with open(Path(__file__).resolve().parent / "words.txt") as f:
            self.words = f.read().splitlines()

    def select_word(self) -> str:
        return random.choice(self.words)

    def check_word(self, to_find: str) -> bool:
        return (to_find in self.words)


class BoardTile(Label):
    bg_color = ColorProperty(COLORS["empty"])


class AlphaTile(Button):
    background_color = ColorProperty(COLORS["absent"])


class WordleApp(App):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tiles: list[BoardTile] = []
        self.alphabet: list[AlphaTile] = []
        self.word_list: WordList = WordList()
        self.game_rows: int = 6
        self.game_cols: int = 5
        self.curr_row: int = 0

    def on_start(self) -> None:
        board = self.root.ids.game_board
        alphabet = self.root.ids.alpha
        # Kivy stores children in reverse order, so flip them
        self.tiles = board.children[::-1]
        self.alphabet = alphabet.children[::-1]
        self.rebuild_board()
        self.game_word = self.word_list.select_word()

    def set_board_tile(self, pos: int, color: str, letter: str) -> None:
        tile = self.tiles[pos]
        if color == "None":
            pass
        else:
            tile.bg_color = color
        if letter == "None":
            pass
        else:
            tile.text = letter

    def set_alpha_tile(self, color: str, letter: str) -> None:
        for i in range(26):
            if self.alphabet[i].text == letter:
                self.alphabet[i].background_color = color
                return None

    def rebuild_board(self) -> None:
        for row in range(self.game_rows):
            for col in range(self.game_cols):
                pos = row * self.game_cols + col
                self.set_board_tile(pos, COLORS["absent"], "")

    def endgame(self) -> None:
        pass

    def update_colors(self) -> None:
        text = f"{self.root.ids.text_input.text[0:5]:<5}"
        offset: int = self.game_cols * self.curr_row
        for i in range(len(text)):
            if text[i] == self.game_word[i]:
                self.set_board_tile(offset + i, COLORS["correct"], "None")
                self.set_alpha_tile(COLORS["correct"], text[i].upper())
            elif text[i] in self.game_word:
                self.set_board_tile(offset + i, COLORS["present"], "None")
                self.set_alpha_tile(COLORS["present"], text[i].upper())
            else:
                self.set_board_tile(offset + i, COLORS["absent"], "None")
                self.set_alpha_tile(COLORS["absent"], text[i].upper())

    def submit_guess(self) -> None:
        self.update_colors()
        text = f"{self.root.ids.text_input.text[0:5]:<5}".lower()
        if text not in self.word_list.words:
            return None
        if self.curr_row == 5:
            self.endgame()
        else:
            self.curr_row += 1
            self.root.ids.text_input.text = ""

    def update_text(self, player_input: str) -> None:
        player_input = f"{player_input[0:5]:<5}".upper()
        offset: int = self.game_cols * self.curr_row

        if len(player_input) <= 5:
            for i in range(len(player_input)):
                self.set_board_tile(offset + i, "None", player_input[i])


def main() -> None:
    App = WordleApp()
    App.run()


if __name__ == "__main__":
    main()
