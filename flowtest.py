import re, subprocess, sys, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = """
  // ---- full pictionary flow regression ----
  var log = [];
  function chk(name, cond){ log.push((cond ? 'PASS ' : 'FAIL ') + name); }
  try {
    chk('screen0 active', screens[0].classList.contains('active'));
    document.querySelector('[data-next]').click();
    chk('advanced to screen1', screens[1].classList.contains('active'));
    chk('banner is secret', banner.className.indexOf('secret') > -1);

    drawBtn.click();
    var opts = cardChoices.querySelectorAll('.choice');
    chk('dealt 5 choices', opts.length === 5);
    opts[1].click();
    chk('card chosen', !!currentCard && cardDisplay.textContent === currentCard.task);
    chk('banned chips shown', cardBanned.hidden === false &&
        cardBanned.querySelectorAll('.chip').length === currentCard.banned.length);
    chk('hide enabled', hideBtn.disabled === false);

    hideBtn.click();
    chk('on screen2', screens[2].classList.contains('active'));
    chk('banner still secret', banner.className.indexOf('secret') > -1);

    prepSkipBtn.click();
    chk('on screen3', screens[3].classList.contains('active'));
    chk('outputBox enabled', outputBox.disabled === false);

    promptBox.value = 'test prompt';
    outputBox.value = 'test output';
    outputBox.dispatchEvent(new Event('input'));
    chk('reveal enabled after typing', revealBtn.disabled === false);

    revealBtn.click();
    chk('on screen4', screens[4].classList.contains('active'));
    chk('banner now show', banner.className.indexOf('show') > -1);
    chk('output visible to B', outputCard.textContent === 'test output');

    guessSkipBtn.click();
    chk('on screen5', screens[5].classList.contains('active'));
    var boxes = document.querySelectorAll('#compare .box');
    chk('3 reveal boxes', boxes.length === 3);

    document.getElementById('gotItBtn').click();
    chk('score chip shows 1/1', scoreChip.textContent.indexOf('1') > -1 && !scoreChip.hidden);
    chk('playAgain visible', scoreResult.hidden === false);

    document.getElementById('playAgainBtn').click();
    chk('looped to screen1', screens[1].classList.contains('active'));
    chk('card cleared', currentCard === null);
    chk('prompt cleared', promptBox.value === '');
  } catch (e) {
    log.push('FAIL threw: ' + e.message);
  }
  var out = document.createElement('pre');
  out.id = 'FLOW';
  out.textContent = log.join(' | ');
  document.body.appendChild(out);
"""

src = (SITE / "index.html").read_text(encoding="utf-8")
assert "})();\n</script>" in src, "script anchor missing"
test = src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1)
(SITE / "_flowtest.html").write_text(test, encoding="utf-8")

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=4000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_flowtest.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="FLOW">(.*?)</pre>', r.stdout, re.S)
if not m:
    print("NO RESULT — page threw before the harness ran"); sys.exit(1)
results = html.unescape(m.group(1)).split(" | ")
fails = [x for x in results if x.startswith("FAIL")]
for x in results: print(("  " if x.startswith("PASS") else ">>") , x)
print()
print(f"{len(results)-len(fails)}/{len(results)} passed")
(SITE / "_flowtest.html").unlink()
sys.exit(1 if fails else 0)
