from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
html = INDEX.read_text(encoding="utf-8")
marker = "/* UI5.1 desktop Practice rhythm */"
if marker in html:
    raise SystemExit("UI5.1 desktop Practice rhythm already applied")

css = r'''

  /* UI5.1 desktop Practice rhythm */
  @media(min-width:1000px) and (min-height:700px){
    .ui3-practice #quizContent{grid-template-rows:auto auto auto;align-content:start}
    .ui3-practice #quizContent>div:last-child{justify-content:flex-start;margin-top:clamp(30px,4vh,44px)}
  }
'''
if "\n</style>" not in html:
    raise SystemExit("Closing style tag missing")
html = html.replace("\n</style>", css + "\n</style>", 1)
INDEX.write_text(html, encoding="utf-8")
print("Applied UI5.1 desktop Practice rhythm")
