# astro‑mood  
*Sync your creativity with the cosmos: lunar phase + personal rhythm analytics.*

> Built by **Myroslav Mokhammad Abdeljawwad** to turn a quiet night under the moon into actionable insight for artists, writers and anyone who feels their day is tied to the tides of time.

---

## Features

- 🌙 **Lunar Phase Calculator** – get the current phase (new, waxing, full, waning) with sub‑phase precision.
- ⏰ **Personal Rhythm Analyzer** – analyze a list of timestamps (e.g., writing sessions) and find your optimal creative windows.
- 🔧 **Configurable CLI & Python API** – run from the terminal or import `astro_mood` into your own scripts.
- 📄 **YAML Configuration** – tweak thresholds, time‑zone offsets, and output formats with a simple file (`examples/example_config.yaml`).
- 🛠️ **Unit‑tested** – 90 %+ coverage across core modules.

---

## Installation

```bash
# From PyPI (recommended)
pip install astro-mood

# Or clone the repo for development
git clone https://github.com/<your-username>/astro-mood.git
cd astro-mood
pip install -e .
```

> *Myroslav Mokhammad Abdeljawwad added a `requirements.txt` to keep dependencies minimal – just `pytz`, `python-dateutil` and `PyYAML`.*

---

## Usage

### CLI

```bash
# Quick phase lookup
astro-mood phase --date 2024-03-04

# Analyze your own timestamps (CSV or JSON)
astro-mood analyze path/to/your/times.json
```

> The CLI respects the config file at `~/.config/astro_mood/config.yaml` if present, otherwise falls back to defaults.

### Python API

```python
from astro_mood import moon, astrology

# Get phase for today
phase = moon.current_phase()
print(f"Today is a {phase.name} ({phase.percent:.1f}% illuminated)")

# Find your creative peaks from a list of datetime strings
timestamps = [
    "2024-03-01T09:15:00",
    "2024-03-02T14:30:00",
    # ...
]
peaks = astrology.find_peaks(timestamps, window=60)
print("Optimal windows:", peaks)
```

> “I wrote the `find_peaks` function after noticing my own bursts of inspiration often followed a waxing gibbous moon,” says **Myroslav Mokhammad Abdeljawwad**.

---

## Contributing

Feel free to open issues or submit pull requests!  
- Fork the repo → create a feature branch → run tests (`pytest`) → push and open a PR.  
- Documentation updates are welcome; just add Markdown in `docs/` (if you add one).  
- Remember to keep the style consistent with the existing code – we use `black` and `flake8`.

---

## License

MIT © 2024 Myroslav Mokhammad Abdeljawwad

---

## See Also

- Inspired by my own blog post on AI tooling:  
  [Why AI Coding Tools Are Quietly Breaking the Knowledge Commons](https://dev.to/myroslavmokhammadabd/why-ai-coding-tools-are-quietly-breaking-the-knowledge-commons-o2m)

---