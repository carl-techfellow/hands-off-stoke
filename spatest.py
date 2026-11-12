import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

# ------------------------------------------------------------------ behaviour
HARNESS = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  function picks(){ return boardList.querySelectorAll('.boardpick'); }
  function slots(){ return boardGrid.querySelectorAll('.slot'); }
  function coach(){ return document.getElementById('coachText').textContent; }
  function pcoach(){ return document.getElementById('pCoachText').textContent; }
  function steps(){ return document.querySelectorAll('#stepper .step'); }
  function nowStep(){
    var s = document.querySelector('#stepper .step.now');
    return s ? s.textContent : '(none)';
  }
  function doneCount(){ return document.querySelectorAll('#stepper .step.done').length; }
  function hash(){ return location.hash; }

  function finish(){
    var o = document.createElement('pre'); o.id='SPA'; o.textContent = log.join(' | ');
    document.body.appendChild(o);
  }

  try {
    // ---------------- the shell ----------------
    chk('picker is the default route', hash() === '#/' || hash() === '');
    chk('one app bar per mode', document.querySelectorAll('.appbar').length === 2);
    chk('feud bar carries a back control',
        feudApp.querySelector('.appbar [data-backmode]') !== null);
    chk('pictionary bar carries a back control',
        pictionaryApp.querySelector('.appbar [data-backmode]') !== null);
    chk('feud bar links the answer key',
        feudApp.querySelector('.appbar a.key').getAttribute('href') === 'admin.html');
    chk('no floating back button left in feud',
        feudApp.querySelector('.backmode') === null);

    // ---------------- pictionary: coach + route per screen ----------------
    document.getElementById('modePictionary').click();
    chk('entering pictionary sets the route', hash() === '#/pictionary/0');
    chk('screen 0 has a next step', pcoach().length > 20);
    chk('screen 0 tells them to press start', pcoach().toLowerCase().indexOf('start') > -1);

    var seen = {};
    for (var i = 0; i < 6; i++) {
      goTo(i);
      seen[pcoach()] = 1;
      if (i === 1) chk('screen 1 names person A', pcoach().indexOf('Person A') > -1);
      if (i === 2) chk('screen 2 points at the chatbot', pcoach().indexOf('chatbot') > -1);
      if (i === 4) chk('screen 4 gives person B the clock', pcoach().indexOf('45 seconds') > -1);
      if (i === 5) chk('final screen says swap', pcoach().toLowerCase().indexOf('swap') > -1);
      chk('screen ' + i + ' routes to its own url', hash() === '#/pictionary/' + i);
    }
    chk('every pictionary screen has its own next step', Object.keys(seen).length === 6);
    chk('the last step reads as finished',
        document.getElementById('pCoach').className.indexOf('done') > -1);

    // ---------------- feud: lineup ----------------
    document.querySelectorAll('[data-backmode]')[0].click();
    chk('back to the picker clears the route', hash() === '#/');
    document.getElementById('modeFeud').click();
    chk('feud lineup has a route', hash() === '#/feud/lineup');
    chk('stepper built', steps().length === 7);
    chk('stepper starts on the draw', nowStep() === 'Draw');
    chk('nothing done yet', doneCount() === 0);

    var nav = document.getElementById('sideNav');
    function navBtn(g){ return nav.querySelector('[data-go="' + g + '"]'); }
    chk('sidebar nav built with four stops', nav.querySelectorAll('button').length === 4);
    chk('lineup is the current stop', navBtn('lineup').classList.contains('on'));
    chk('match stops locked before a match',
        navBtn('board').disabled && navBtn('fast').disabled && navBtn('beat').disabled);
    chk('lineup step says start the match', coach().toLowerCase().indexOf('start the match') > -1);

    function firstAtLevel(l){
      for (var i = 0; i < BOARDS.length; i++) if (BOARDS[i].level === l) return i;
      return -1;
    }
    document.getElementById('clearLineupBtn').click();
    chk('an empty lineup asks for four more rounds', coach().indexOf('4 more rounds') > -1);
    chk('the empty lineup explains the difficulty rule',
        coach().toLowerCase().indexOf('difficulty') > -1);
    picks()[firstAtLevel(1)].click();
    chk('the ask counts down', coach().indexOf('3 more rounds') > -1);
    ROUND_LEVELS.slice(1).forEach(function(l){ picks()[firstAtLevel(l)].click(); });
    chk('a full lineup says start again', coach().toLowerCase().indexOf('start the match') > -1);
    chk('the full lineup explains the ramp',
        coach().indexOf(LEVEL_NAMES[1]) > -1 && coach().indexOf(LEVEL_NAMES[4]) > -1);

    // guided instructions, in the game, before anyone presses start
    var how = document.querySelector('.howbox');
    chk('a how-it-runs block sits on the lineup screen', how !== null);
    chk('the how-it-runs block starts closed', how.open === false);
    chk('it walks the whole match', how.querySelectorAll('.howlist li').length >= 6);
    var howText = how.textContent.toLowerCase();
    ['easy to hard', 'face-off', 'keywords', 'three misses', '300', 'beat the board']
      .forEach(function(bit){
        chk('the walkthrough covers ' + bit, howText.indexOf(bit) > -1);
      });

    // ---------------- feud: a round ----------------
    document.getElementById('startMatchBtn').click();
    chk('the board has its own route', hash() === '#/feud/board');
    chk('stepper moves to round 1', nowStep() === 'R1');
    chk('the draw is marked done', doneCount() === 1);
    chk('match stops unlock once a match starts',
        !navBtn('board').disabled && !navBtn('fast').disabled && !navBtn('beat').disabled);
    chk('the board is the current stop', navBtn('board').classList.contains('on'));
    chk('face-off step explains the buzz', coach().toLowerCase().indexOf('buzz') > -1);
    chk('round 1 face-off frames it as a warm-up',
        coach().toLowerCase().indexOf('warm-up') > -1);
    chk('face-off step says read it out loud', coach().toLowerCase().indexOf('out loud') > -1);
    chk('bar score starts level',
        document.getElementById('abScore').textContent.replace(/\s/g, '') === '0\u20130');

    // ---- the pinned action footer ----
    var abar = document.getElementById('actionBar');
    chk('the board controls live in a footer bar', abar !== null);
    chk('the footer is pinned to the viewport bottom',
        getComputedStyle(abar).position === 'sticky');
    chk('the footer holds every action group',
        abar.contains(document.getElementById('faceoffBtns')) &&
        abar.contains(document.getElementById('playBtns')) &&
        abar.contains(document.getElementById('abandonBtn')));
    function barLive(){
      return [].slice.call(abar.querySelectorAll('.fbtns')).some(function(g){ return !g.hidden; });
    }
    chk('the footer is never empty during the face-off', barLive());

    document.getElementById('fo1Btn').click();
    chk('the footer is never empty during play-or-pass', barLive());
    chk('play-or-pass step asks the question', coach().toLowerCase().indexOf('pass') > -1);
    chk('play-or-pass step names the winner', coach().indexOf('Team 1') > -1);

    document.getElementById('playBtn').click();
    chk('play step points at the guess box', coach().toLowerCase().indexOf('box') > -1);
    chk('play step mentions keywords', coach().toLowerCase().indexOf('keyword') > -1);
    chk('play step warns about three misses', coach().indexOf('Three misses') > -1);

    chk('the footer is never empty during play', barLive());

    var gi = document.getElementById('guessInput');
    function guess(t){ gi.value = t; document.getElementById('guessBtn').click(); }

    guess('express interest');
    chk('after a hit the step counts what is left', coach().indexOf('5 answers left') > -1);
    chk('after a hit the step shows the bank', coach().indexOf('30 in the bank') > -1);

    document.getElementById('strikeBtn').click();
    document.getElementById('strikeBtn').click();
    chk('two strikes gets its own warning', coach().indexOf('Two strikes') > -1);
    chk('the warning names the other team', coach().indexOf('Team 2') > -1);

    document.getElementById('strikeBtn').click();
    chk('the steal step explains one guess', coach().toLowerCase().indexOf('one guess') > -1);
    chk('the steal step states the stakes', coach().indexOf('30') > -1);

    document.getElementById('stealFailBtn').click();
    chk('round 2 on the stepper', nowStep() === 'R2');
    chk('two steps done', doneCount() === 2);
    chk('bar score updated', document.getElementById('abScore').textContent.indexOf('30') > -1);

    // clear a board to see the cleared-board step
    document.getElementById('fo1Btn').click();
    document.getElementById('playBtn').click();
    for (var k = 0; k < 6; k++) slots()[k].click();
    chk('a cleared board says award it', coach().toLowerCase().indexOf('award bank') > -1);

    document.getElementById('awardBtn').click();
    chk('round 3 reached on the stepper', nowStep() === 'R3 \u00d72');

    // ---------------- fast money + beat the board ----------------
    document.getElementById('abandonBtn').click();
    chk('fast money has a route', hash() === '#/feud/fast-money');
    chk('fast money is its own step', nowStep() === 'Fast Money');
    chk('fast money step gives both clocks',
        coach().indexOf('20-second') > -1 && coach().indexOf('25 seconds') > -1);
    chk('fast money step names the target', coach().indexOf('200 combined') > -1);

    // ---------------- sidebar jumps ----------------
    chk('fast money is the current stop', navBtn('fast').classList.contains('on'));
    var fmFirstQ = fastSet[0].q;
    var fopt0 = document.getElementById('fastGrid').querySelectorAll('.fastrow')[0]
                 .querySelectorAll('.fopt')[0];
    fopt0.click();   // player 1 banks the top answer before we wander off
    var fmScore = fastScore(0);

    navBtn('board').click();
    chk('nav jumps back to the board', fsBoard.classList.contains('active'));
    chk('the jump routes the url', hash() === '#/feud/board');
    chk('the board becomes the current stop', navBtn('board').classList.contains('on'));

    navBtn('fast').click();
    chk('nav returns to fast money', fsFast.classList.contains('active'));
    chk('returning does not redraw the questions', fastSet[0].q === fmFirstQ);
    chk('returning keeps the entries', fastScore(0) === fmScore && fmScore > 0);

    navBtn('beat').click();
    chk('nav reaches beat the board', fsRound2.classList.contains('active'));
    chk('the jump arrives at a set-up screen', avoidList.querySelectorAll('.ac').length === 6);
    chk('beat the board routes its url', hash() === '#/feud/beat-the-board');
    chk('beat the board becomes the current stop', navBtn('beat').classList.contains('on'));

    navBtn('fast').click();   // back where the scripted flow expects to be

    document.getElementById('toRound2Btn').click();
    chk('beat the board has a route', hash() === '#/feud/beat-the-board');
    chk('beat the board is the last step', nowStep() === 'Last word');
    chk('beat the board step names the timer', coach().indexOf('90-second') > -1);

    document.getElementById('finalScoreBtn').click();
    chk('the final step turns into a debrief', coach().toLowerCase().indexOf('debrief') > -1);
    chk('the final step points at the log', coach().toLowerCase().indexOf('session log') > -1);
    chk('the final step reads as finished',
        document.getElementById('coach').className.indexOf('done') > -1);

    document.getElementById('newMatchBtn').click();
    chk('a new match returns to the lineup route', hash() === '#/feud/lineup');
    chk('a new match resets the stepper', nowStep() === 'Draw');
    chk('a new match locks the match stops again',
        navBtn('board').disabled && navBtn('fast').disabled && navBtn('beat').disabled);
    chk('the lineup is the current stop again', navBtn('lineup').classList.contains('on'));

    // ---------------- deep links ----------------
    // a live-match screen with no match running must not be linkable
    location.hash = '#/feud/fast-money';
    setTimeout(function(){
      try {
        chk('a match screen with no match falls back to the lineup',
            fsPick.classList.contains('active'));
        chk('the fallback rewrites the url', hash() === '#/feud/lineup');

        // with a match actually running, the same link works
        document.getElementById('startMatchBtn').click();
        location.hash = '#/feud/fast-money';
        setTimeout(function(){
         try {
          chk('deep link into fast money works mid-match',
              fsFast.classList.contains('active'));

        location.hash = '#/pictionary/3';
        setTimeout(function(){
          try {
            chk('deep link into a pictionary screen works',
                getComputedStyle(pictionaryApp).display !== 'none' && current === 3);
            chk('deep linking a mode hides the other',
                getComputedStyle(feudApp).display === 'none');

            location.hash = '#/nonsense/42';
            setTimeout(function(){
              try {
                chk('an unknown route lands on the picker',
                    document.getElementById('modePicker').hidden === false);
                chk('an unknown route hides both games',
                    getComputedStyle(feudApp).display === 'none' &&
                    getComputedStyle(pictionaryApp).display === 'none');

                location.hash = '#/pictionary/99';
                setTimeout(function(){
                  try {
                    chk('an out-of-range screen falls back to the first', current === 0);
                  } catch(e){ log.push('FAIL threw late: ' + e.message); }
                  finish();
                }, 30);
              } catch(e){ log.push('FAIL threw: ' + e.message); finish(); }
            }, 30);
          } catch(e){ log.push('FAIL threw: ' + e.message); finish(); }
        }, 30);
         } catch(e){ log.push('FAIL threw: ' + e.message); finish(); }
        }, 30);
      } catch(e){ log.push('FAIL threw: ' + e.message); finish(); }
    }, 30);
  } catch(e){
    log.push('FAIL threw: ' + e.message);
    finish();
  }
