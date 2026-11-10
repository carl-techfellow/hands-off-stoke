import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function disp(el){ return getComputedStyle(el).display; }
  function picks(){ return boardList.querySelectorAll('.boardpick'); }
  function slots(){ return boardGrid.querySelectorAll('.slot'); }
  function startBtn(){ return document.getElementById('startMatchBtn'); }
  // the app draws at random; tests that assert on specific boards force the order
  function fixLineup(){
    document.getElementById('clearLineupBtn').click();
    picks()[0].click(); picks()[1].click(); picks()[2].click(); picks()[3].click();
  }
  function faceoff(i){ document.getElementById(i === 0 ? 'fo1Btn' : 'fo2Btn').click(); }
  function strike3(){ var b = document.getElementById('strikeBtn'); b.click(); b.click(); b.click(); }
  // win a round outright: face-off -> play -> reveal one slot -> award
  function winRound(by, slotIdx){
    faceoff(by);
    document.getElementById('playBtn').click();
    slots()[slotIdx === undefined ? 0 : slotIdx].click();
    document.getElementById('awardBtn').click();
  }
  try {
    document.getElementById('modeFeud').click();
    chk('feud rendered', disp(feudApp) !== 'none');
    chk('pictionary not rendered', disp(pictionaryApp) === 'none');
    chk('lands on lineup builder', fsPick.classList.contains('active'));
    chk('six boards offered', picks().length === 6);
    chk('four lineup slots shown', lineupEl.querySelectorAll('.lslot').length === 4);

    // ---- categories are drawn automatically ----
    chk('lineup auto-filled on arrival', lineup.length === 4);
    chk('all four slots filled', lineupEl.querySelectorAll('.lslot.filled').length === 4);
    chk('start ready without any picking', startBtn().disabled === false);
    chk('draw has no repeats', new Set(lineup.map(function(b){ return b.tag; })).size === 4);
    chk('every drawn board is a real board',
        lineup.every(function(b){ return BOARDS.indexOf(b) > -1; }));
    chk('drawn boards marked used in the swap list',
        boardList.querySelectorAll('.boardpick.used').length === 4);

    // reshuffle keeps a legal four-board draw
    var before = lineup.map(function(b){ return b.tag; }).join(',');
    var changed = false;
    for (var tries = 0; tries < 25 && !changed; tries++) {
      document.getElementById('shuffleLineupBtn').click();
      if (lineup.map(function(b){ return b.tag; }).join(',') !== before) changed = true;
    }
    chk('reshuffle produces a different draw', changed);
    chk('reshuffle still draws four', lineup.length === 4);
    chk('reshuffle has no repeats', new Set(lineup.map(function(b){ return b.tag; })).size === 4);

    document.getElementById('clearLineupBtn').click();
    chk('clear empties the lineup', lineup.length === 0);
    chk('clear disables start', startBtn().disabled === true);
    chk('clear asks for four more', document.getElementById('lineupHint').textContent.indexOf('4 more') > -1);

    // ---- manual swapping still works ----
    picks()[0].click();
    chk('one board picked', lineup.length === 1);
    chk('picked board marked used', picks()[0].classList.contains('used'));
    chk('slot 1 filled', lineupEl.querySelectorAll('.lslot.filled').length === 1);
    chk('still disabled at one', startBtn().disabled === true);
    chk('hint counts the gap', document.getElementById('lineupHint').textContent.indexOf('3 more') > -1);

    picks()[0].click();
    chk('re-click removes from lineup', lineup.length === 0);
    chk('used mark cleared', picks()[0].classList.contains('used') === false);

    picks()[0].click(); picks()[1].click(); picks()[2].click(); picks()[3].click();
    chk('four picked', lineup.length === 4);
    chk('start enabled at four', startBtn().disabled === false);
    picks()[4].click();
    chk('cannot pick a fifth', lineup.length === 4);
    chk('lineup order preserved', lineup[0].tag === BOARDS[0].tag && lineup[3].tag === BOARDS[3].tag);
    chk('multipliers labelled on lineup',
        lineupEl.textContent.indexOf('\u00d72') > -1 && lineupEl.textContent.indexOf('\u00d73') > -1);

    fixLineup();
    startBtn().click();

    // ---- round 1: face-off ----
    chk('match starts on board screen', fsBoard.classList.contains('active'));
    chk('round index starts at 0', roundIdx === 0);
    chk('first board is lineup[0]', currentBoard.tag === BOARDS[0].tag);
    chk('six slots built', slots().length === 6);
    chk('starts in face-off', phase === 'faceoff');
    chk('face-off bar visible', document.getElementById('faceoffBar').hidden === false);
    chk('face-off buttons visible', document.getElementById('faceoffBtns').hidden === false);
    chk('play buttons hidden in face-off', document.getElementById('playBtns').hidden === true);
    chk('nobody shown in control yet', teamRow.querySelectorAll('.team.control').length === 0);
    chk('round chip shows single points', roundChip.textContent.indexOf('single points') > -1);
    chk('round chip shows the target', roundChip.textContent.indexOf('300') > -1);
    chk('round 1 slot 1 worth 30', slots()[0].querySelector('.spts').textContent === '30');

    faceoff(1);
    chk('face-off winner recorded', faceoffWinner === 1);
    chk('moves to play-or-pass', phase === 'playpass');
    chk('play/pass buttons visible', document.getElementById('playpassBtns').hidden === false);

    // ---- pass hands control to the other team ----
    document.getElementById('passBtn').click();
    chk('pass gives control to team 1', control === 0);
    chk('phase is play after pass', phase === 'play');
    chk('team 1 card marked control', teamRow.querySelectorAll('.team')[0].classList.contains('control'));

    // ---- reveals bank, they do not score directly ----
    slots()[0].click();
    chk('30 into bank', bank === 30);
    chk('nobody scored on reveal', teams[0].score === 0 && teams[1].score === 0);
    slots()[0].click();
    chk('no double-bank on one slot', bank === 30);
    slots()[1].click();
    chk('bank accumulates to 55', bank === 55);

    // ---- three strikes opens the steal ----
    strike3();
    chk('three strikes marked', strikeRow.querySelectorAll('.strikeslot.on').length === 3);
    chk('phase is steal', phase === 'steal');
    chk('steal banner shown', document.getElementById('stealBanner').hidden === false);
    chk('strike button hidden in steal', document.getElementById('strikeBtn').hidden === true);
    chk('steal-failed button shown', document.getElementById('stealFailBtn').hidden === false);

    // a successful steal takes the bank and ends the round
    slots()[2].click();
    chk('steal pays the other team', teams[1].score === 75);
    chk('controlling team got nothing', teams[0].score === 0);
    chk('round advanced after award', roundIdx === 1);
    chk('bank reset for new round', bank === 0);
    chk('strikes reset for new round', strikes === 0);
    chk('back to face-off', phase === 'faceoff');
    chk('board 2 loaded', currentBoard.tag === BOARDS[1].tag);
    chk('new board unrevealed', boardGrid.querySelectorAll('.slot.revealed').length === 0);

    // ---- round 2 still single points ----
    chk('round 2 is single points', multiplier() === 1);
    chk('round 2 slot 1 still 30', slots()[0].querySelector('.spts').textContent === '30');
    faceoff(0);
    document.getElementById('playBtn').click();
    chk('play keeps control with winner', control === 0);
    strike3();
    document.getElementById('stealFailBtn').click();
    chk('failed steal pays control team', teams[0].score === 0);
    chk('round 3 reached', roundIdx === 2);

    // ---- round 3 doubles ----
    chk('round 3 multiplier is 2', multiplier() === 2);
    chk('round 3 slot 1 worth 60', slots()[0].querySelector('.spts').textContent === '60');
    chk('round chip shows 2x', roundChip.textContent.indexOf('2\u00d7') > -1);
    faceoff(0);
    document.getElementById('playBtn').click();
    slots()[0].click();
    chk('doubled points banked', bank === 60);
    document.getElementById('awardBtn').click();
    chk('team 1 has 60', teams[0].score === 60);
    chk('round 4 reached', roundIdx === 3);

    // ---- round 4 triples ----
    chk('round 4 multiplier is 3', multiplier() === 3);
    chk('round 4 slot 1 worth 90', slots()[0].querySelector('.spts').textContent === '90');
    chk('round chip shows 3x', roundChip.textContent.indexOf('3\u00d7') > -1);

    // reveal-all pays nobody
    var b0 = teams[0].score, b1 = teams[1].score;
    document.getElementById('revealAllBtn').click();
    chk('reveal all shows six', boardGrid.querySelectorAll('.slot.revealed').length === 6);
    chk('reveal all pays nobody', teams[0].score === b0 && teams[1].score === b1);

    // ---- four rounds done, nobody at 300 -> sudden death ----
    faceoff(0);
    document.getElementById('playBtn').click();
    document.getElementById('awardBtn').click();
    chk('sudden death after four rounds', fsSudden.classList.contains('active'));
    chk('sudden death uses an unplayed board', lineup.indexOf(sdBoard) === -1);
    chk('sudden death shows the top answer',
        document.getElementById('sdAsked').textContent.indexOf(sdBoard.answers[0]) > -1);

    document.getElementById('sd2Btn').click();
    chk('sudden death winner clears the target', teams[1].score >= 300);
    chk('sudden death leads to fast money', fsFast.classList.contains('active'));

    // ---- fast money ----
    chk('fast money names the winner',
        document.getElementById('fastWinner').textContent.indexOf('Team 2') > -1);
    chk('five fast money questions', document.getElementById('fastGrid').querySelectorAll('.fastrow').length === 5);
    chk('entering player 1 first', fastPlayer === 0);
    chk('combined starts at zero', fastScore(0) + fastScore(1) === 0);
    chk('target shown', document.getElementById('fastTotal').textContent.indexOf('200') > -1);

    function fopt(qi, ai){
      return document.getElementById('fastGrid').querySelectorAll('.fastrow')[qi]
             .querySelectorAll('.fopt')[ai];
    }
    fopt(0, 0).click();
    chk('p1 top answer scores 30', fastScore(0) === 30);
    fopt(1, 1).click();
    chk('p1 second answer adds 25', fastScore(0) === 55);
    fopt(1, 1).click();
    chk('re-click clears the pick', fastScore(0) === 30);
    fopt(1, 1).click();
    var missBtn = document.getElementById('fastGrid').querySelectorAll('.fastrow')[2]
                  .querySelector('.fopt.miss');
    missBtn.click();
    chk('no-match scores nothing', fastScore(0) === 55);

    document.getElementById('fastPlayerToggle').click();
    chk('toggled to player 2', fastPlayer === 1);
    chk('player 1 score preserved', fastScore(0) === 55);
    chk('duplicate marked for player 2', fopt(0, 0).classList.contains('dupe'));
    fopt(0, 0).click();
    chk('player 2 cannot repeat player 1', fastScore(1) === 0);
    fopt(0, 1).click();
    chk('player 2 scores a fresh answer', fastScore(1) === 25);
    chk('combined total reported',
        document.getElementById('fastTotal').textContent.indexOf('80') > -1);
    chk('no win banner below target', document.getElementById('fastResult').hidden === true);

    // clear 200 combined
    fopt(1, 0).click(); fopt(2, 0).click(); fopt(3, 0).click(); fopt(4, 0).click();
    chk('player 2 at 145', fastScore(1) === 145);
    chk('combined is 200', fastScore(0) + fastScore(1) === 200);
    chk('win banner at target', document.getElementById('fastResult').hidden === false);

    document.getElementById('fast20Btn').addEventListener('click', function(){});
    document.getElementById('fast20Btn').click();
    chk('20s timer resets to player 1', fastPlayer === 0);
    chk('timer shows 20', document.getElementById('fastTimer').textContent === '20');
    document.getElementById('fast25Btn').click();
    chk('25s timer switches to player 2', fastPlayer === 1);
    chk('timer shows 25', document.getElementById('fastTimer').textContent === '25');

    // ---- beat the board still reachable after the match ----
    document.getElementById('toRound2Btn').click();
    chk('beat the board reachable', fsRound2.classList.contains('active'));
    chk('avoid chips listed', avoidList.querySelectorAll('.ac').length === 6);

    // ---- new match wipes everything and draws again ----
    document.getElementById('newMatchBtn').click();
    chk('new match returns to picker', fsPick.classList.contains('active'));
    chk('new match draws a fresh four', lineup.length === 4);
    chk('new match draw has no repeats', new Set(lineup.map(function(b){ return b.tag; })).size === 4);
    chk('new match zeroes scores', teams[0].score === 0 && teams[1].score === 0);
    chk('new match resets round', roundIdx === 0);
    chk('new match leaves start ready', startBtn().disabled === false);

    // ---- end-match-early path ----
    fixLineup();
    startBtn().click();
    faceoff(0);
    document.getElementById('playBtn').click();
    document.getElementById('revealAllBtn').click();
    slots()[0].click(); slots()[1].click(); slots()[2].click();
    slots()[3].click(); slots()[4].click(); slots()[5].click();
    chk('reveal-all slots no longer bank', bank === 0);

    document.getElementById('abandonBtn').click();
    chk('end-match-early goes to fast money', fsFast.classList.contains('active'));

    // ---- mode isolation ----
    document.querySelectorAll('[data-backmode]')[0].click();
    document.getElementById('modePictionary').click();
    chk('pictionary still enterable', disp(pictionaryApp) !== 'none');
    chk('feud hidden from pictionary', disp(feudApp) === 'none');
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='MATCH'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""

src = (SITE / "index.html").read_text(encoding="utf-8")
test = src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1)
(SITE / "_matchtest.html").write_text(test, encoding="utf-8")

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=4000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_matchtest.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="MATCH">(.*?)</pre>', r.stdout, re.S)
if not m:
    print("NO RESULT - page threw before the harness ran")
    sys.exit(1)
results = html.unescape(m.group(1)).split(" | ")
fails = [x for x in results if x.startswith("FAIL")]
for x in results:
    print(("  " if x.startswith("PASS") else ">>"), x)
print()
print(f"{len(results)-len(fails)}/{len(results)} passed")
(SITE / "_matchtest.html").unlink()
sys.exit(1 if fails else 0)
