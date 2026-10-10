# Crafted by Vivek Nair (VN) — https://github.com/vivekn4
#!/usr/bin/env python3
"""Tic-Tac-Toe engine: the commenter plays X, a minimax AI plays O.

Usage: python3 play.py "<move>"   e.g. python3 play.py "b2"  |  python3 play.py "new"

Reads tictactoe/state.json, then writes state.json + board.svg + result.json.
Pure stdlib. Never raises to the caller -- every input is handled gracefully.
"""
import json
import os
import re
import sys

try:
    from render import render_board
except ImportError:  # pragma: no cover - render failures must not break a move
    render_board = None

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "state.json")
SVG_PATH = os.path.join(HERE, "board.svg")
RESULT_PATH = os.path.join(HERE, "result.json")
BOARD_URL_HINT = "https://raw.githubusercontent.com/vivekn4/vivekn4/main/tictactoe/board.svg"

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)
# Center first, then corners, then edges -> the AI prefers the center on ties.
MOVE_ORDER = (4, 0, 2, 6, 8, 1, 3, 5, 7)

STATUSES = ("playing", "x_wins", "o_wins", "draw")


def check_winner(board):
    """'X' / 'O' / 'draw' / None."""
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None


def minimax(board, o_turn, depth):
    w = check_winner(board)
    if w == "O":
        return 10 - depth
    if w == "X":
        return depth - 10
    if w == "draw":
        return 0
    if o_turn:
        best = -999
        for i in range(9):
            if not board[i]:
                board[i] = "O"
                best = max(best, minimax(board, False, depth + 1))
                board[i] = ""
        return best
    best = 999
    for i in range(9):
        if not board[i]:
            board[i] = "X"
            best = min(best, minimax(board, True, depth + 1))
            board[i] = ""
    return best


def best_o_move(board):
    """Perfect O move (index), preferring center, then corners, then edges."""
    best_score, best_idx = -999, None
    for i in MOVE_ORDER:
        if not board[i]:
            board[i] = "O"
            score = minimax(board, False, 0)
            board[i] = ""
            if score > best_score:
                best_score, best_idx = score, i
    return best_idx


def cell_name(i):
    return "ABC"[i % 3] + str(i // 3 + 1)


def move_to_index(token):
    return "abc".index(token[0]) + 3 * (int(token[1]) - 1)


def load_state():
    try:
        with open(STATE_PATH) as f:
            state = json.load(f)
        board = state.get("board", [])
        if (
            not isinstance(board, list)
            or len(board) != 9
            or any(m not in ("", "X", "O") for m in board)
        ):
            raise ValueError("bad board")
        status = state.get("status", "playing")
        if status not in STATUSES:
            status = "playing"
        return {"board": list(board), "status": status}
    except (OSError, ValueError, KeyError, TypeError):
        return {"board": [""] * 9, "status": "playing"}


def save_all(state, summary):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)
    if render_board is not None:
        with open(SVG_PATH, "w") as f:
            f.write(render_board(state["board"], state["status"]))
    with open(RESULT_PATH, "w") as f:
        json.dump({"summary": summary, "board_url_hint": BOARD_URL_HINT}, f)


def save_result_only(summary):
    with open(RESULT_PATH, "w") as f:
        json.dump({"summary": summary, "board_url_hint": BOARD_URL_HINT}, f)


def play_move(token):
    """Apply one move. Returns (new_state_or_None, summary).

    new_state is None when nothing changed (invalid move / game already over).
    """
    state = load_state()
    board, status = state["board"], state["status"]

    if token == "new":
        state = {"board": [""] * 9, "status": "playing"}
        return state, "🎮 New game started! You're X — comment a cell like `B2` to move."

    if not re.fullmatch(r"[abc][123]", token):
        shown = token if token else "(empty)"
        return None, (
            f"Hmm, `{shown}` isn't a valid cell. "
            "Use a column A–C and a row 1–3, like `B2`."
        )

    if status != "playing":
        over = {
            "x_wins": "X already won this one 🏆",
            "o_wins": "O already won this one 🤖",
            "draw": "That game was a draw 🤝",
        }[status]
        return None, f"{over}! Comment `new` to start a fresh game."

    idx = move_to_index(token)
    name = token.upper()
    if board[idx]:
        return None, f"Cell `{name}` is already taken — pick another one, like `B2`."

    board[idx] = "X"
    w = check_winner(board)
    if w == "X":
        state["status"] = "x_wins"
        return state, f"🎉 You played X at `{name}` — **X WINS!** GG! Comment `new` for a rematch."
    if w == "draw":
        state["status"] = "draw"
        return state, f"You played X at `{name}` — board's full, **DRAW!** Comment `new` for a rematch."

    oi = best_o_move(board)
    board[oi] = "O"
    oname = cell_name(oi)
    w = check_winner(board)
    if w == "O":
        state["status"] = "o_wins"
        return state, (
            f"You played X at `{name}`, O answered at `{oname}` — **O WINS.** "
            "Better luck next time! Comment `new` to play again."
        )
    if w == "draw":
        state["status"] = "draw"
        return state, (
            f"You played X at `{name}`, O answered at `{oname}` — **DRAW!** "
            "Comment `new` for a rematch."
        )
    return state, (
        f"You played X at `{name}`, O answered at `{oname}`. "
        "Your move — comment a cell like `C3`."
    )


def main(argv):
    try:
        raw = argv[1] if len(argv) > 1 else ""
        parts = raw.strip().split()
        token = parts[0].lower().strip("`'\".,!?:;") if parts else ""
        new_state, summary = play_move(token)
        if new_state is None:
            save_result_only(summary)  # state.json untouched
        else:
            save_all(new_state, summary)
        print(summary)
    except Exception:
        summary = (
            "Hmm, something hiccuped processing that move — "
            "try a cell like `B2`, or `new` for a fresh game."
        )
        try:
            save_result_only(summary)
        except OSError:
            pass
        print(summary)


if __name__ == "__main__":
    main(sys.argv)