"""

# ------------------------------------------------------------------ responsive
RESP = r"""
  var log = [];
  function chk(n,c){ log.push((c?'PASS ':'FAIL ')+n); }
  var W = document.documentElement.clientWidth;
  function overflow(where){
    var bad = [];
    document.querySelectorAll('.app:not([hidden]) *').forEach(function(e){
      if (e.scrollWidth > W + 1) bad.push(e.className || e.tagName);
    });
    chk(where + ' fits at ' + W + 'px' + (bad.length ? ' [' + bad.slice(0,3).join(',') + ']' : ''),
        bad.length === 0);
    chk(where + ' does not scroll the page sideways at ' + W + 'px',
        document.documentElement.scrollWidth <= W + 1);
  }
  try {
    log.push('INFO viewport=' + W);
    document.getElementById('modeFeud').click();

    var grid = document.querySelector('#feudApp .hostgrid');
    var sidebarOn = getComputedStyle(grid).display === 'grid';
    chk('sidebar layout engages only at desktop widths', sidebarOn === (W >= 920));
    if (sidebarOn) {
      var side = document.querySelector('#feudApp .hostside');
      chk('sidebar holds a readable column', side.offsetWidth >= 220 && side.offsetWidth <= 310);
      chk('the stage keeps most of the screen', side.offsetWidth < W / 2);
      chk('the timeline runs vertically in the sidebar',
          getComputedStyle(document.getElementById('stepper')).flexDirection === 'column');
    } else {
      chk('narrow screens keep the stacked-top layout',
          getComputedStyle(document.getElementById('stepper')).flexDirection === 'row');
    }
    overflow('lineup');
    document.querySelector('.swapbox').open = true;
    overflow('lineup+swap');

    document.getElementById('startMatchBtn').click();
    overflow('face-off');
    document.getElementById('fo1Btn').click();
    document.getElementById('playBtn').click();
    overflow('board in play');

    var gi = document.getElementById('guessInput');
    gi.value = 'a fairly long guess typed by a host in a hurry';
    document.getElementById('guessBtn').click();
    overflow('board after a guess');

    document.getElementById('abandonBtn').click();
    overflow('fast money');
    document.getElementById('toRound2Btn').click();
    overflow('beat the board');

    // the app bar and the coach line must survive a narrow viewport
    var bar = feudApp.querySelector('.appbar');
    chk('app bar stays on screen', bar.scrollWidth <= W + 1);
    chk('stepper scrolls rather than overflowing',
        document.getElementById('stepper').scrollWidth > 0);
    var coachBox = document.getElementById('coach');
    chk('coach line wraps instead of overflowing', coachBox.scrollWidth <= W + 1);

    document.querySelectorAll('[data-backmode]')[0].click();
    document.getElementById('modePictionary').click();
    overflow('pictionary opening');
    goTo(4);
    overflow('pictionary guessing screen');
  } catch(e){ log.push('FAIL threw: ' + e.message); }
  var o = document.createElement('pre'); o.id='SPA'; o.textContent = log.join(' | ');
  document.body.appendChild(o);
