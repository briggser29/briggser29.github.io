# Erik's Book Shelf

The public, read-only version of my reading log, live at https://briggser29.github.io.

`index.html` is generated. To rebuild it from a Shelf database export:

```
python3 tools/build.py <folder of book .json files> [yearly goal]
```

`tools/shelf-template.html` is the Shelf app itself; the build embeds a snapshot of the books into it and switches it to view-only. Notes, saved quotes and Audible IDs are left out of the public page. Covers load from Audible and Open Library on the public page only.

## Meal Prep Picker (`/meals`)

Live at https://briggser29.github.io/meals. Recipe text and photos are published only as encrypted files (`meals/data.bin`, `meals/photos/*.bin`); the passcode unlocks them in the browser. Household picks, shopping checkmarks, notes and ratings sync through Supabase (`meals/tools/supabase-setup.sql`).

To rebuild after changing the source page:

```
python3 meals/tools/build_meals.py <source page .html> <photos dir> meals <passcode> --supabase-url <url> --supabase-key <anon key>
```
