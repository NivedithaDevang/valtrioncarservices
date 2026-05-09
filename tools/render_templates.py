import os
import traceback
from pathlib import Path
import shutil

from app import create_app

app = create_app()

TEMPLATES_DIR = Path('app') / 'templates'
OUT_DIR = Path('public')
STATIC_SRC = Path('app') / 'static'
STATIC_DST = OUT_DIR / 'static'

OUT_DIR.mkdir(exist_ok=True)

with app.app_context():
    template_names = list(app.jinja_env.list_templates())

    for tmpl in template_names:
        if not tmpl.endswith('.html'):
            continue

        out_path = OUT_DIR / tmpl
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # some templates may use url_for or request, provide a test request context
            with app.test_request_context('/'):
                rendered = app.jinja_env.get_template(tmpl).render()
            out_path.write_text(rendered, encoding='utf-8')
            print(f"Rendered: {tmpl} -> {out_path}")
        except Exception as e:
            tb = traceback.format_exc()
            # try fallback: strip Jinja tags from source to produce a readable static page
            try:
                src_path = TEMPLATES_DIR / tmpl
                raw = src_path.read_text(encoding='utf-8')
                # naive removal of Jinja tags
                import re
                sanitized = re.sub(r"\{\%[\s\S]*?\%\}", "", raw)
                sanitized = re.sub(r"\{\{[\s\S]*?\}\}", "", sanitized)
                out_path.write_text(sanitized, encoding='utf-8')
                print(f"Fallback written for: {tmpl}")
            except Exception:
                placeholder = f"<html><body><h1>Rendering failed for {tmpl}</h1><pre>{tb}</pre></body></html>"
                out_path.write_text(placeholder, encoding='utf-8')
                print(f"Failed: {tmpl} (wrote error placeholder)")

# Copy static assets
if STATIC_SRC.exists():
    try:
        if STATIC_DST.exists():
            shutil.rmtree(STATIC_DST)
        shutil.copytree(STATIC_SRC, STATIC_DST)
        print(f"Copied static to {STATIC_DST}")
    except Exception as e:
        print(f"Failed to copy static: {e}")
else:
    print("No static folder found to copy")
