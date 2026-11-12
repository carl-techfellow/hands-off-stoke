import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function setOut(v){ r2Output.value = v; r2Output.dispatchEvent(new Event('input')); }
  function r2team(i){ return r2TeamRow.querySelectorAll('.team')[i]; }
  function picks(){ return boardList.querySelectorAll('.boardpick'); }
  function slots(){ return boardGrid.querySelectorAll('.slot'); }
  try {
    document.getElementById('modeFeud').click();
    // the app draws at random inside each difficulty band; force the first board
    // of every band so the assertions below know which boards are in play
    function firstAtLevel(l){
      for (var i = 0; i < BOARDS.length; i++) if (BOARDS[i].level === l) return i;
      return -1;
    }
    function expected(i){ return BOARDS[firstAtLevel(ROUND_LEVELS[i])]; }
    document.getElementById('clearLineupBtn').click();
    ROUND_LEVELS.forEach(function(l){ picks()[firstAtLevel(l)].click(); });
    document.getElementById('startMatchBtn').click();

    // round 1: team 1 wins the face-off, plays, takes 30
    document.getElementById('fo1Btn').click();
    document.getElementById('playBtn').click();
    slots()[0].click();
    document.getElementById('awardBtn').click();
    chk('setup: team1 has 30 from round 1', teams[0].score === 30);
    chk('setup: now on the second drawn board', currentBoard.tag === expected(1).tag);

    // cut the match short and run the teaching round
    document.getElementById('abandonBtn').click();
    chk('abandon lands on fast money', fsFast.classList.contains('active'));
    document.getElementById('toRound2Btn').click();
    chk('beat the board active', fsRound2.classList.contains('active'));
    chk('avoid chips listed', avoidList.querySelectorAll('.ac').length === 6);
    chk('question carried over',
        document.getElementById('r2Asked').textContent === expected(1).asked);
    chk('two teams in the teaching round', r2TeamRow.querySelectorAll('.team').length === 2);
    chk('judge panel hidden initially', r2Judge.hidden === true);
    chk('badges clear on entry', r2TeamRow.querySelectorAll('.tbadge').length === 0);
    chk('match scores carried in', r2TeamRow.textContent.indexOf('30') > -1);
    chk('write timer armed at 90', document.getElementById('r2Timer').textContent === '90');

    // busted answer
    r2team(1).click();
    chk('judge panel opens', r2Judge.hidden === false);
    chk('judged team highlighted', r2team(1).classList.contains('control'));
    var topAnswer = expected(1).answers[0].text;
    setOut('Draft one: ' + topAnswer + ' the rest of the sentence.');
    chk('scan flags busted', r2Scan.className.indexOf('busted') > -1);
    chk('busted names the hit', r2Scan.textContent.indexOf(topAnswer) > -1);

    // clean answer - deliberately unlike anything on any board
    setOut('zebra kettle forty two purple bicycle coffee');
    chk('scan flags clean', r2Scan.className.indexOf('clean') > -1);

    // a multi-word trigger counts as busted even when the exact answer is absent
    var multi = null;
    expected(1).answers.forEach(function(a){
      a.keys.forEach(function(k){ if (!multi && k.indexOf(' ') > -1) multi = k; });
    });
    if (multi) {
      setOut('Draft two: ' + multi + ' on the data pipeline.');
      chk('multi-word trigger also busts', r2Scan.className.indexOf('busted') > -1);
    } else {
      chk('multi-word trigger also busts (no multi-word key on this board)', true);
    }
    setOut('zebra kettle forty two purple bicycle coffee');
    chk('clean again after the trigger test', r2Scan.className.indexOf('clean') > -1);

    document.getElementById('r2Good').click();
    chk('team2 +25', teams[1].score === 25);
    chk('panel closes after judging', r2Judge.hidden === true);
    chk('badge shows escaped', r2TeamRow.querySelectorAll('.tbadge.ok').length === 1);

    // no double award
    r2team(1).click();
    document.getElementById('r2Good').click();
    chk('no double award on re-judge', teams[1].score === 25);

    // flip to zero reverses the award
    r2team(1).click();
    document.getElementById('r2Zero').click();
    chk('flip to zero removes points', teams[1].score === 0);
    chk('badge now no-points', r2TeamRow.querySelectorAll('.tbadge.no').length === 1);

    // flip back re-awards exactly once
    r2team(1).click();
    document.getElementById('r2Good').click();
    chk('flip back re-awards once', teams[1].score === 25);

    // per-team text persistence
    r2team(0).click();
    chk('other team starts empty', r2Output.value === '');
    setOut('team one wrote this');
    r2team(1).click();
    chk('team2 text remembered', r2Output.value.indexOf('zebra kettle') > -1);
    r2team(0).click();
    chk('team1 text remembered', r2Output.value === 'team one wrote this');

    chk('match score intact', teams[0].score === 30);

    // empty paste clears the verdict rather than claiming clean
    setOut('');
    chk('empty paste shows no verdict', r2Scan.textContent === '');

    document.getElementById('finalScoreBtn').click();
    chk('winner line shown', winnerLine.hidden === false);
    chk('winner is team1 at 30', winnerLine.textContent.indexOf('30') > -1);

    // re-entry clears the teaching round but keeps match scores
    document.getElementById('toRound2Btn').click();
    chk('re-entry clears badges', r2TeamRow.querySelectorAll('.tbadge').length === 0);
    chk('re-entry clears pasted text', (teams[1].r2text || '') === '');
    chk('re-entry hides the winner line', winnerLine.hidden === true);
    chk('re-entry keeps match scores', teams[0].score === 30 && teams[1].score === 25);

    // a new match wipes the teaching round too
    document.getElementById('newMatchBtn').click();
    chk('new match back to picker', fsPick.classList.contains('active'));
    chk('new match redraws the categories', lineup.length === 4);
    chk('new match zeroes scores', teams[0].score === 0 && teams[1].score === 0);
    chk('new match clears r2 verdicts', !teams[0].r2 && !teams[1].r2);

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
