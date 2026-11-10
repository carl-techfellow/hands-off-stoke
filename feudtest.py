import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function disp(el){ return getComputedStyle(el).display; }
  function slots(){ return boardGrid.querySelectorAll('.slot'); }
  function strikeBtn(){ return document.getElementById('strikeBtn'); }
  try {
    document.getElementById('modeFeud').click();
    chk('feud rendered', disp(feudApp) !== 'none');
    chk('pictionary not rendered', disp(pictionaryApp) === 'none');
    chk('lands on board picker', fsPick.classList.contains('active'));
    chk('six boards listed', boardList.querySelectorAll('.boardpick').length === 6);

    boardList.querySelectorAll('.boardpick')[0].click();
    chk('board screen active', fsBoard.classList.contains('active'));
    chk('six slots built', slots().length === 6);
    chk('exactly two teams', teamRow.querySelectorAll('.team').length === 2);
    chk('team1 starts in control', teamRow.querySelectorAll('.team')[0].className.indexOf('control') > -1);
    chk('bank starts empty', bank === 0);

    // reveals feed the BANK, not a team score
    slots()[0].click();
    chk('slot revealed', slots()[0].classList.contains('revealed'));
    chk('30 into bank', bank === 30);
    chk('no team scored yet', teams[0].score === 0 && teams[1].score === 0);

    slots()[0].click();
    chk('no double-bank on same slot', bank === 30);

    slots()[1].click();
    chk('bank accumulates to 55', bank === 55);

    // two strikes: no steal yet
    strikeBtn().click(); strikeBtn().click();
    chk('two strikes marked', strikeRow.querySelectorAll('.strikeslot.on').length === 2);
    chk('no steal at two strikes', stealMode === false);
    chk('control unchanged by strikes', activeTeam === 0);

    // third strike opens the steal
    strikeBtn().click();
    chk('steal opens at three', stealMode === true);
    chk('steal banner visible', document.getElementById('stealBanner').hidden === false);
    chk('steal button appears', document.getElementById('stealFailBtn').hidden === false);
    chk('strike button hides during steal', strikeBtn().hidden === true);

    // a successful steal hands the whole bank to the other team
    slots()[2].click();
    chk('steal pays team2 the bank', teams[1].score === 75);
    chk('control team got nothing', teams[0].score === 0);
    chk('bank emptied after steal', bank === 0);
    chk('steal mode closed', stealMode === false);
    chk('strikes cleared after award', strikeRow.querySelectorAll('.strikeslot.on').length === 0);

    // failed steal: bank goes to the controlling team
    boardList.querySelectorAll('.boardpick')[1].click();  // fresh board
    chk('new board clears bank', bank === 0);
    slots()[0].click();
    strikeBtn().click(); strikeBtn().click(); strikeBtn().click();
    chk('steal open again', stealMode === true);
    document.getElementById('stealFailBtn').click();
    chk('failed steal pays control', teams[0].score === 30);
    chk('bank emptied', bank === 0);

    // manual award
    boardList.querySelectorAll('.boardpick')[2].click();
    slots()[0].click();
    slots()[1].click();
    chk('bank is 55', bank === 55);
    document.getElementById('awardBtn').click();
    chk('award pays control team', teams[0].score === 85);
    chk('bank cleared by award', bank === 0);

    // switch control
    var before = activeTeam;
    document.getElementById('nextTeamBtn').click();
    chk('control switches', activeTeam === 1 - before);

    // reveal all awards nothing directly
    var t0 = teams[0].score, t1 = teams[1].score;
    document.getElementById('revealAllBtn').click();
    chk('all six revealed', boardGrid.querySelectorAll('.slot.revealed').length === 6);
    chk('reveal-all pays nobody', teams[0].score === t0 && teams[1].score === t1);

    // back out to pictionary
    document.querySelectorAll('[data-backmode]')[0].click();
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
