# Recipe Generator

Tell it what's in your kitchen and it writes you a recipe using those
ingredients — in the cuisine you pick, respecting the diet you pick.

Built on Google Gemini. Runs on your own machine.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## What it does

You give it a list of ingredients. It returns a single complete recipe with a
name, prep and cook times, a quantified ingredient list, numbered steps, and a
couple of tips on substitutions or storage.

Two things make the output more useful than a plain chat prompt:

- **It sticks to what you have.** Anything the recipe needs that you didn't
  list gets marked `(pantry)`, so you can see at a glance whether you need to
  go to the shop.
- **The structure is fixed.** A system instruction pins the format, so every
  recipe comes back in the same shape rather than a different layout each time.

The answer streams in as it's written, so you're reading the first steps while
the rest is still being generated.

---

## Setup

You need Python 3.10 or newer.

```bash
pip install -r requirements.txt
```

Get a free Gemini API key from
[aistudio.google.com/apikey](https://aistudio.google.com/apikey), then create a
file called `.env` in this folder:

```
GOOGLE_API_KEY=your-key-here
```

Copy `.env.example` to `.env` if you'd rather start from a template.

---

## Running it

### Web interface

```bash
streamlit run recipe_app.py
```

Opens at <http://localhost:8501>.

| Control | What it does |
|---|---|
| **Ingredients** | One per line, or comma separated — both work |
| **Cuisine** | 12 options, from West African to Japanese |
| **Diet** | Omnivorous, vegetarian, vegan, pescatarian, gluten-free, dairy-free, keto, halal |
| **Servings** | 1 to 12; quantities scale to match |
| **Extra requirements** | Free text — *"under 30 minutes"*, *"no oven"*, *"extra spicy"* |
| **Model** | Four Gemini models; `gemini-3.6-flash` is the default |

Every recipe can be downloaded as `.txt` (just the recipe) or `.json` (the
recipe plus the ingredients, cuisine, diet and model that produced it).
Recipes you generate stay listed under **Earlier this session** until you close
the tab.

### As a script

`recipe.py` is the same idea without the interface — edit the ingredients at
the bottom of the file and run it:

```bash
python recipe.py
```

It prints the recipe and writes `food_recipe.txt` and `food_recipe.json` to the
current folder.

---

## Choosing a model

All four are Gemini Flash models — fast and cheap enough for this on the free
tier.

| Model | Notes |
|---|---|
| `gemini-3.6-flash` | Default. Reliable, good quality |
| `gemini-3.7-flash` | Newer. Occasionally returns 503 when busy |
| `gemini-3.5-flash` | Older, still solid |
| `gemini-3.5-flash-lite` | Fastest and cheapest, slightly less detail |

If one is busy or rate limited, the app says so and suggests switching — it
won't fail with a stack trace.

---

## Customising it

Everything worth changing sits at the top of `recipe_app.py`:

| Constant | What it controls |
|---|---|
| `MODELS` | Which models appear in the dropdown |
| `CUISINES` | The cuisine list — add your own |
| `DIETS` | The diet list |
| `SYSTEM_INSTRUCTION` | The recipe format. Edit this to change the sections, the tone, or the level of detail |

`SYSTEM_INSTRUCTION` is the one with the biggest effect. It's plain English —
if you want metric measurements only, or a wine pairing at the end, say so
there.

---

## Notes

- **Your key stays local.** It's read from `.env` and used to call Google
  directly. Nothing is stored or sent anywhere else.
- **What is sent to Google:** your ingredient list and the options you picked.
  That's all.
- **Free tier limits.** Recipes are small requests, so you'd have to generate a
  lot of them in one minute to hit a limit. If you do, the app tells you to
  wait or switch model.
- **No database.** Session history lives in memory and disappears when you
  close the tab. Download anything you want to keep.

---

## Files

| File | Purpose |
|---|---|
| `recipe_app.py` | Streamlit interface with streaming, downloads and history |
| `recipe.py` | Minimal script version |
| `requirements.txt` | Dependencies |
| `.env.example` | Template for your API key |

---

## License

MIT — do what you like with it.
