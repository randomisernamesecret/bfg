#!/usr/bin/env python3
"""Single source of truth for the live app catalogue.

Used by build_llms.py (llms.txt, llms-full.txt and apps.json) so the three cannot
drift. Store names, ids and categories come from the App Store Connect listing
data pulled on 2026-11-10 (live_listings.json); devices and the purchase model
come from app_facts.py (the same text as the "At a glance" box on each page).
Re-check store names against the store whenever an app is renamed.

Only live apps are listed. Coming-soon games are in COMING_SOON.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app_facts  # noqa: E402

SITE = "https://bfgapps.co"
SITE_LANGS = ["en", "de", "es", "fr", "ja", "zh-Hans"]

# slug: (store name, short name, category, summary, who it is for, privacy position)
APP_TEXT = {
    "kanesh": ("Tickview: SEC Filings & Alerts", "Tickview", "Finance",
               "Sourced alerts for your watchlist and the economy: new SEC filings, insider purchases, price crossings and Recession Watch (a model probability shown with its track record), plus the bond market and plain-English questions answered with sourced cards. Not investment advice.",
               "Individual investors who want sourced information on iPhone and iPad rather than tips.",
               "No account, no ads. All AI runs on the device; the app fetches only public market data."),
    "cognithix": ("11 Plus Exam Prep: Cognithix", "Cognithix", "Education",
                  "11+ practice for ages 9 to 11: English, verbal reasoning, non-verbal reasoning and language aptitude (no maths), with daily plans, timed mock papers and parent progress insights.",
                  "Parents preparing a child for the 11+ for grammar and independent schools in England.",
                  "No account; data stays on the device."),
    "arithmetix": ("Arithmetix - Times Tables SATs", "Arithmetix", "Education",
                   "UK National Curriculum maths from Reception to Year 6 with spaced repetition, times tables practice for the Year 4 multiplication check, and virtual pet motivation.",
                   "UK primary school children and their parents.",
                   "No account; progress stays on the device."),
    "sparks-studios": ("Doodlebee: Coloring & Drawing", "Doodlebee", "Games",
                       "Drawing and coloring app for kids and grown-ups: draw any shape, tap to fill it and watch it dance, with pages to color by hand or by number, storybooks read aloud and music.",
                       "Children and families who want a calm, safe creative app.",
                       "No ads, no accounts; nothing leaves the device."),
    "photoflight": ("PhotoFlight: Travel Photo Map", "PhotoFlight", "Travel",
                    "Travel map built from the location data already in your photos: countries, cities, flights and achievements, with no live tracking needed. Includes PhotoGuessr, a family game where everyone secretly pins where one of your photos was taken.",
                    "Travellers who want a map of past trips from the photos they already have.",
                    "No account; your travel history stays on the device."),
    "cyla": ("Ondi: Private Period Tracker", "Ondi", "Health & Fitness",
             "Private period and cycle tracker with Apple Watch temperature support.",
             "People who want to track their cycle without an account or a cloud.",
             "No accounts, no cloud, no servers; data stays on the device."),
    "cloudmesh": ("Cloudmesh: Rain Alerts & Radar", "Cloudmesh", "Weather",
                  "Hyperlocal weather: minute-by-minute rain alerts, live radar, a forecast blended from many sources, air quality and 24 widgets.",
                  "Anyone who wants accurate rain timing and a weather app without a subscription.",
                  "No account; approximate location is used for forecasts and rain alerts."),
    "pacegrid": ("PaceGrid: GPS Running Tracker", "PaceGrid", "Health & Fitness",
                 "GPS run, ride, walk and hike tracker with Injury Guard training-load alerts, smart ring sleep data and GPX/FIT export.",
                 "Runners, cyclists and hikers who want to keep their training data without a subscription.",
                 "No account; workouts stay on the device."),
    "minua": ("Minua: Earn Screen Time", "Minua", "Productivity",
              "Screen time you earn, for your child or for yourself: time in the apps you want more of unlocks the apps you want less of. Parent PIN mode for a child's device, Myself mode for adults.",
              "Parents setting screen-time rules, and adults breaking their own scroll habit.",
              "Fully on the device, no accounts."),
    "bellgrave": ("Bellgrave — 3D Roguelike RPG", "Bellgrave", "Games",
                  "Dark 3D roguelike horde-survivor: draft an arsenal of up to four weapons, evolve them from boss treasure, dodge telegraphed attacks, face multi-phase bosses across cursed realms. Touch or game controller.",
                  "Action and roguelike fans who want a premium game with no ads or timers.",
                  "No ads, no account; progress stays on the device."),
    "cardbash": ("Card Bash: Roguelike Deck RPG", "Card Bash", "Games",
                 "Roguelike deck RPG with 200+ neon creature cards, tactical turn-based fights, a booster to open every 24 hours, daily quests, duels with a friend nearby over Wi-Fi or Bluetooth and trades through Messages.",
                 "Card-battler and roguelike players on iPhone and iPad.",
                 "No ads; game progress stays on the device."),
    "mergebash": ("Merge Bash: Idle Monster Game", "Merge Bash", "Games",
                  "Idle merge-to-evolve creature collector: merge Beasts from Common to Mythic, haggle with league patrons, send expeditions, climb nine leagues and face the Tide League's champion in Champion Clash. Idle earnings while you are away.",
                  "Players who like idle and merge games.",
                  "No ads; progress stays on the device."),
    "penlicence": ("Inkla: Handwriting Practice", "Inkla", "Education",
                   "Handwriting practice for kids in 8 languages (English, French, German, Spanish, Romanian, Japanese hiragana, Chinese, Hindi): letter formation with feedback after every attempt, print and cursive, Word Explorer and Meaning Quiz.",
                   "Children learning to write and the adults teaching them.",
                   "On the device, no accounts."),
    "keystrike": ("Keystrike: Piano Sight Reading", "Keystrike", "Education",
                  "Piano lessons: graded course from Grade 0 to Grade 8, sight-reading, ear training, built-in pieces as engraved sheet music or falling notes, MIDI keyboard or on-screen piano, MIDI import.",
                  "Beginners, returning players and self-taught learners who want a structured path.",
                  "No account, no ads, no tracking; progress and recordings stay on the device."),
    "custoda": ("Custoda: Expiry Tracker", "Custoda", "Food & Drink",
                "Pantry, expiry and allergen tracker: scan to track expiry dates, allergen and diet warnings that say \"unverified\" when data is missing, recipes ranked by what you have, a household shopping list and dinner vote via private iCloud invitations, replace-by dates for smoke alarms and first-aid kits.",
                "Households that want to waste less food and stay safe with allergens.",
                "No account; data stays on the device, and barcode lookups send only the barcode number."),
    "farewars": ("Fare Wars", "Fare Wars", "Games",
                 "Arcade bus racing through Rivergate: race rival buses for every fare, boss races, a garage of restored buses and a paint shop.",
                 "Arcade racing fans on iPhone and iPad.",
                 "No ads; progress stays on the device."),
    "robotrooftoprun": ("Zoombot: Robot Running Game", "Zoombot", "Games",
                        "Jetpack runner across a city of rooftops: outrun patrols, beat bosses, rescue your crew and build your own robot in the Workshop.",
                        "Endless-runner fans on iPhone and iPad.",
                        "No ads; progress stays on the device."),
}

# Homepage order of the live apps.
ORDER = ["kanesh", "cognithix", "arithmetix", "sparks-studios", "photoflight", "cyla", "cloudmesh", "pacegrid",
         "minua", "bellgrave", "cardbash", "mergebash", "penlicence", "keystrike", "custoda", "farewars",
         "robotrooftoprun"]

COMING_SOON = [
    ("Nitro Metro", "nitrometro",
     "Arcade street racing across ten world cities with police chases, power-ups and cars to build; race friends nearby or online. Touch or game controller. Coming soon to iPhone and iPad."),
    ("Hollowstead", "hollowstead",
     "A farming and survival game with a story, in development. Coming soon to iPhone and iPad."),
]

OS_NAMES = {"iPhone": "iOS", "iPad": "iPadOS", "Mac": "macOS", "Apple Watch": "watchOS"}
SCHEMA_CATEGORY = {"kanesh": "FinanceApplication", "cognithix": "EducationalApplication",
                   "arithmetix": "EducationalApplication", "sparks-studios": "GameApplication"}


def store_url(app_id):
    return f"https://apps.apple.com/app/id{app_id}"


def operating_system(slug):
    return ", ".join(OS_NAMES[d] for d in app_facts.APPS[slug][3])


def catalogue():
    out = []
    for slug in ORDER:
        sid, price_key, _data, devices = app_facts.APPS[slug]
        name, short, cat, summary, audience, privacy = APP_TEXT[slug]
        langs = [l for l, d in (("en", ""), ("de", "de/"), ("es", "es/"), ("fr", "fr/"), ("ja", "ja/"), ("zh-Hans", "zh-CN/"))
                 if os.path.exists(os.path.join(app_facts.ROOT, d, "apps", slug, "index.html"))]
        out.append({
            "name": name, "shortName": short, "slug": slug, "appStoreId": sid,
            "url": f"{SITE}/apps/{slug}/", "appStoreUrl": store_url(sid),
            "category": cat, "platforms": devices, "summary": summary, "audience": audience,
            "priceModel": app_facts.PRICE[price_key][0], "privacy": privacy,
            "account": "Not needed", "ads": "None",
            "privacyUrl": f"{SITE}/apps/{slug}/privacy.html",
            "supportUrl": f"{SITE}/apps/{slug}/support.html",
            "termsUrl": f"{SITE}/apps/{slug}/terms.html",
            "pageLanguages": langs,
        })
    return out
