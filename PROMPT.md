# The build prompt

This is the prompt to paste into an AI when you want to change or extend this app.
It exists because the three things that make these games work in a room full of people
are the three things an AI will quietly drop if you do not ask for them: **responsiveness**,
**in-game feedback**, and **guided instructions**.

Everything below the line is the prompt. Replace the last paragraph with what you
actually want, and leave the rest alone.

---

You are working on a facilitator-run classroom game that is a single static site:
`index.html` (two games — Prompt Pictionary and Prompt Feud), `admin.html` (the host's
answer key and session log), and `feud-data.js` (the shared board data both pages read).
No build step, no framework, no network calls at runtime. Vanilla JS in one IIFE, `var`
not `let`, no external libraries. It is served from GitHub Pages and must also work when
opened from a local folder.

The room this runs in: one host at a laptop, output on a projector, two teams of adult
learners, 40 minutes. The host is not a developer and has not rehearsed. Something will
go wrong and they will have to recover live, in front of everyone.

**Hold these three properties. They are the requirements, not the polish.**

**1. Responsive — it has to survive the actual hardware.**

- Every screen must work from a 360px phone to a 1920px projector. Nothing may scroll
  the page sideways at any width: `document.documentElement.scrollWidth` must never
  exceed `clientWidth`.
- Size type and spacing with `clamp()` against viewport units, not fixed pixels. Grids
  collapse at breakpoints (`repeat(4,1fr)` → `1fr 1fr` → `1fr`); rows of buttons stack.
- Anything that cannot shrink — a wide table, a long chip row, a timeline — scrolls
  inside its own `overflow-x:auto` container, never the page.
- Tall content stays reachable: a centred flex screen needs `overflow-y:auto` and
  `justify-content: safe center`, or long content becomes unscrollable on short screens.
- Respect `prefers-reduced-motion` on every transition and animation you add.
- Projector reality: nothing load-bearing may be thinner than 1.5px or rely on colour
  alone to carry meaning.

**2. In-game feedback — every input gets an answer inside 100ms.**

- Every action states its result in words on screen, not just by changing a number.
  A guess says whether it landed, which answer it landed on, and what it was worth.
  A top answer says it was the top answer.
- Never fail silently and never fail ambiguously. A rejected input explains the
  rejection ("not on the board") and leaves the consequence to the host — the app does
  not hand out penalties on its own.
- Destructive actions confirm in place (click once to arm, again to commit) rather than
  firing on the first click or opening a dialog.
- State the running state continuously: scores, bank, strikes, what is left on the board,
  which team is in control.
- Sound and flash are additions to a text result, never replacements for one.

**3. Guided instructions — the host never has to remember what comes next.**

- A persistent "next step" line reads the actual game state, not the current screen:
  not "you are on the board screen" but "Two strikes. One more miss and Team 2 gets a
  single guess at all 85 points."
- The sequence is visible: a timeline of where the session is and what is left.
- Every screen can be reached by URL (`#/feud/board`), the back button works, and a link
  to a state that cannot exist yet falls back somewhere sensible *and corrects the URL*.
- Full instructions live in the game, collapsed, for reading before you start — not only
  in a README nobody opens mid-match.
- Spoilers stay off the projector. Answer keys live in `admin.html`, which warns about it.

**House rules.**

- Write for adult learners. Plain, direct, never school-toned, never cute. Escalate to
  "program coordinator", not "teacher".
- Palette: ink `#161217`, paper `#FAF6F2`, red `#D6003C`, green `#2F9E58`. Segoe UI for
  text, Consolas for labels.
- Never invent data that claims to be measured. Board answers are authored from known
  model defaults, which is exactly why scoring is rank-based instead of quoting survey
  counts nobody counted. If you add content, say where it came from.
- Escape anything a human typed before putting it in `innerHTML`.
- Board data belongs in `feud-data.js` so the game and the answer key cannot drift apart.

**Prove it before you tell me it works.** The suites are headless-Chrome harnesses that
inject assertions into the live page: `matchtest.py` (match flow), `r2test.py` (Beat the
Board), `flowtest.py` (Pictionary), `spatest.py` (routing, next steps, and overflow at
four viewports), `admintest.py` (logging and the answer key), plus `keydiag.py` and
`guessdiag.py` for keyword routing. Run all of them, add assertions for whatever you
changed, and report the real numbers. If something fails, say so and show the output.
Headless Chrome floors the viewport around 512px, so breakpoints below that need a human
to look — say that out loud instead of implying they were tested.

**What I want changed:**

> _(replace this with the actual request — e.g. "add a third game mode", "make the
> guess box host-only so players cannot read it off the projector", "add six more
> boards at the brutal difficulty band")_
