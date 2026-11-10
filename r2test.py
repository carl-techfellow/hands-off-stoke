import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function setOut(v){ r2Output.value = v; r2Output.dispatchEvent(new Event('input')); }
  try {
    document.getElementById('modeFeud').click();
    boardList.querySelectorAll('.boardpick')[0].click();   // email board
    boardGrid.querySelectorAll('.slot')[0].click();        // team1 +30
    chk('setup: team1 has 30', teams[0].score === 30);

    document.getElementById('toRound2Btn').click();
    chk('round2 active', fsRound2.classList.contains('active'));
    chk('board auto-revealed on entry', boardGrid.querySelectorAll('.slot.revealed').length === 6);
    chk('avoid chips listed', avoidList.querySelectorAll('.ac').length === 6);
    chk('question carried over', document.getElementById('r2Asked').textContent.indexOf('professional email') > -1);
    chk('judge panel hidden initially', r2Judge.hidden === true);
    chk('r2 badges clear on entry', r2TeamRow.querySelectorAll('.tbadge').length === 0);

    // open a team, paste a BUSTED answer
    r2TeamRow.querySelectorAll('.team')[1].click();
    chk('judge panel opens', r2Judge.hidden === false);
    setOut('Hi there! I hope this email finds you well, just checking in.');
    chk('scan flags busted', r2Scan.className.indexOf('busted') > -1);
    chk('busted names the hit', r2Scan.textContent.indexOf('finds you well') > -1);

    // clean answer scans clean
    setOut('Quick one before your coffee: the invoice numbers do not line up.');
    chk('scan flags clean', r2Scan.className.indexOf('clean') > -1);

    // award it
    document.getElementById('r2Good').click();
    chk('team2 +25', teams[1].score === 25);
    chk('panel closes after judging', r2Judge.hidden === true);
    chk('badge shows escaped', r2TeamRow.querySelectorAll('.tbadge.ok').length === 1);

    // re-judging the same team must not double-award
    r2TeamRow.querySelectorAll('.team')[1].click();
    document.getElementById('r2Good').click();
    chk('no double award on re-judge', teams[1].score === 25);

    // flipping a scored team to zero takes the points back
    r2TeamRow.querySelectorAll('.team')[1].click();
    document.getElementById('r2Zero').click();
    chk('flip to zero removes points', teams[1].score === 0);
    chk('badge now no-points', r2TeamRow.querySelectorAll('.tbadge.no').length === 1);

    // zero-scored team flipped back to good re-awards once
    r2TeamRow.querySelectorAll('.team')[1].click();
    document.getElementById('r2Good').click();
    chk('flip back re-awards once', teams[1].score === 25);

    // pasted text persists per team
    r2TeamRow.querySelectorAll('.team')[2].click();
    chk('other team starts empty', r2Output.value === '');
    setOut('team three text');
    r2TeamRow.querySelectorAll('.team')[1].click();
    chk('team2 text remembered', r2Output.value.indexOf('coffee') > -1);
    r2TeamRow.querySelectorAll('.team')[2].click();
    chk('team3 text remembered', r2Output.value === 'team three text');

    // round 1 scores survive round 2
    chk('round1 score intact', teams[0].score === 30);

    // final scores
    document.getElementById('finalScoreBtn').click();
    chk('winner line shown', winnerLine.hidden === false);
    chk('winner is team1 at 30', winnerLine.textContent.indexOf('30') > -1);

    // back to board, then new board resets r2 state on re-entry
    document.getElementById('backToBoardBtn').click();
    chk('back on board screen', fsBoard.classList.contains('active'));
    document.getElementById('toRound2Btn').click();
    chk('re-entry clears badges', r2TeamRow.querySelectorAll('.tbadge').length === 0);
    chk('re-entry clears pasted text', (teams[1].r2text || '') === '');

    // pictionary still reachable and intact
    document.querySelectorAll('[data-backmode]')[0].click();
    document.getElementById('modePictionary').click();
    chk('pictionary still works', getComputedStyle(pictionaryApp).display !== 'none');
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='R2'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""

src = (SITE / "index.html").read_text(encoding="utf-8")
test = src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1)
(SITE / "_r2test.html").write_text(test, encoding="utf-8")

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=4000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_r2test.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="R2">(.*?)</pre>', r.stdout, re.S)
if not m:
    print("NO RESULT - page threw before the harness ran")
    sys.exit(1)
results = html.unescape(m.group(1)).split(" | ")
fails = [x for x in results if x.startswith("FAIL")]
for x in results:
    print(("  " if x.startswith("PASS") else ">>"), x)
print()
print(f"{len(results)-len(fails)}/{len(results)} passed")
(SITE / "_r2test.html").unlink()
sys.exit(1 if fails else 0)
