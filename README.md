# Smartphone Data Analysis & Price Prediction

Exploratory and predictive analysis of a dataset of 15,000 smartphone listings, covering data acquisition, cleaning/treatment, grouping, and price prediction, with fully interactive HTML/Plotly charts and a combined insights dashboard.

**[`smartphones_insights.html`](smartphones_insights.html)** is the single, self-contained dashboard — open it directly in a browser (works fully offline, `plotly.js` is vendored locally in `plotly.min.js`).

## Data Acquisition

The raw dataset lives at [`smartphones.csv`](smartphones.csv) (15,000 rows × 25 columns). It is a **synthetically generated** catalog of smartphone specs — each row combines a brand, model, and spec sheet (screen size, price, RAM, storage, camera, battery, etc.) independently at random, so brand/chipset/GPU combinations don't necessarily reflect real-world products. It's used here as a realistic-shaped, freely reusable dataset for practicing a full analysis pipeline, not as a source of factual market data.

Steps to acquire and load it, in order:

1. **Obtain the file.** Place `smartphones.csv` at the repository root (already included in this repo).
2. **Verify the schema.** The pipeline expects these columns: `id, brand_name, model, screen_size, price, release_year, operating_system, battery_capacity, ram, storage, camera_mp, front_camera_mp, refresh_rate, weight, thickness, body_material, chipset, gpu, dual_sim, network_support, bluetooth_version, wifi_version, usb_type, fast_charging, fingerprint_sensor`.
3. **Load and validate.** [`data_cleaning.py`](data_cleaning.py) reads the raw CSV with `pandas.read_csv` and immediately runs it through the treatment pipeline described below — nothing downstream ever touches the raw file directly.
4. **Persist the validated copy.** The cleaned dataset is written to `smartphones_clean.csv`, and a JSON report of every change made is written to `outputs/kpis_cleaning.json`, so the acquisition step is auditable and reproducible.

## Data Treatment & Cleaning

Implemented in [`data_cleaning.py`](data_cleaning.py) and shared by both analysis scripts, so every chart and model is trained on the exact same validated dataset:

1. **Text normalization** — trims whitespace on every categorical/text column.
2. **Type validation** — coerces all numeric columns (`price`, `ram`, `storage`, `battery_capacity`, etc.) with `pandas.to_numeric`, turning any malformed value into a detectable `NaN`.
3. **Duplicate removal** — drops exact duplicate rows and duplicate `id`s.
4. **Range/sanity validation** — drops rows with physically impossible values (e.g. negative price, screen size outside 3–10", RAM outside 1–64 GB, release year outside 2000–2026).
5. **Missing value imputation** — defensive step: numeric gaps are filled with the column median, categorical gaps with the column mode.
6. **Outlier treatment** — flags and caps extreme `price` values using the IQR method (3× multiplier) so a handful of extreme values can't distort the regression trendlines.

Result on this dataset (see `outputs/kpis_cleaning.json`): **0 duplicates, 0 missing values, 0 invalid-range rows** — the source file was already well-formed — but **17 extreme price outliers were detected and capped**, and the dataset was still run through the full defensive pipeline so it holds up on a messier future version of the file.

## Grouping & Aggregation

Implemented in [`analise_smartphones.py`](analise_smartphones.py), producing three aggregated summary tables (via `pandas.groupby`), each exported as CSV and one rendered as an interactive table on the dashboard:

| Output | Grouped by | Metrics |
|---|---|---|
| `outputs/brand_summary.csv` | `brand_name` | model count, avg. price, avg. RAM, avg. battery, avg. camera, % 5G, % dual-SIM |
| `outputs/year_summary.csv` | `release_year` | model count, avg. price, avg. RAM, % 5G |
| `outputs/os_summary.csv` | `operating_system` | model count, avg. price, avg. RAM |

The brand-level summary is also rendered as an interactive Plotly table (`08_brand_summary_table`) in the dashboard.

## Predictive Modeling

Implemented in [`analise_preditiva.py`](analise_preditiva.py) with scikit-learn:

- **Linear Regression** on average price by release year, projected forward to 2032 with a confidence band.
- **Random Forest** and **Gradient Boosting** regressors trained on 19 features (specs + label-encoded categoricals) to predict `price`, evaluated with an 80/20 train/test split (MAE, R²).
- Feature importance ranking from the Random Forest model.
- Linear projections of average spec values (RAM, battery, camera, refresh rate, storage, 5G share) through 2032.

Actual results from this run:

- **Gradient Boosting** narrowly outperforms Random Forest (MAE ≈ R$ 17,102 vs. R$ 17,145; R² ≈ 0.47 for both) — a moderate fit.
- **`operating_system` (Apple/iOS vs. Android) is by far the strongest price predictor** (importance ≈ 0.62), reflecting the large price premium Apple devices carry in this dataset. RAM, camera and screen size matter comparatively little.
- Because brand/spec combinations were assigned independently at random, spec-to-price correlations besides the OS/brand premium are close to zero (e.g. price×RAM ≈ 0.01, price×camera ≈ 0.00) — a useful reminder that a model's R² is bounded by how much real signal exists in the data, not just by model choice.

## Interactive HTML Charts

All charts are built with Plotly and render fully client-side (hover, zoom, pan, legend filtering) — no server required.

| File | What it shows |
|---|---|
| `01_projecao_preco.html` | Historical average price by release year, linear trendline projected to 2032. |
| `02_importancia_features.html` | Feature importances from the Random Forest price model. |
| `03_real_vs_previsto.html` | Actual vs. predicted price (test set), Random Forest vs. Gradient Boosting. |
| `04_tendencias_specs.html` | Multi-panel projection of RAM, battery, camera, refresh rate, storage, 5G share to 2032. |
| `05_bubble_marcas.html` | Bubble chart: brand price vs. camera resolution, bubble size = model count. |

`outputs/fragments/*.html` holds the embeddable (non-standalone) version of every chart above plus the EDA charts (top brands, price by brand, OS share, price by year, RAM/storage distribution, correlation heatmap, grouped brand table) — these are what `gerar_dashboard.py` stitches into `smartphones_insights.html`.

Static Matplotlib/Seaborn equivalents (`graficos_visao_geral.png`, `correlacao.png`, `ram_storage.png`) are also generated for quick reference outside a browser.

## How to Run

```bash
python analise_smartphones.py
python analise_preditiva.py
python gerar_dashboard.py
```

Run in this order from the repository root. Each script is idempotent and safe to re-run.

## Tech Stack

`pandas` · `numpy` · `scikit-learn` · `plotly` · `matplotlib` · `seaborn`

## Repository Layout

```
smartphones.csv                 # raw source dataset
smartphones_clean.csv           # validated/cleaned dataset (generated)
data_cleaning.py                # data acquisition + treatment/cleaning pipeline
analise_smartphones.py          # EDA, grouping, static PNGs + interactive fragments
analise_preditiva.py            # predictive modeling (scikit-learn + Plotly)
gerar_dashboard.py              # assembles fragments + KPIs into the dashboard
smartphones_insights.html       # combined interactive insights dashboard (generated)
plotly.min.js                   # vendored Plotly.js (generated)
01..05_*.html                   # standalone interactive predictive charts (generated)
outputs/fragments/*.html        # embeddable chart fragments (generated)
outputs/kpis_*.json             # KPI values used by the dashboard (generated)
outputs/*_summary.csv           # grouped/aggregated tables (generated)
*.png                           # static EDA charts (generated)
```
