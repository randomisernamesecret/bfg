# Custoda regional product catalogs

These five optional food packs each contain 3,000 popular named products tagged for the United States, United Kingdom, France, Germany or Spain. Products may appear in multiple packs. Coverage is a curated snapshot, not a complete national catalog.

Source: [Open Food Facts official bulk TSV export](https://world.openfoodfacts.org/data), retrieved 2026-10-05. Attribution: Open Food Facts contributors. No Yuka data, ratings, images or code is included.

Database: [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Individual contents: [Database Contents License 1.0](https://opendatacommons.org/licenses/dbcl/1-0/). Product images referenced in records, where available, are credited to Open Food Facts contributors under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/); image files are not included in these packs.

Changes: popular named products selected by `unique_scans_n` and country tags; fields trimmed to the app's product model; TSV nutrient-level tags converted to keyed levels; barcode identity and catalog provenance retained. Missing data remains missing. SHA-256, byte size and product counts are published in `manifest.json`; each SQLite file contains attribution and source metadata.

The downloadable SQLite files are the complete modified database snapshots offered under ODbL. Rebuild tool: `tools/build-product-db/build-regional-packs.py` in the Custoda source repository. User inventories, avoid lists, label text and personal photos are never included or sent to this host.
