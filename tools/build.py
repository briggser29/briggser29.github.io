"""Rebuild index.html (Erik's Public Shelf) from a Shelf database export.

Usage: python3 tools/build.py <books_dir> [goal_for_this_year]
  books_dir: folder of <doc_id>.json files exported from the Shelf's "books" collection.
Private fields (notes, ISBN, ASIN) are never copied into the public page.
"""
import datetime, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KEEP = ["title", "author", "status", "progress", "rating", "finishedAt", "dnfAt", "startedAt",
        "genres", "runtimeMin", "owned", "source", "updatedAt", "favorite"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def main():
    books_dir = sys.argv[1]
    today = datetime.date.today()
    goals = {str(today.year): int(sys.argv[2])} if len(sys.argv) > 2 and sys.argv[2] else {}
    books = []
    for f in sorted(glob.glob(os.path.join(books_dir, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d = d.get("data", d)
        b = {k: d[k] for k in KEEP if k in d}
        b["id"] = os.path.basename(f)[:-5]
        books.append(b)
    if not books:
        sys.exit("No books found; refusing to publish an empty shelf.")
    stamp = f"{MONTHS[today.month - 1]} {today.day}, {today.year}"
    s = open(os.path.join(HERE, "shelf-template.html"), encoding="utf-8").read()
    s = s.replace("<title>Erik's Shelf</title>", "<title>Erik's Public Shelf</title>", 1)
    s = s.replace('<span class="viewonly"> · view only</span>', f'<span class="viewonly"> · updated {stamp}</span>', 1)
    start = s.index("(async () => {\n  render();")
    end = s.index("})();", start) + len("})();")
    snap = {"books": books, "goals": goals}
    boot = ("const SNAPSHOT = " + json.dumps(snap, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
            "visitor = true;\ndocument.body.classList.add(\"visitor\");\n"
            "books = SNAPSHOT.books;\ngoals = SNAPSHOT.goals;\nrender();")
    s = s[:start] + boot + s[end:]
    head_end = s.index("</style>") + len("</style>")
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           '<meta name="description" content="Erik\'s reading log: what I\'m reading, what I\'ve finished, and what\'s next.">\n'
           + s[:head_end] +
           '\n<style>html{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}</style>\n'
           '</head>\n<body>' + s[head_end:] + '\n</body>\n</html>\n')
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(doc)
    print(f"Built index.html: {len(books)} books, updated {stamp}")

if __name__ == "__main__":
    main()
