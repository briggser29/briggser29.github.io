# Erik's Public Shelf

The public, read-only version of my reading log, live at https://briggser29.github.io.

`index.html` is generated. To rebuild it from a Shelf database export:

```
python3 tools/build.py <folder of book .json files> [yearly goal]
```

`tools/shelf-template.html` is the Shelf app itself; the build embeds a snapshot of the books into it and switches it to view-only. Notes, saved quotes and Audible IDs are left out of the public page. Covers load from Audible and Open Library on the public page only.
