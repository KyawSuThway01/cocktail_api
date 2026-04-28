# 🍹 Cocktail API

> A production-style cocktail API designed for real-world applications like bartender tools, mobile apps, and AI-powered drink assistants.

---

## Why I Built This

The bar and hospitality industry lacks modern, developer-friendly data infrastructure. Most cocktail apps rely on outdated databases or Wikipedia scrapes. This project simulates a real SaaS backend for the bar industry — serving rich, curated content including cocktail histories, food pairing science, step-by-step video tutorials, and zero-proof alternatives. Built to integrate with mobile apps, POS systems, and AI sommelier tools.

---

## Key Features

- 🍸 **10 curated cocktail histories** with origin stories and fun facts
- 🍽️ **25 food pairing systems** with match-level scoring (Perfect / Excellent / Good)
- 🎬 **38 cocktail video tutorials** across Classic, Whisky, Artisan, and more
- 🧃 **15 zero-proof mocktail recipes** for inclusive menu design
- 🔍 **Advanced filtering** by category, tag, difficulty, and flavour profile
- 🎲 **Randomized endpoints** for dynamic content delivery
- 🌐 **CORS enabled** — ready to connect to any frontend out of the box

---

## Demo

> API live response — `GET /api/history/negroni`

```json
{
  "name": "Negroni",
  "year": "1919",
  "origin": "Florence, Italy",
  "era": "Post-WWI",
  "summary": "The Negroni was born in Florence, Italy in 1919 when Count Camillo Negroni asked bartender Fosco Scarselli to strengthen his Americano by replacing soda water with gin...",
  "fun_fact": "The Negroni is one of the few cocktails named after a real person who actually invented it — most cocktail origin stories are disputed myths.",
  "image": "/static/cocktail_history/negroni.png"
}
```

> Food pairing response — `GET /api/pairing/wagyu_beef`

```json
{
  "name": "Wagyu Beef",
  "category": "Meat",
  "flavour_profile": ["Rich", "Buttery", "Umami", "Savoury"],
  "pairings": [
    {
      "cocktail": "Old Fashioned",
      "match_level": "Perfect",
      "reason": "Bourbon's caramel and vanilla notes mirror the beef's richness, while the bitters cut through the fat and cleanse the palate between bites."
    },
    {
      "cocktail": "Manhattan",
      "match_level": "Excellent",
      "reason": "Rye whisky's spice and sweet vermouth's herbal complexity complement wagyu's deep umami without overpowering it."
    }
  ]
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8+ |
| Framework | Flask |
| Server | Gunicorn |
| Data Format | JSON |
| Media Serving | Flask Static Files |
| Deployment | Render |

---

## Project Structure

```
cocktail_api/
├── app.py                        # Main Flask application
├── requirements.txt              # Python dependencies
└── static/
    ├── cocktail_history/         # Cocktail history images
    ├── cocktail_pairing_images/  # Food pairing cocktail images
    ├── food_pairing_videos/      # Food pairing video clips
    ├── garnish_videos/           # Garnish tutorial videos
    ├── mocktail_videos/          # Mocktail tutorial videos
    └── videos/                   # Main cocktail tutorial videos
```

---

## Getting Started

```bash
git clone https://github.com/KyawSuThway01/cocktail_api.git
cd cocktail_api
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:10000` by default.

---

## API Overview

All endpoints return JSON. CORS is enabled for all origins.

| Resource | Endpoints | Records |
|----------|-----------|---------|
| Cocktail History | `/api/histories`, `/api/history/<n>` | 10 cocktails |
| Food Pairings | `/api/pairings`, `/api/pairing/<n>` | 25 dishes |
| Cocktail Videos | `/api/videos`, `/api/video/<n>` | 38 videos |
| Mocktails | `/api/mocktails`, `/api/mocktail/<n>` | 15 drinks |
| Garnish Tutorials | `/api/garnish_tutorials`, `/api/garnish_tutorial/<n>` | 11 videos |
| Backgrounds | `/api/backgrounds`, `/api/background/<n>` | 9 scenes |

Every resource also supports:
- `GET /api/<resource>/random` — random entry
- `GET /api/<resource>/categories` — grouped by category
- Query filters: `?category=`, `?difficulty=`, `?tag=`, `?flavour=`

---

## Key Endpoints

### Cocktail History
```
GET /api/history/negroni
GET /api/history/old_fashioned
GET /api/histories/random
```
Available: `old_fashioned`, `martini`, `negroni`, `manhattan`, `mojito`, `daiquiri`, `margarita`, `singapore_sling`, `sazerac`, `mai_tai`

### Food Pairings
```
GET /api/pairing/wagyu_beef
GET /api/pairing/oysters
GET /api/pairings?category=Seafood
```
Each dish returns up to 3 cocktail recommendations with match levels: `Perfect`, `Excellent`, or `Good`.

### Cocktail Videos
```
GET /api/videos?difficulty=Easy
GET /api/videos?category=Classic
GET /api/video/smoked_old_fashioned
```

### Mocktails (Zero-Proof)
```
GET /api/mocktails?category=Tropical
GET /api/mocktail/virgin_mojito
GET /api/mocktails/random
```

---

## Deployment

Deployed on [Render](https://render.com) using Gunicorn. The app reads the `PORT` environment variable automatically.

```bash
gunicorn app:app
```

To point video URLs at a CDN, update `VIDEO_BASE_URL` in `app.py`:

```python
VIDEO_BASE_URL = "https://your-cdn.com/videos/"
```

---

## Roadmap

- [ ] PostgreSQL database integration
- [ ] User favourites and saved pairings
- [ ] Cocktail search by ingredient
- [ ] AI-powered drink recommendations
- [ ] Authentication and API key management

---

## License

Private project. All rights reserved by KyawSuThway01.
