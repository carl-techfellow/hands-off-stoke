import re, subprocess, html, pathlib

SITE = pathlib.Path(r"C:/tmp-hoff/site")
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

# things a team would actually shout, and the answer it should land on
CASES = [
    ("Cover letter",   "i hope to express interest",        "I am writing to express my interest in"),
    ("Cover letter",   "excited",                            "I am excited to apply for"),
    ("Cover letter",   "i saw your posting",                 "I came across your job posting"),
    ("Resume bullet",  "spearheading",                       "Spearheaded"),
    ("Resume bullet",  "cross-functional!",                  "Collaborated with cross-functional teams"),
    ("Status update",  "circle back",                         "Circling back"),
    ("Status update",  "im blocked",                          "Currently blocked on"),
    ("Commit message", "readme",                              "Update README"),
    ("Commit message", "bug fixes",                           "Fix bug"),
    ("Test cases",     "wrong password",                      "Invalid password"),
    ("Test cases",     "they leave it blank",                 "Empty fields"),
    ("Test cases",     "forgot my password",                  "Password reset"),
    ("User story",     "as a user i want",                    "As a user, I want"),
    ("Slide titles",   "takeaways",                           "Key Takeaways"),
    ("Slide titles",   "thanks!",                             "Thank You"),
    ("App ideas",      "a todo app",                          "To-do list"),
    ("App ideas",      "tracking your expenses",              "Budget tracker"),
    ("Hedging",        "it just depends",                     "It depends"),
    ("Hedging",        "as a language model",                 "As an AI"),
    ("Sign-offs",      "hope that helps",                     "I hope this helps"),
    ("Sign-offs",      "dont hesitate to reach out",          "Feel free to reach out"),
    ("Formatting",     "bullets",                             "Bullet points"),
    ("Formatting",     "those long dashes",                   "Em dashes"),
    # these should NOT match anything
    ("Cover letter",   "my dog ate the homework",             None),
    ("Formatting",     "purple zebra kettle",                 None),
]

js_cases = ",\n    ".join(
    '{t:%s, g:%s, w:%s}' % (
        repr(t).replace("'", '"'), repr(g).replace("'", '"'),
        "null" if w is None else repr(w).replace("'", '"'))
    for t, g, w in CASES)

HARNESS = r"""
  var CASES = [
    %s
  ];
  var out = [], fails = 0;
  CASES.forEach(function(c){
    for (var i = 0; i < BOARDS.length; i++) if (BOARDS[i].tag === c.t) currentBoard = BOARDS[i];
    var m = matchGuess(c.g);
    var got = (m === -1) ? null : currentBoard.answers[m].text;
    var ok = (got === c.w);
    if (!ok) fails++;
    out.push((ok ? 'ok   ' : 'FAIL ') + c.t + ' :: "' + c.g + '" -> ' + (got || 'NO MATCH'));
  });
  var o = document.createElement('pre'); o.id = 'OV';
  o.textContent = out.join('\n') + '\n\n' + (CASES.length - fails) + '/' + CASES.length + ' realistic guesses judged correctly';
  document.body.appendChild(o);
""" % js_cases

src = (SITE / "index.html").read_text(encoding="utf-8")
(SITE / "_gd.html").write_text(src.replace("})();\n</script>", HARNESS + "})();\n</script>", 1),
                               encoding="utf-8")
r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--virtual-time-budget=3000", "--dump-dom",
                    "file:///C:/tmp-hoff/site/_gd.html"],
                   capture_output=True, text=True, errors="ignore")
m = re.search(r'<pre id="OV">(.*?)</pre>', r.stdout, re.S)
print(html.unescape(m.group(1)) if m else "NO RESULT")
(SITE / "_gd.html").unlink()
