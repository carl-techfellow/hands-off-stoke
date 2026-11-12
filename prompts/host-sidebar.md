# Change request: the facilitator's navigation becomes a sidebar

This is the filled-in build prompt for this change, written before the change was made.
The frame it slots into is [`PROMPT.md`](../PROMPT.md) — everything there about
responsiveness, in-game feedback, guided instructions, house rules, and proving it with
the suites applies in full. This file is only the last section: **what I want changed.**

---

**What I want changed:**

Move the facilitator's in-game controls and orientation into a **host sidebar** so
running a match feels like driving a console instead of hunting through stacked bars.

**The problem as it stands.** The app bar, the match timeline, and the next-step line
are stacked horizontally across the top of the screen. On a projector that costs
vertical space the board needs, and it puts the host's eyes at the top edge while the
action is in the middle. Navigation between match phases barely exists: to revisit the
board from Fast Money you use the browser's back button; to reach Beat the Board early
you must know that "End match early" → "Last word" is the path. The host should never
need to know secret paths.

**What the sidebar must contain, top to bottom:**

1. The app bar's contents: back to the games, the mode name, the live score, the
   answer-key link.
2. The match timeline (Draw → R1–R4 → Fast Money → Last word), vertical, still marking
   done / current.
3. The next-step coach line — same element, same state-driven text.
4. **Phase navigation**: four stops — Lineup, The board, Fast Money, Beat the Board —
   that jump straight to a phase with one click. The current stop is highlighted.
   Stops that need a running match are disabled until one starts, and lock again when
   a new match resets.

**Behaviour rules:**

- Jumping must go through the same state guards as normal play. Jumping to Fast Money
  the first time sets it up; jumping back to it later must **not** redraw the questions
  or wipe the players' entries. Jumping to Beat the Board must arrive at a set-up
  screen (question, avoid-chips), never a blank one.
- Jumps route through the URL like every other transition — the address bar, the back
  button, and deep links keep working.
- Keep the existing play controls (strike, award, steal) on the stage with the board.
  The sidebar is navigation and orientation, not gameplay.

**Responsive rules (these are the ones a model will quietly drop):**

- The sidebar engages only at desktop/projector widths (≥920px). Below that, every
  element falls back to exactly the current stacked-top layout — phones and half-screen
  windows lose nothing.
- The sidebar takes a readable fixed column (clamp ~230–300px), never half the screen.
  The stage keeps `minmax(0, 1fr)` so nothing can force a sideways page scroll.
- The sidebar scrolls its own overflow and stays pinned while the stage scrolls.

**Prove it:** extend `spatest.py` — nav exists with four stops, locked before a match,
unlocks on start, current-stop highlighting, jump-and-return preserves Fast Money
state, Beat the Board arrives set up, URLs route, new match locks the stops again, and
the grid layout engages at 1078/1578px but not at 512/738px. All other suites stay
green. Report real numbers.
