# Wordle (Kivy)

A desktop Wordle clone built with Python and the Kivy framework. Guess the
hidden five-letter word in six tries, with color feedback and a persistent
alphabet hint row.

## Features

- 6x5 board: six guesses of five letters each
- Valid-word checking against the bundled word list
- Correct (green), present (yellow), and absent (gray) tile coloring
- Persistent alphabet hints that keep the best known result per letter
- On-screen keyboard with a `DEL` key
- Physical keyboard input, with focus returned to the guess field automatically
- Win/loss messages, including the answer when you run out of guesses
- One-click restart after a game ends

## Requirements

- Python 3.14
- Kivy 2.3.1

See `requirements.txt` for the full list of Python dependencies.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

The app loads `src/wordle.kv`, so it must be started from the `src` directory:

```bash
cd src
python main.py
```

## Controls

- Type letters to fill the current row
- Press `Enter` to submit the guess
- Click the on-screen keyboard to enter letters, or `DEL` to delete the last one
- Click **Submit** to submit; the same button becomes **Restart** once the game ends

## Testing and linting

Run these from the repository root:

```bash
python -m unittest discover -s tests -v
flake8 src/main.py tests/test_game.py --max-line-length=120
```

## Project structure

```text
src/main.py         Application logic and game state
src/wordle.kv       Kivy UI definition and styling
src/words.txt       Word list used for answers and guess validation
tests/test_game.py  Unit tests for game behavior
```

## License

MIT. See [LICENSE](LICENSE).
