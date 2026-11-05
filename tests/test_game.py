import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from kivy.factory import Factory
from kivy.lang import Builder, global_idmap
from kivy.utils import get_color_from_hex

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import main  # noqa: E402


class WordleAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Builder.load_file(str(SRC / "wordle.kv"))

    def setUp(self) -> None:
        self.app = main.WordleApp()
        # Point KV's app proxy at this instance so widget rules call it
        object.__setattr__(global_idmap["app"], "_obj", self.app)
        self.root = Factory.MyLayout()
        self.app.root = self.root
        self.app.tiles = self.root.ids.game_board.children[::-1]
        self.app.alphabet = self.root.ids.alpha.children[::-1]
        self.app.word_list.words = ["crane", "slate", "abbey"]
        self.app.on_start()
        self.app.game_word = "crane"

    def tearDown(self) -> None:
        text_input = self.root.ids.text_input
        if text_input.focus:
            text_input.focus = False
        self.app.on_stop()

    def test_build_returns_layout_with_expected_ids(self) -> None:
        app = main.WordleApp()
        root = app.build()

        self.assertEqual(root.__class__.__name__, "MyLayout")
        for widget_id in (
            "game_board", "message", "text_input", "guess", "alpha"
        ):
            self.assertIsNotNone(root.ids.get(widget_id), widget_id)
        self.assertEqual(len(root.ids.game_board.children), 30)
        self.assertEqual(len(root.ids.alpha.children), 27)

    def test_resource_path_resolves_source_data_files(self) -> None:
        self.assertEqual(main.resource_path("words.txt"), SRC / "words.txt")
        self.assertEqual(main.resource_path("wordle.kv"), SRC / "wordle.kv")

    def submit_guess(self, text: str) -> None:
        self.root.ids.text_input.text = text
        self.app.submit_guess()

    def press_tile(self, key: str) -> None:
        tile = next(
            tile for tile in self.app.alphabet if tile.text == key
        )
        tile.dispatch("on_release")

    def alpha_color(self, letter: str) -> list:
        tile = next(
            tile for tile in self.app.alphabet if tile.text == letter
        )
        return tile.background_color

    def alpha_text_color(self, letter: str) -> list:
        tile = next(
            tile for tile in self.app.alphabet if tile.text == letter
        )
        return tile.color

    def test_alpha_tile_uses_empty_pressed_background(self) -> None:
        tile = self.app.alphabet[0]

        self.assertFalse(hasattr(tile, "bakcground_down"))
        self.assertEqual(tile.background_down, "")

    def test_invalid_guess_is_not_colored_or_advanced(self) -> None:
        color_before = self.app.tiles[0].bg_color

        self.submit_guess("zzzzz")

        self.assertEqual(self.app.curr_row, 0)
        self.assertFalse(self.app.game_over)
        self.assertEqual(self.root.ids.message.text, "Not in word list")
        self.assertEqual(self.app.tiles[0].bg_color, color_before)

    def test_valid_guess_advances_to_next_row(self) -> None:
        self.submit_guess("SLATE")

        self.assertEqual(self.app.curr_row, 1)
        self.assertFalse(self.app.game_over)
        self.assertEqual(self.root.ids.text_input.text, "")

    def test_valid_guess_schedules_input_focus(self) -> None:
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.submit_guess("SLATE")
            schedule_once.assert_called_once_with(self.app.focus_input, 0)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertTrue(self.root.ids.text_input.focus)

    def test_invalid_guess_schedules_input_focus(self) -> None:
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.submit_guess("ZZZZZ")
            schedule_once.assert_called_once_with(self.app.focus_input, 0)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertTrue(self.root.ids.text_input.focus)
        self.assertEqual(self.app.curr_row, 0)

    def test_winning_guess_does_not_focus_disabled_input(self) -> None:
        self.root.ids.text_input.focus = True

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.submit_guess("CRANE")
            schedule_once.assert_called_once_with(self.app.focus_input, 0)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertTrue(self.root.ids.text_input.disabled)
        self.assertFalse(self.root.ids.text_input.focus)

    def test_correct_guess_wins_and_disables_input(self) -> None:
        self.submit_guess("CRANE")

        self.assertTrue(self.app.game_over)
        self.assertEqual(self.root.ids.message.text, "You win!")
        self.assertEqual(
            self.app.tiles[0].bg_color,
            get_color_from_hex(main.COLORS["correct"]),
        )
        self.assertTrue(self.root.ids.text_input.disabled)
        self.assertFalse(self.root.ids.guess.disabled)
        self.assertEqual(self.root.ids.guess.text, "Restart")
        self.assertTrue(all(tile.disabled for tile in self.app.alphabet))

    def test_wrong_guess_on_last_row_loses(self) -> None:
        self.app.curr_row = self.app.game_rows - 1

        self.submit_guess("slate")

        self.assertTrue(self.app.game_over)
        self.assertIn("CRANE", self.root.ids.message.text)
        self.assertTrue(self.root.ids.text_input.disabled)
        self.assertEqual(self.root.ids.guess.text, "Restart")
        self.assertTrue(all(tile.disabled for tile in self.app.alphabet))

    def test_action_button_restarts_after_game_over(self) -> None:
        self.submit_guess("CRANE")

        self.app.on_action_press()

        self.assertFalse(self.app.game_over)
        self.assertEqual(self.app.curr_row, 0)
        self.assertEqual(self.root.ids.message.text, "")
        self.assertEqual(self.root.ids.guess.text, "Submit")

    def test_new_game_resets_board_and_controls(self) -> None:
        self.app.curr_row = self.app.game_rows - 1
        self.submit_guess("slate")
        self.app.alphabet[0].background_color = get_color_from_hex(
            main.COLORS["correct"]
        )
        self.app.word_list.words = ["crane"]

        self.app.new_game()

        self.assertEqual(self.app.curr_row, 0)
        self.assertFalse(self.app.game_over)
        self.assertEqual(self.app.game_word, "crane")
        self.assertEqual(self.root.ids.message.text, "")
        self.assertEqual(self.app.tiles[0].text, "")
        self.assertEqual(
            self.app.tiles[0].bg_color,
            get_color_from_hex(main.COLORS["empty"]),
        )
        self.assertEqual(
            self.app.alphabet[0].background_color,
            get_color_from_hex(main.COLORS["absent"]),
        )
        self.assertFalse(any(tile.disabled for tile in self.app.alphabet))
        self.assertFalse(self.root.ids.text_input.disabled)
        self.assertFalse(self.root.ids.guess.disabled)
        self.assertEqual(self.root.ids.guess.text, "Submit")
        self.assertEqual(self.root.ids.guess.opacity, 1)

    def test_alphabet_key_appends_letter_and_updates_board(self) -> None:
        self.press_tile("A")

        self.assertEqual(self.root.ids.text_input.text, "a")
        self.assertEqual(self.app.tiles[0].text, "A")
        self.assertEqual(self.app.tiles[1].text.strip(), "")

    def test_alphabet_keys_stop_at_five_letters(self) -> None:
        for letter in "ABCDEF":
            self.press_tile(letter)

        self.assertEqual(self.root.ids.text_input.text, "abcde")
        self.assertEqual(
            "".join(tile.text for tile in self.app.tiles[:5]),
            "ABCDE",
        )

    def test_delete_key_removes_last_letter_and_clears_tile(self) -> None:
        for letter in "ABC":
            self.press_tile(letter)

        self.press_tile("DEL")

        self.assertEqual(self.root.ids.text_input.text, "ab")
        self.assertEqual(self.app.tiles[2].text.strip(), "")
        self.assertEqual(
            self.app.tiles[2].bg_color,
            get_color_from_hex(main.COLORS["empty"]),
        )

    def test_text_input_does_not_unfocus_on_validate(self) -> None:
        self.assertFalse(self.root.ids.text_input.text_validate_unfocus)

    def test_text_input_background_is_transparent(self) -> None:
        text_input = self.root.ids.text_input

        self.assertEqual(list(text_input.background_color), [0, 0, 0, 0])
        self.assertEqual(text_input.background_normal, "")
        self.assertEqual(text_input.background_active, "")
        self.assertEqual(text_input.background_disabled_normal, "")

    def test_enter_submits_current_guess(self) -> None:
        self.assertFalse(self.root.ids.text_input.multiline)
        for letter in "CRANE":
            self.press_tile(letter)

        self.root.ids.text_input.dispatch("on_text_validate")

        self.assertTrue(self.app.game_over)
        self.assertEqual(self.root.ids.message.text, "You win!")
        self.assertEqual(
            self.app.tiles[0].bg_color,
            get_color_from_hex(main.COLORS["correct"]),
        )

    def test_short_guess_shows_not_enough_letters(self) -> None:
        self.submit_guess("abc")

        self.assertEqual(self.root.ids.message.text, "Not enough letters")
        self.assertEqual(self.app.curr_row, 0)
        self.assertEqual(
            self.app.tiles[0].bg_color,
            get_color_from_hex(main.COLORS["empty"]),
        )

    def test_editing_clears_error_message(self) -> None:
        for message, guess in (
            ("Not enough letters", "abc"),
            ("Not in word list", "zzzzz"),
        ):
            self.submit_guess(guess)
            self.assertEqual(self.root.ids.message.text, message)

            self.press_tile("DEL")

            self.assertEqual(self.root.ids.message.text, "")

    def test_tiles_use_empty_color_and_reset_on_edit(self) -> None:
        empty = get_color_from_hex(main.COLORS["empty"])
        for tile in self.app.tiles:
            self.assertEqual(tile.bg_color, empty)

        self.app.tiles[0].bg_color = get_color_from_hex(
            main.COLORS["correct"]
        )
        self.press_tile("A")

        for tile in self.app.tiles[:5]:
            self.assertEqual(tile.bg_color, empty)

    def row_colors(self, row: int = 0) -> list:
        start = row * self.app.game_cols
        end = start + self.app.game_cols
        return [tile.bg_color for tile in self.app.tiles[start:end]]

    @staticmethod
    def expected_colors(*names: str) -> list:
        return [get_color_from_hex(main.COLORS[name]) for name in names]

    def test_duplicate_guess_letters_do_not_over_color(self) -> None:
        self.app.word_list.words = ["abbey", "bobby"]
        self.app.game_word = "abbey"

        self.submit_guess("bobby")

        self.assertEqual(
            self.row_colors(),
            self.expected_colors(
                "present", "absent", "correct", "absent", "correct"
            ),
        )

    def test_correct_match_consumes_only_answer_copy(self) -> None:
        # CRANE contains a single E, which the correct match at index 4 uses.
        self.app.word_list.words = ["crane", "eerie"]
        self.app.game_word = "crane"

        self.submit_guess("eerie")

        self.assertEqual(
            self.row_colors(),
            self.expected_colors(
                "absent", "absent", "present", "absent", "correct"
            ),
        )

    def test_duplicate_guess_letter_uses_each_answer_copy_once(self) -> None:
        # THERE contains two E's, so one can be present and one correct.
        self.app.word_list.words = ["there", "eerie"]
        self.app.game_word = "there"

        self.submit_guess("eerie")

        self.assertEqual(
            self.row_colors(),
            self.expected_colors(
                "present", "absent", "present", "absent", "correct"
            ),
        )

    def test_non_duplicate_guess_scores_correctly(self) -> None:
        self.submit_guess("slate")

        self.assertEqual(
            self.row_colors(),
            self.expected_colors(
                "absent", "absent", "correct", "absent", "correct"
            ),
        )

    def test_correct_alpha_hint_survives_later_present_guess(self) -> None:
        self.app.word_list.words = ["crane", "crate", "trace"]

        self.submit_guess("crate")
        self.assertEqual(
            self.alpha_color("C"),
            get_color_from_hex(main.COLORS["correct"]),
        )

        self.submit_guess("trace")

        self.assertEqual(self.app.alpha_hints["C"], main.COLORS["correct"])
        self.assertEqual(
            self.alpha_color("C"),
            get_color_from_hex(main.COLORS["correct"]),
        )

    def test_present_alpha_hint_upgrades_to_correct(self) -> None:
        self.app.word_list.words = ["crane", "berry"]

        self.submit_guess("berry")
        self.assertEqual(self.app.alpha_hints["R"], main.COLORS["present"])
        self.assertEqual(self.app.alpha_hints["E"], main.COLORS["present"])

        self.submit_guess("crane")

        self.assertEqual(self.app.alpha_hints["R"], main.COLORS["correct"])
        self.assertEqual(self.app.alpha_hints["E"], main.COLORS["correct"])
        self.assertEqual(
            self.alpha_color("R"),
            get_color_from_hex(main.COLORS["correct"]),
        )
        self.assertEqual(
            self.alpha_color("E"),
            get_color_from_hex(main.COLORS["correct"]),
        )

    def test_last_alphabet_tile_m_receives_hint(self) -> None:
        self.app.word_list.words = ["mango"]
        self.app.game_word = "mango"

        self.submit_guess("mango")

        self.assertEqual(self.app.alpha_hints["M"], main.COLORS["correct"])
        self.assertEqual(
            self.alpha_color("M"),
            get_color_from_hex(main.COLORS["correct"]),
        )

    def test_new_game_clears_alpha_hint_state(self) -> None:
        self.app.word_list.words = ["crane", "crate"]
        self.submit_guess("crate")
        self.assertIn("C", self.app.alpha_hints)
        self.assertEqual(
            self.alpha_color("C"),
            get_color_from_hex(main.COLORS["correct"]),
        )

        self.app.word_list.words = ["crane"]
        self.app.new_game()

        self.assertEqual(self.app.alpha_hints, {})
        self.assertEqual(
            self.alpha_color("C"),
            get_color_from_hex(main.COLORS["absent"]),
        )

    def test_absent_letters_dim_alpha_tile_text(self) -> None:
        self.submit_guess("slate")

        for letter in "SLT":
            self.assertEqual(
                self.alpha_text_color(letter),
                get_color_from_hex(main.ALPHA_TEXT_DIM),
            )
        for letter in "AE":
            self.assertEqual(
                self.alpha_text_color(letter),
                get_color_from_hex(main.ALPHA_TEXT_NORMAL),
            )

    def test_alphabet_tiles_have_bigger_font(self) -> None:
        self.assertEqual(self.app.alphabet[0].font_size, 22)

    def test_absent_alpha_tile_is_dimmed(self) -> None:
        self.submit_guess("slate")

        for letter in "SLT":
            tile = next(
                tile for tile in self.app.alphabet if tile.text == letter
            )
            self.assertLess(tile.opacity, 1)
        for letter in "AE":
            tile = next(
                tile for tile in self.app.alphabet if tile.text == letter
            )
            self.assertEqual(tile.opacity, 1)

    def test_new_game_resets_alpha_tile_dimming(self) -> None:
        self.submit_guess("slate")
        tile = next(tile for tile in self.app.alphabet if tile.text == "S")
        self.assertLess(tile.opacity, 1)

        self.app.new_game()

        self.assertEqual(tile.opacity, 1)

    def test_present_letter_keeps_normal_alpha_tile_text(self) -> None:
        self.app.word_list.words = ["crane", "trace"]

        self.submit_guess("trace")

        self.assertEqual(
            self.alpha_text_color("C"),
            get_color_from_hex(main.ALPHA_TEXT_NORMAL),
        )
        self.assertEqual(
            self.alpha_text_color("T"),
            get_color_from_hex(main.ALPHA_TEXT_DIM),
        )

    def test_new_game_restores_alpha_tile_text_color(self) -> None:
        self.submit_guess("slate")
        self.assertEqual(
            self.alpha_text_color("S"),
            get_color_from_hex(main.ALPHA_TEXT_DIM),
        )

        self.app.word_list.words = ["crane"]
        self.app.new_game()

        normal = get_color_from_hex(main.ALPHA_TEXT_NORMAL)
        for tile in self.app.alphabet:
            self.assertEqual(tile.color, normal)

    def test_restart_reenables_keyboard(self) -> None:
        self.submit_guess("CRANE")
        self.assertTrue(all(tile.disabled for tile in self.app.alphabet))

        self.app.press_key("A")
        self.assertEqual(self.root.ids.text_input.text, "CRANE")

        self.app.on_action_press()

        self.assertFalse(any(tile.disabled for tile in self.app.alphabet))
        self.press_tile("B")
        self.assertEqual(self.root.ids.text_input.text, "b")

    def test_window_focus_focuses_active_input(self) -> None:
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.app.on_window_focus(None, True)
            schedule_once.assert_called_once_with(self.app.focus_input, 0)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertTrue(self.root.ids.text_input.focus)

    def test_window_focus_does_not_focus_disabled_input(self) -> None:
        self.submit_guess("CRANE")
        self.assertTrue(self.root.ids.text_input.disabled)
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.app.on_window_focus(None, True)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertFalse(self.root.ids.text_input.focus)

    def test_window_losing_focus_does_not_schedule_input_focus(self) -> None:
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.app.on_window_focus(None, False)

        schedule_once.assert_not_called()
        self.assertFalse(self.root.ids.text_input.focus)

    def test_new_game_restores_input_focus(self) -> None:
        self.submit_guess("CRANE")
        self.root.ids.text_input.focus = False

        with patch.object(main.Clock, "schedule_once") as schedule_once:
            self.app.new_game()
            schedule_once.assert_called_once_with(self.app.focus_input, 0)
            callback = schedule_once.call_args.args[0]
            callback(0)

        self.assertFalse(self.root.ids.text_input.disabled)
        self.assertTrue(self.root.ids.text_input.focus)


if __name__ == "__main__":
    unittest.main()
