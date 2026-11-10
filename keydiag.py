import re, subprocess, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

HARNESS = r"""
  var bad = [];
  BOARDS.forEach(function(b){
    currentBoard = b;
    b.answers.forEach(function(a, ai){
      a.keys.forEach(function(k){
        var m = matchGuess(k);
        if (m !== ai) {
          bad.push(b.tag + ' :: "' + k + '" -> ' +
                   (m === -1 ? 'NO MATCH' : b.answers[m].text) + '  (wanted: ' + a.text + ')');
        }
      });
    });
  });
  var o = document.createElement('pre'); o.id = 'OV';
  o.textContent = 'misroutes=' + bad.length + '\n' + bad.join('\n');
  document.body.appendChild(o);
"""

src = (SITE / "index.html").read_text(encoding="utf-8")
(SITE / "_kd.html").write_text(src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1),
                               encoding="utf-8")
r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=3000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_kd.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="OV">(.*?)</pre>', r.stdout, re.S)
print(html.unescape(m.group(1)) if m else "NO RESULT")
(SITE / "_kd.html").unlink()