"""


def run(harness, tmp, size=None, budget=4000):
    src = (SITE / "index.html").read_text(encoding="utf-8")
    idx = src.rfind("})();\n</script>")
    (SITE / tmp).write_text(src[:idx] + harness + src[idx:], encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--disable-gpu",
           "--virtual-time-budget=%d" % budget, "--dump-dom"]
    if size:
        cmd.append("--window-size=%d,%d" % size)
    cmd.append("file:///C:/tmp-hoff/site/" + tmp)
    r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    (SITE / tmp).unlink()
    m = re.search(r'<pre id="SPA">(.*?)</pre>', r.stdout, re.S)
    return html.unescape(m.group(1)).split(" | ") if m else None


total = fails = 0
blocks = [("routing + next steps", HARNESS, "_spa.html", None)]
for w in (420, 760, 1100, 1600):
    blocks.append(("responsive @ %dpx window" % w, RESP, "_spa%d.html" % w, (w, 900)))

for label, harness, tmp, size in blocks:
    print("=== " + label + " ===")
    results = run(harness, tmp, size)
    if results is None:
        print("NO RESULT - page threw before the harness ran")
        sys.exit(1)
    for x in results:
        if x.startswith("INFO"):
            print("  --", x)
            continue
        print(("  " if x.startswith("PASS") else ">>"), x)
    f = len([x for x in results if x.startswith("FAIL")])
    total += len([x for x in results if not x.startswith("INFO")])
    fails += f
    print()

print(f"{total-fails}/{total} passed")
sys.exit(1 if fails else 0)
