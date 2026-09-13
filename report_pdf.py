"""
INSPECTION DATA - Generation automatique du rapport d'inspection en PDF.
Rend le site (web/index.html) en PDF via un navigateur headless (Playwright).
Prerequis : pip install playwright  puis  python -m playwright install chromium
"""
import pathlib
from datetime import date

def build_pdf(out_path=None, dated=False):
    from playwright.sync_api import sync_playwright
    root = pathlib.Path(__file__).resolve().parent
    html = root / "web" / "index.html"
    if not (root / "web" / "findings.js").exists():
        print("findings.js manquant : lance d'abord  python run.py")
        return None

    out_dir = root / "reports"
    out_dir.mkdir(exist_ok=True)
    if out_path is None:
        name = f"rapport_inspection_{date.today().isoformat()}.pdf" if dated else "rapport_inspection.pdf"
        out_path = out_dir / name

    url = "file://" + str(html)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(900)           # laisse le JS construire le DOM et les polices se charger
        pg.emulate_media(media="screen")   # PDF fidele au site : theme sombre, couleurs
        pg.pdf(path=str(out_path), format="A4", print_background=True,
               margin={"top": "10mm", "bottom": "12mm", "left": "10mm", "right": "10mm"})
        b.close()
    print(f"Rapport PDF genere : {out_path}")
    return out_path

if __name__ == "__main__":
    build_pdf()
