# Crafted by Vivek Nair (VN) — https://github.com/vivekn4
#!/usr/bin/env python3
"""Render the Tic-Tac-Toe board state to a clean 600x600 SVG. Pure stdlib.

Board indexing: index 0 = A1, row-major A1..C3.
  Row A: A1=0, B1=1, C1=2
  Row B: A2=3, B2=4, C2=5
  Row C: A3=6, B3=7, C3=8
"""
import json
import os

SIZE = 600
CELL = SIZE // 3  # 200

BG = "#161b22"
GRID = "#30363d"
X_COLOR = "#58a6ff"
O_COLOR = "#f85149"
LABEL_COLOR = "#8b949e"
WIN_LINE_COLOR = "#d29922"

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
)

BANNERS = {"x_wins": "X WINS!", "o_wins": "O WINS!", "draw": "DRAW!"}


def cell_name(i):
    """Index -> label, e.g. 0 -> 'A1', 4 -> 'B2', 8 -> 'C3'."""
    return "ABC"[i % 3] + str(i // 3 + 1)


def cell_center(i):
    row, col = divmod(i, 3)
    return col * CELL + CELL // 2, row * CELL + CELL // 2


def winning_line(board):
    """Return the winning triple of indices, or None."""
    for line in WIN_LINES:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return line
    return None


def render_board(board, status):
    """Return the SVG string for a board + status."""
    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
        f'viewBox="0 0 {SIZE} {SIZE}" font-family="sans-serif">'
    )
    p.append(f'<rect width="{SIZE}" height="{SIZE}" rx="24" fill="{BG}"/>')

    # grid lines
    for k in (1, 2):
        x = k * CELL
        p.append(
            f'<line x1="{x}" y1="20" x2="{x}" y2="{SIZE - 20}" '
            f'stroke="{GRID}" stroke-width="6" stroke-linecap="round"/>'
        )
        p.append(
            f'<line x1="20" y1="{x}" x2="{SIZE - 20}" y2="{x}" '
            f'stroke="{GRID}" stroke-width="6" stroke-linecap="round"/>'
        )

    # cells: corner label + mark
    for i in range(9):
        row, col = divmod(i, 3)
        x0, y0 = col * CELL, row * CELL
        p.append(
            f'<text x="{x0 + 14}" y="{y0 + 30}" font-size="22" '
            f'fill="{LABEL_COLOR}">{cell_name(i)}</text>'
        )
        cx, cy = cell_center(i)
        mark = board[i]
        if mark == "X":
            o = 52
            p.append(
                f'<line x1="{cx - o}" y1="{cy - o}" x2="{cx + o}" y2="{cy + o}" '
                f'stroke="{X_COLOR}" stroke-width="26" stroke-linecap="round"/>'
            )
            p.append(
                f'<line x1="{cx + o}" y1="{cy - o}" x2="{cx - o}" y2="{cy + o}" '
                f'stroke="{X_COLOR}" stroke-width="26" stroke-linecap="round"/>'
            )
        elif mark == "O":
            p.append(
                f'<circle cx="{cx}" cy="{cy}" r="56" fill="none" '
                f'stroke="{O_COLOR}" stroke-width="24"/>'
            )

    # gold strike-through on the winning line
    line = winning_line(board)
    if line:
        x1, y1 = cell_center(line[0])
        x2, y2 = cell_center(line[2])
        p.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{WIN_LINE_COLOR}" stroke-width="14" stroke-linecap="round" opacity="0.95"/>'
        )

    # end-of-game banner
    banner = BANNERS.get(status)
    if banner:
        p.append('<rect x="130" y="250" width="340" height="100" rx="20" fill="#000000" opacity="0.78"/>')
        p.append(
            f'<text x="300" y="318" font-size="56" font-weight="bold" '
            f'fill="#ffffff" text-anchor="middle">{banner}</text>'
        )

    p.append("</svg>")
    return "\n".join(p)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "state.json")) as f:
        state = json.load(f)
    svg = render_board(state["board"], state.get("status", "playing"))
    with open(os.path.join(here, "board.svg"), "w") as f:
        f.write(svg)
    print("board.svg written")


if __name__ == "__main__":
    main()
