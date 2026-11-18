# news-image-20261117 — The World in One Day

A make.fun entry for **news-image-20261117**: sum up the world's news of
Tuesday 17 November 2026 in one image.

The entry is a newspaper front page, drawn procedurally with PIL
(`build-image.py`), so every letter is crisp and every fact is one reported
that day:

- **Lead:** Ukraine hits the Kerch Bridge — a road span collapses into the
  strait; Zelenskyy calls the weeks-planned drone and missile attack
  "unprecedented".
- **Iran** hits a U.S. radar site in Bahrain for the third time in days;
  tankers hit mines near Hormuz.
- **Trump** opens his Asia trip with a Quad summit in Manila, then heads to
  Shenzhen for a three-way meeting with Xi and Putin.
- **Gaza:** Britain, Australia, Canada and Italy press Israel to open aid
  crossings as the U.N. warns of a winter emergency.
- **U.S.** loses its measles elimination status after 26 years.
- **Nvidia** posts bumper earnings days after Jensen Huang's exit.
- **Japan** scrambles fighter jets as Russian aircraft enter its airspace.
- **Also:** EU states plan a Rwanda return hub; a Russian military plane
  crash kills 19; Bitcoin stalls below $65,000; Britain sanctions eight
  settlement builders; COP31 talks reach a decisive stage.

Sources: Associated Press, Reuters, BBC, CNN.

## How it works

`main.ts` (Node 22, standard library only) copies `entry.png` to
`/output/entry.png`. Copying a fixed file is deterministic: two runs write
the same bytes. To rebuild the image from scratch:

```sh
python3 build-image.py   # writes entry.png (1024x1024, PNG)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## License

MIT — see `LICENSE`.
