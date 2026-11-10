import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function disp(el){ return getComputedStyle(el).display; }
  try {
    // enter feud from the picker
    document.getElementById('modeFeud').click();
    chk('feud rendered', disp(feudApp) !== 'none');
    chk('pictionary not rendered', disp(pictionaryApp) === 'none');
    chk('doc not rendered under feud', disp(docEl) === 'none');
    chk('lands on board picker', fsPick.classList.contains('active'));
    chk('six boards listed', boardList.querySelectorAll('.boardpick').length === 6);

    // load a board
    boardList.querySelectorAll('.boardpick')[0].click();
    chk('board screen active', fsBoard.classList.contains('active'));
    chk('six slots built', boardGrid.querySelectorAll('.slot').length === 6);
    chk('slots start hidden', boardGrid.querySelector('.slot .stext').textContent.indexOf('\u2022') > -1);
    chk('question shown', askedText.textContent.indexOf('professional email') > -1);
    chk('four teams', teamRow.querySelectorAll('.team').length === 4);
    chk('team1 starts active', teamRow.querySelectorAll('.team')[0].className.indexOf('active') > -1);

    // reveal top slot -> 30 pts to active team
    boardGrid.querySelectorAll('.slot')[0].click();
    var s0 = boardGrid.querySelectorAll('.slot')[0];
    chk('slot revealed', s0.classList.contains('revealed'));
    chk('answer text shown', s0.querySelector('.stext').textContent.indexOf('finds you well') > -1);
    chk('30 pts to team1', teams[0].score === 30);

    // double-click same slot must not double-score
    boardGrid.querySelectorAll('.slot')[0].click();
    chk('no double score', teams[0].score === 30);

    // strike advances the turn and marks a strike
    document.getElementById('strikeBtn').click();
    chk('one strike marked', strikeRow.querySelectorAll('.strikeslot.on').length === 1);
    chk('turn passed to team2', activeTeam === 1);

    // next reveal scores to team 2
    boardGrid.querySelectorAll('.slot')[1].click();
    chk('25 pts to team2', teams[1].score === 25);
    chk('team1 unchanged', teams[0].score === 30);

    // next team button clears strikes
    document.getElementById('nextTeamBtn').click();
    chk('strikes cleared', strikeRow.querySelectorAll('.strikeslot.on').length === 0);
    chk('turn is team3', activeTeam === 2);

    // reveal all does not award points
    var before = teams[2].score;
    document.getElementById('revealAllBtn').click();
    chk('all six revealed', boardGrid.querySelectorAll('.slot.revealed').length === 6);
    chk('reveal-all awards nothing', teams[2].score === before);

    // new board returns to picker, scores persist
    document.getElementById('newBoardBtn').click();
    chk('back at picker', fsPick.classList.contains('active'));
    chk('scores persist across boards', teams[0].score === 30 && teams[1].score === 25);

    // second board is fresh
    boardList.querySelectorAll('.boardpick')[2].click();
    chk('new board unrevealed', boardGrid.querySelectorAll('.slot.revealed').length === 0);
    chk('new question loaded', askedText.textContent.indexOf('marketing') > -1);

    // leaving to picker and back into pictionary still works
    document.querySelectorAll('[data-backmode]')[0].click();
    chk('back to mode picker', disp(modePicker) !== 'none' && disp(feudApp) === 'none');
    document.getElementById('modePictionary').click();
    chk('pictionary still enterable', disp(pictionaryApp) !== 'none');
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='FEUD'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""

src = (SITE / "index.html").read_text(encoding="utf-8")
test = src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1)
(SITE / "_feudtest.html").write_text(test, encoding="utf-8")

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=4000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_feudtest.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="FEUD">(.*?)</pre>', r.stdout, re.S)
if not m:
    print("NO RESULT - page threw before the harness ran")
    sys.exit(1)
results = html.unescape(m.group(1)).split(" | ")
fails = [x for x in results if x.startswith("FAIL")]
for x in results:
    print(("  " if x.startswith("PASS") else ">>"), x)
print()
print(f"{len(results)-len(fails)}/{len(results)} passed")
(SITE / "_feudtest.html").unlink()
sys.exit(1 if fails else 0)
