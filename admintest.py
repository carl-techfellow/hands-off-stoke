import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

# ---------------------------------------------------------------- game side
GAME_HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function picks(){ return boardList.querySelectorAll('.boardpick'); }
  function slots(){ return boardGrid.querySelectorAll('.slot'); }
  function entries(){ try { return JSON.parse(localStorage.getItem(FEUD.LOG_KEY) || '[]'); }
                      catch(e){ return []; } }
  function kinds(){ return entries().map(function(e){ return e.kind; }); }
  function last(){ var a = entries(); return a[a.length - 1] || {}; }
  try {
    localStorage.removeItem(FEUD.LOG_KEY);
    chk('shared data loaded', !!window.FEUD && FEUD.BOARDS.length >= 12);
    chk('log starts empty', entries().length === 0);

    document.getElementById('modeFeud').click();
    chk('answer key linked from the lineup screen',
        document.querySelector('.adminlink a').getAttribute('href') === 'admin.html');
    chk('answer key opens in its own tab',
        document.querySelector('.adminlink a').target === '_blank');

    document.getElementById('clearLineupBtn').click();
    picks()[0].click(); picks()[1].click(); picks()[2].click(); picks()[3].click();
    document.getElementById('startMatchBtn').click();
    chk('match-start logged', kinds().indexOf('match-start') > -1);
    chk('match-start records the lineup',
        entries()[0].detail.indexOf('R1 x1') > -1 && entries()[0].detail.indexOf('R4 x3') > -1);
    chk('round-start logged', kinds().indexOf('round-start') > -1);
    chk('round-start names the board',
        entries()[1].board === BOARDS[0].tag && entries()[1].round === 1);

    document.getElementById('fo1Btn').click();
    chk('face-off logged', last().kind === 'face-off');
    chk('face-off records the team', last().team === 'Team 1');

    document.getElementById('playBtn').click();
    chk('play decision logged', last().kind === 'play');

    var gi = document.getElementById('guessInput');
    function guess(t){ gi.value = t; document.getElementById('guessBtn').click(); }

    guess('zebra kettle bicycle');
    chk('a miss is logged', last().kind === 'guess-miss');
    chk('the miss records what was said', last().said === 'zebra kettle bicycle');
    chk('the miss records the guessing team', last().team === 'Team 1');

    guess('express interest');
    var hit = entries()[entries().length - 1];
    chk('a hit is logged', hit.kind === 'guess-hit');
    chk('the hit records what was said', hit.said === 'express interest');
    chk('the hit records the answer it landed on', hit.detail.indexOf('express my interest') > -1);
    chk('the hit records the points', hit.points === 30);
    chk('the hit records the round', hit.round === 1);
    chk('the hit records the board', hit.board === BOARDS[0].tag);

    guess('express interest');
    chk('a repeat guess is logged separately', last().kind === 'guess-repeat');

    document.getElementById('strikeBtn').click();
    chk('a strike is logged', last().kind === 'strike');
    chk('the strike counts itself', last().detail.indexOf('strike 1 of 3') > -1);

    document.getElementById('strikeBtn').click();
    document.getElementById('strikeBtn').click();
    chk('the steal is logged', kinds().indexOf('steal-open') > -1);
    chk('the steal names the stealing team', last().team === 'Team 2');

    document.getElementById('stealFailBtn').click();
    var awards = entries().filter(function(e){ return e.kind === 'award'; });
    chk('the award is logged', awards.length === 1);
    chk('the award records who took the bank', awards[0].team === 'Team 1');
    chk('the award records the amount', awards[0].points === 30);

    // scores ride along on every entry
    chk('entries carry the running score', last().s1 === 30 && last().s2 === 0);

    // steal that lands, on the next board
    document.getElementById('fo2Btn').click();
    document.getElementById('playBtn').click();
    guess(BOARDS[1].answers[0].keys[0]);
    chk('guess on a later round records round 2', last().round === 2);

    document.getElementById('abandonBtn').click();
    document.getElementById('toRound2Btn').click();
    var r2row = r2TeamRow.querySelectorAll('.team')[0];
    r2row.click();
    r2Output.value = 'zebra kettle forty two purple bicycle';
    r2Output.dispatchEvent(new Event('input'));
    document.getElementById('r2Good').click();
    chk('beat-the-board verdict logged', last().kind === 'escaped');
    chk('the verdict keeps their pasted output', last().said.indexOf('zebra kettle') > -1);
    chk('the verdict records the 25', last().points === 25);

    document.getElementById('finalScoreBtn').click();
    chk('final score logged', last().kind === 'final');
    chk('final names both teams', last().detail.indexOf('Team 1') > -1 &&
                                 last().detail.indexOf('Team 2') > -1);

    // the log survives a new match rather than being wiped
    var before = entries().length;
    document.getElementById('newMatchBtn').click();
    chk('new match does not wipe the log', entries().length === before);

    chk('every entry has a timestamp',
        entries().every(function(e){ return !!e.at && !isNaN(new Date(e.at).getTime()); }));
    chk('nothing logged without a kind', entries().every(function(e){ return !!e.kind; }));
    chk('log stays under the cap', entries().length <= 800);
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='ADMIN'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""

# ---------------------------------------------------------------- admin side
ADMIN_HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  try {
    var boards = document.querySelectorAll('#boards .board');
    chk('a card per board', boards.length === FEUD.BOARDS.length);
    chk('every answer listed',
        document.querySelectorAll('#boards tbody tr').length ===
        FEUD.BOARDS.reduce(function(n,b){ return n + b.answers.length; }, 0));

    var allKeys = FEUD.BOARDS.reduce(function(n,b){
      return n + b.answers.reduce(function(m,a){ return m + a.keys.length; }, 0); }, 0);
    chk('every keyword listed', document.querySelectorAll('#boards .key').length === allKeys);

    var strictShown = document.querySelectorAll('#boards .key.strict').length;
    var strictReal = FEUD.BOARDS.reduce(function(n,b){
      return n + b.answers.reduce(function(m,a){
        return m + a.keys.filter(function(k){ return k.indexOf(' ') > -1; }).length; }, 0); }, 0);
    chk('scan-strict keywords marked', strictShown === strictReal);

    chk('first board shows its question',
        boards[0].querySelector('.bq').textContent === FEUD.BOARDS[0].asked);
    chk('ranks run 1 to 6',
        boards[0].querySelectorAll('.rank')[0].textContent === '#1' &&
        boards[0].querySelectorAll('.rank')[5].textContent === '#6');
    var firstPts = boards[0].querySelectorAll('tbody .pts')[0].textContent;
    chk('single-value points shown', firstPts.indexOf('30') === 0);
    chk('doubled and tripled values shown',
        firstPts.indexOf('60') > -1 && firstPts.indexOf('90') > -1);
    chk('bottom answer worth 5',
        boards[0].querySelectorAll('tbody .pts')[5].textContent.indexOf('5') === 0);
    chk('board count reported',
        document.getElementById('keyCount').textContent.indexOf(String(FEUD.BOARDS.length)) === 0);

    // boards start closed so the page is not a wall of answers
    chk('boards start closed', boards[0].open === false);
    document.getElementById('expandAll').click();
    chk('open all works', boards[0].open === true && boards[boards.length-1].open === true);
    document.getElementById('collapseAll').click();
    chk('close all works', boards[0].open === false);

    // search
    var sb = document.getElementById('search');
    function find(q){ sb.value = q; sb.dispatchEvent(new Event('input')); }
    function visible(){ return [].slice.call(boards).filter(function(d){ return !d.hidden; }); }

    find('spearheaded');
    chk('search finds a board by its answer', visible().length === 1);
    chk('search found the right board', visible()[0].querySelector('.btag').textContent === 'Resume bullet');
    chk('a search hit opens itself', visible()[0].open === true);

    find('circle back');
    chk('search finds a board by a keyword only', visible().length === 1);
    chk('keyword search found the right board',
        visible()[0].querySelector('.btag').textContent === 'Status update');

    find('readme');
    chk('search matches the commit board', visible().length === 1);

    find('zzzznothing');
    chk('no matches hides everything', visible().length === 0);
    chk('empty search reports zero',
        document.getElementById('keyCount').textContent.indexOf('0 of') === 0);

    find('');
    chk('clearing the search restores every board', visible().length === FEUD.BOARDS.length);

    // fast money key
    chk('fast money questions listed',
        document.querySelectorAll('#fastmoney .board').length === FEUD.FASTMONEY.length);
    chk('fast money answers listed',
        document.querySelectorAll('#fastmoney tbody tr').length ===
        FEUD.FASTMONEY.reduce(function(n,f){ return n + f.a.length; }, 0));

    // ---- the log, seeded the way the game writes it ----
    chk('empty log shows the placeholder', document.getElementById('logEmpty').hidden === false);
    chk('empty log has no rows', document.getElementById('logBody').children.length === 0);

    localStorage.setItem(FEUD.LOG_KEY, JSON.stringify([
      { kind:'match-start', at:'2026-11-12T14:03:00.000Z', round:0, board:'',
        detail:'R1 x1 Cover letter', s1:0, s2:0 },
      { kind:'guess-hit', at:'2026-11-12T14:05:30.000Z', round:1, board:'Cover letter',
        team:'Team 1', said:'express interest', detail:'#1 I am writing to express my interest in',
        points:30, s1:0, s2:0 },
      { kind:'guess-miss', at:'2026-11-12T14:06:00.000Z', round:1, board:'Cover letter',
        team:'Team 1', said:'something, with a comma "and quotes"', detail:'not on the board',
        s1:0, s2:0 },
      { kind:'award', at:'2026-11-12T14:07:00.000Z', round:1, board:'Cover letter',
        team:'Team 1', detail:'took the bank of 30', points:30, s1:30, s2:0 }
    ]));
    document.getElementById('refreshLog').click();

    var rows = document.getElementById('logBody').children;
    chk('log rows rendered', rows.length === 4);
    chk('placeholder hidden once there are rows',
        document.getElementById('logEmpty').hidden === true);
    chk('log reports the count',
        document.getElementById('logCount').textContent.indexOf('4 entries') > -1);
    chk('a hit is labelled hit', rows[1].querySelector('.kind').textContent === 'hit');
    chk('a hit is coloured', rows[1].querySelector('.kind').className.indexOf('hit') > -1);
    chk('a miss is labelled miss', rows[2].querySelector('.kind').textContent === 'miss');
    chk('the round is shown', rows[1].querySelector('.rnd').textContent === '1');
    chk('round zero shows a dash', rows[0].querySelector('.rnd').textContent === '\u2014');
    chk('what they said is shown', rows[1].querySelector('.said').textContent === 'express interest');
    chk('points are shown', rows[1].querySelector('.pts').textContent === '30');
    chk('missing points show a dash', rows[2].querySelector('.pts').textContent === '\u2014');
    chk('running score is shown', rows[3].querySelector('.score').textContent === '30\u20130');
    chk('a clock time is shown', /^\d\d:\d\d:\d\d$/.test(rows[0].querySelector('.when').textContent));

    // clearing is two-step so a stray click does not wipe a match
    var clearBtn = document.getElementById('clearLog');
    clearBtn.click();
    chk('first clear click only arms it',
        document.getElementById('logBody').children.length === 4 &&
        clearBtn.textContent.indexOf('Really') > -1);
    clearBtn.click();
    chk('second clear click empties it', document.getElementById('logBody').children.length === 0);
    chk('clear wipes storage', (localStorage.getItem(FEUD.LOG_KEY) || '') === '');
    chk('clear restores the button label', clearBtn.textContent === 'Clear the log');
    chk('placeholder returns', document.getElementById('logEmpty').hidden === false);

    chk('back link points at the game',
        document.querySelector('nav a').getAttribute('href') === 'index.html');
    chk('the page warns about the projector',
        document.querySelector('.warn').textContent.toLowerCase().indexOf('projector') > -1);
    chk('provenance stated in the footer',
        document.querySelector('footer').textContent.indexOf('not measured') > -1);

    // the run-through: the host should not have to reconstruct the order of play
    var run = document.querySelectorAll('#run, .runlist');
    chk('a how-to-run section exists', document.getElementById('run') !== null);
    chk('the run-through is a numbered sequence',
        document.querySelectorAll('.runlist')[0].tagName === 'OL');
    chk('the run-through covers the whole match',
        document.querySelectorAll('.runlist')[0].children.length >= 8);
    var runText = document.querySelectorAll('.runlist')[0].textContent.toLowerCase();
    ['two windows', 'draw', 'play', 'pass', 'steal', 'sudden death', 'fast money',
     'beat the board', 'debrief'].forEach(function(bit){
      chk('run-through mentions ' + bit, runText.indexOf(bit) > -1);
    });
    chk('debrief questions supplied',
        document.querySelectorAll('.runlist.tight')[0].children.length === 3);
    chk('how-to-run is in the nav',
        document.querySelector('nav a[href="#run"]') !== null);
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='ADMIN'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""


def run(page, harness, tmp):
    src = (SITE / page).read_text(encoding="utf-8")
    assert src.count("})();\n</script>") >= 1, "no injection point in " + page
    # inject into the LAST script block so admin.html's own IIFE is the target
    idx = src.rfind("})();\n</script>")
    test = src[:idx] + harness + src[idx:]
    (SITE / tmp).write_text(test, encoding="utf-8")
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                        "--virtual-time-budget=4000", "--dump-dom",
                        "file:///C:/tmp-hoff/site/" + tmp],
                       capture_output=True, text=True, errors="ignore")
    (SITE / tmp).unlink()
    m = re.search(r'<pre id="ADMIN">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return None
    return html.unescape(m.group(1)).split(" | ")


total = fails = 0
for label, page, harness, tmp in [
        ("game logging", "index.html", GAME_HARNESS, "_admingame.html"),
        ("admin page", "admin.html", ADMIN_HARNESS, "_adminpage.html")]:
    print("=== " + label + " ===")
    results = run(page, harness, tmp)
    if results is None:
        print("NO RESULT - page threw before the harness ran")
        sys.exit(1)
    for x in results:
        print(("  " if x.startswith("PASS") else ">>"), x)
    f = len([x for x in results if x.startswith("FAIL")])
    total += len(results)
    fails += f
    print()

print(f"{total-fails}/{total} passed")
sys.exit(1 if fails else 0)
