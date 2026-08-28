from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
html = INDEX.read_text(encoding="utf-8")

marker = "/* UI5 mobile vocabulary list finish */"
if marker in html:
    raise SystemExit("UI5 mobile vocabulary finish already applied")

css = r'''

  /* UI5 mobile vocabulary list finish */
  @media(max-width:430px){
    .library-table{table-layout:fixed;width:100%;min-width:0}
    .library-table th:nth-child(n+3),.library-table td:nth-child(n+3){display:none!important}
    .library-table th:nth-child(1),.library-table td:nth-child(1){width:58px;padding-left:12px;padding-right:8px}
    .library-table th:nth-child(2),.library-table td:nth-child(2){width:auto;padding-left:8px;padding-right:12px}
    .library-table .word-open-btn{display:block;width:100%;white-space:normal;overflow-wrap:anywhere}
    .library-table .word-subline{display:block;max-width:none;white-space:normal;overflow:visible;text-overflow:clip;line-height:1.35}
  }
'''
if "\n</style>" not in html:
    raise SystemExit("Closing style tag missing")
html = html.replace("\n</style>", css + "\n</style>", 1)
INDEX.write_text(html, encoding="utf-8")
print("Applied UI5 mobile vocabulary list finish with noun-button coverage across content and surface suites")
