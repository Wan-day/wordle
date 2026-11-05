import random
import sys
from pathlib import Path
from typing import Any
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import ColorProperty
from kivy.uix.label import Label
from kivy.uix.button import Button

COLORS = {
    "empty": "#141a26",
    "correct": "#22c55e",
    "present": "#eab308",
    "absent": "#343b4a",
}

ALPHA_HINT_RANK = {
    COLORS["absent"]: 0,
    COLORS["present"]: 1,
    COLORS["correct"]: 2,
}

ALPHA_TEXT_NORMAL = "#eef2ff"
ALPHA_TEXT_DIM = "#7b849b"
ALPHA_TILE_DIM_OPACITY = 0.6


def resource_path(filename: str) -> Path:
    """Resolve a data file shipped in the app bundle or next to the source."""
    base_dir: Path = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    )
    return base_dir / filename


class WordList():
    def __init__(self) -> None:
        with open(resource_path("words.txt")) as f:
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
        self.game_word: str = ""
        self.game_over: bool = False
        self.alpha_hints: dict[str, str] = {}

    def build(self) -> Any:
        # MyLayout lives in wordle.kv, which load_kv() has already parsed and
        # registered with Factory by the time build() runs.
        return Factory.MyLayout()

    def load_kv(self, filename: str | None = None) -> bool:
        if filename is None:
            filename = str(resource_path("wordle.kv"))
        return super().load_kv(filename=filename)

    def on_start(self) -> None:
        board = self.root.ids.game_board
        alphabet = self.root.ids.alpha
        # Kivy stores children in reverse order, so flip them
        self.tiles = board.children[::-1]
        self.alphabet = alphabet.children[::-1]
        Window.bind(focus=self.on_window_focus)
        self.new_game()

    def on_stop(self) -> None:
        Window.unbind(focus=self.on_window_focus)
        Clock.unschedule(self.focus_input)

    def on_window_focus(self, window: Any, focused: bool) -> None:
        if focused:
            Clock.schedule_once(self.focus_input, 0)

    def focus_input(self, *args: Any) -> None:
        text_input = self.root.ids.text_input
        if self.game_over or text_input.disabled:
            return None
        text_input.focus = True
        return None

    def new_game(self) -> None:
        self.game_over = False
        self.curr_row = 0
        self.game_word = self.word_list.select_word()
        self.root.ids.text_input.text = ""
        self.rebuild_board()
        self.alpha_hints.clear()
        for tile in self.alphabet:
            tile.background_color = COLORS["absent"]
            tile.color = ALPHA_TEXT_NORMAL
            tile.disabled = False
            tile.opacity = 1
        self.root.ids.text_input.disabled = False
        self.root.ids.message.text = ""
        self.root.ids.guess.text = "Submit"
        self.root.ids.guess.disabled = False
        self.root.ids.guess.opacity = 1
        Clock.schedule_once(self.focus_input, 0)

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
        current = self.alpha_hints.get(letter)
        if current is not None and (
            ALPHA_HINT_RANK[color] < ALPHA_HINT_RANK[current]
        ):
            return None
        for tile in self.alphabet:
            if tile.text == "DEL":
                continue
            if tile.text == letter:
                tile.background_color = color
                tile.opacity = (
                    ALPHA_TILE_DIM_OPACITY
                    if color == COLORS["absent"]
                    else 1
                )
                if color == COLORS["absent"]:
                    tile.color = ALPHA_TEXT_DIM
                else:
                    tile.color = ALPHA_TEXT_NORMAL
                self.alpha_hints[letter] = color
                return None

    def rebuild_board(self) -> None:
        for row in range(self.game_rows):
            for col in range(self.game_cols):
                pos = row * self.game_cols + col
                self.set_board_tile(pos, COLORS["empty"], "")

    def endgame(self, won: bool) -> None:
        self.game_over = True
        if won:
            self.root.ids.message.text = "You win!"
        else:
            self.root.ids.message.text = (
                f"Out of guesses! The word was {self.game_word.upper()}"
            )
        self.root.ids.text_input.disabled = True
        self.root.ids.guess.text = "Restart"
        for tile in self.alphabet:
            tile.disabled = True

    def on_action_press(self) -> None:
        if self.game_over:
            self.new_game()
        else:
            self.submit_guess()

    def update_colors(self, text: str) -> None:
        offset: int = self.game_cols * self.curr_row
        colors: list[str] = [COLORS["absent"] for _ in text]
        remaining: list[str] = list(self.game_word)
        # First pass: exact matches are correct and consume their letter.
        for i in range(len(text)):
            if text[i] == self.game_word[i]:
                colors[i] = COLORS["correct"]
                remaining[i] = ""
        # Second pass: a guess letter is present only while an unmatched
        # copy of it remains in the answer.
        for i in range(len(text)):
            if colors[i] == COLORS["correct"]:
                continue
            if text[i] in remaining:
                colors[i] = COLORS["present"]
                remaining.remove(text[i])

        status_rank = {
            COLORS["absent"]: 0,
            COLORS["present"]: 1,
            COLORS["correct"]: 2,
        }
        alphabet_colors: dict[str, str] = {}
        for i in range(len(text)):
            letter = text[i].upper()
            current = alphabet_colors.get(letter)
            if current is None or status_rank[colors[i]] > status_rank[current]:
                alphabet_colors[letter] = colors[i]

        for i in range(len(text)):
            self.set_board_tile(offset + i, colors[i], "None")
        for letter, color in alphabet_colors.items():
            self.set_alpha_tile(color, letter)

    def press_key(self, key: str) -> None:
        if self.game_over:
            return None
        text_input = self.root.ids.text_input
        if key == "DEL":
            text_input.text = text_input.text[:-1]
        elif len(key) == 1 and key.isalpha():
            if len(text_input.text) >= self.game_cols:
                return None
            text_input.text += key.lower()
        return None

    def submit_guess(self) -> None:
        if self.game_over:
            return None
        try:
            text = self.root.ids.text_input.text[0:self.game_cols].lower()
            if len(text) < self.game_cols:
                self.root.ids.message.text = "Not enough letters"
                return None
            if not self.word_list.check_word(text):
                self.root.ids.message.text = "Not in word list"
                return None
            self.update_colors(text)
            if text == self.game_word:
                self.endgame(True)
            elif self.curr_row == self.game_rows - 1:
                self.endgame(False)
            else:
                self.curr_row += 1
                self.root.ids.text_input.text = ""
            return None
        finally:
            Clock.schedule_once(self.focus_input, 0)

    def update_text(self, player_input: str) -> None:
        self.root.ids.message.text = ""
        player_input = f"{player_input[0:self.game_cols]:<{self.game_cols}}".upper()
        offset: int = self.game_cols * self.curr_row

        for i in range(len(player_input)):
            self.set_board_tile(offset + i, COLORS["empty"], player_input[i])


def main() -> None:
    App = WordleApp()
    App.run()


if __name__ == "__main__":
    main()
