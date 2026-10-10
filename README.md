# 🎮 Profile Tic-Tac-Toe

![Made by VN](https://img.shields.io/badge/made%20by-VN-blue)

A playable Tic-Tac-Toe game embedded in the GitHub profile README. Visitors play
**X** by commenting on a pinned issue; a built-in minimax AI plays **O** and
replies with the updated board. No API keys, no servers, no secrets — just
GitHub Actions, Python, and SVG.

## How it works

1. A visitor comments a cell like `B2` on the pinned 🎮 issue.
2. The `tictactoe.yml` workflow wakes up, extracts the move, and runs
   `tictactoe/play.py`.
3. `play.py` validates the move, applies X, answers with a perfect minimax O,
   then rewrites `state.json`, `board.svg`, and `result.json`.
4. The workflow commits those files back to `main` and posts a reply comment
   with the summary + the fresh board image (cache-busted with the new commit
   SHA so it always shows the latest board).
5. The README embeds `tictactoe/board.svg` from `main`, so the profile always
   shows the live game.

Moves are serialized with a concurrency group per issue, so rapid comments
can't corrupt the board.

## Files

| File | Purpose |
|---|---|
| `state.json` | The board (`""`/`"X"`/`"O"`, index 0 = A1, row-major) + `status` (`playing`/`x_wins`/`o_wins`/`draw`) |
| `board.svg` | Rendered board, regenerated after every move |
| `result.json` | One-line summary of the last move, consumed by the workflow's reply comment |
| `render.py` | Pure-stdlib SVG renderer (grid, labels, marks, win strike-through, banner) |
| `play.py` | CLI game engine: `python3 play.py "b2"` / `python3 play.py "new"` |

## Manual setup (one-time, after pushing)

1. Push this repo to `vivekn4/vivekn4` (the special profile repo — name must
   match the username exactly).
2. Create a new issue titled exactly:

   ```
   🎮 Tic-Tac-Toe — comment your move (e.g. B2)
   ```

   Suggested body: "You're X (blue), the built-in AI is O (red). Comment a
   cell like `B2` to move, or `new` for a fresh game. Columns A–C, rows 1–3."
3. Pin the issue (⋯ → **Pin issue**) so it stays at the top of the issues tab.
4. Comment `new` on the issue to kick off the first game.

The workflow only reacts to issues whose title starts with `🎮 Tic-Tac-Toe`,
so other issues are unaffected.

## Local testing

```bash
python3 tictactoe/play.py new   # fresh board
python3 tictactoe/play.py b2    # play X at B2, AI answers
python3 render.py 2>/dev/null || python3 tictactoe/render.py  # re-render only
```

---

**Crafted by [Vivek Nair](https://github.com/vivekn4) · VN**
