# Slides

HTML decks for recording, built from the scripts in `../scripts/`.

## Ep 00: Four Careers, One Project

File: `ep00-four-careers-one-project.html`

Open the file in a browser, or run a local server from the repo root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/slides/ep00-four-careers-one-project.html`.

### Presenting

- Arrow keys, Space, or swipe to move between slides.
- Press `N` to toggle speaker cues at the bottom of each slide.
- 16:9 deck, paper background, large text for screen recording.

### Brand: Plein Air

The deck follows `~/branding/README.md` and the Plein Air rules:

- Paper, never white. Violet ink, never black.
- Broken colour: three low-opacity washes plus blurred dabs, no flat field larger than a card.
- Soft edges, 14 percent ink borders, radii 8 to 26 px, violet shadows at 10 to 30 percent.
- Serif speaks, sans works, mono counts: Fraunces for titles, Karla for body, Spline Sans Mono for times, refs and numbers.
- Grain layer at 50 percent above the page, below the content.
- One complement dab per screen, under 8 percent of area.

Default palette is Riverbank Mist, selected for Ep 00. Fonts stay Fraunces for display, Karla for text and Spline Sans Mono for numbers. The other 12 palettes remain in the switcher and in `slides/palettes.html`.

Use the switcher at the bottom left to test palettes and the Day and Night modes. URL parameters `?p=<palette>&mode=day|night` are kept in sync, so you can link a specific palette, for example `?p=waterlilies&mode=day`. Open `slides/palettes.html` for a decision sheet with all 13 palettes side by side.

The deck ships 13 palettes. The first 7 are the original Plein Air sets from `~/branding`. The 6 new ones (Renoir Umbrellas, Morisot Garden, Cassatt Boating, Haystacks Dawn, Riverbank Mist, Garden Hour) were built with the same `tokens/build.py` rules and pass the 4.5:1 contrast gate.

Fonts are copied locally in `slides/fonts/` from `~/branding/assets/fonts/` and referenced with `@font-face`. Tokens live in `slides/tokens.css`, copied from `~/branding/preview/tokens.css`.

### Coverage

The deck follows `scripts/ep00-four-careers-one-project.md` segment by segment: Hook (00:00), Four Roles (00:40), Tour of the App (02:00), Act 1 (04:30), Act 2 (06:00), Act 3 (07:30), Act 4 (09:00), How the Course Works (10:00), What You Need (11:30), CV Skills Ledger (13:30), Outro.

It is a visual aid, not the full script. Key points and visuals are on screen. Your talking points stay in the script.

## Adding the next episode

Copy `ep00-four-careers-one-project.html` to `ep01-<slug>.html` and rebuild the slides from that episode script using the same template. Keep the time label, the act badge, the progress bar and the `N` notes toggle so every deck behaves the same when you record. Keep the Plein Air surfaces. Do not reintroduce dark, neon or technical themes.
