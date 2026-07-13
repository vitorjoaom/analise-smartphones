"""
Smartphones Dataset — Dashboard Builder
========================================
Assembles the KPI json files + Plotly chart fragments produced by
analise_smartphones.py and analise_preditiva.py into a single
self-contained, interactive HTML dashboard.
Run analise_smartphones.py and analise_preditiva.py first.
"""

import json
import os
import shutil

import plotly

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(PROJECT_PATH, "outputs")
FRAG_PATH = os.path.join(OUT_PATH, "fragments")
DASHBOARD_PATH = os.path.join(PROJECT_PATH, "smartphones_insights.html")

# Vendor plotly.js locally so the dashboard works fully offline, with no
# dependency on an external CDN (more reliable for a portfolio artifact).
PLOTLY_JS_SRC = os.path.join(os.path.dirname(plotly.__file__), "package_data", "plotly.min.js")
PLOTLY_JS_DEST = os.path.join(PROJECT_PATH, "plotly.min.js")
shutil.copyfile(PLOTLY_JS_SRC, PLOTLY_JS_DEST)
print(f"Vendored plotly.js -> {PLOTLY_JS_DEST}")


def load_json(name):
    with open(os.path.join(OUT_PATH, name), encoding="utf-8") as f:
        return json.load(f)


def load_fragment(name):
    with open(os.path.join(FRAG_PATH, f"{name}.html"), encoding="utf-8") as f:
        return f.read()


print("Loading KPIs and chart fragments...")
kpis = {**load_json("kpis_eda.json"), **load_json("kpis_predictive.json")}

kpi_cards = [
    ("📱", f"{kpis['total_smartphones']:,}", "Smartphones analyzed"),
    ("🏷️", f"{kpis['n_brands']}", "Brands represented"),
    ("👑", kpis["top_brand"], "Most common brand"),
    ("💎", kpis["priciest_brand"], "Priciest brand on average"),
    ("💰", f"R$ {kpis['avg_price']:,.0f}", "Average price"),
    ("📶", f"{kpis['pct_5g']}%", "Devices with 5G"),
    ("👆", f"{kpis['pct_fingerprint']}%", "With fingerprint sensor"),
    ("🔢", f"{kpis['pct_dual_sim']}%", "With dual SIM"),
    ("🤖", kpis["best_model"], "Best price prediction model"),
    ("📉", f"R$ {kpis['rf_mae']:,.0f}", "Price prediction MAE"),
    ("📈", f"R$ {kpis['price_2032']:,.0f}", "Projected avg. price (2032)"),
    ("🧠", f"{kpis['ram_2032']:.1f} GB", "Projected avg. RAM (2032)"),
]

sections = [
    ("01_top_brands", "Top Brands", "The 10 brands with the most smartphone models in the dataset."),
    ("03_os_share", "Operating System Share", "Market split between Android, iOS and other operating systems."),
    ("04_price_by_year", "Average Price by Release Year", "How the average smartphone price has evolved historically."),
    ("02_price_by_brand", "Price Distribution by Brand", "Price spread for the 6 most common brands, showing median, quartiles and outliers."),
    ("05_ram_distribution", "RAM Distribution", "How many devices ship with each RAM tier."),
    ("06_storage_distribution", "Storage Distribution", "How many devices ship with each internal storage tier."),
    ("07_correlation_heatmap", "Variable Correlations", "How price, battery, RAM, storage, camera and other specs relate to one another."),
    ("08_projecao_preco", "Price Projection to 2032", "Historical average price fitted with a Linear Regression trendline, projected forward to 2032 with a confidence band."),
    ("09_importancia_features", "Price Model — Feature Importance", "Which specs drive price the most, according to the Random Forest regressor."),
    ("10_real_vs_previsto", "Price Model — Actual vs. Predicted", "Actual vs. predicted price on a held-out test set, comparing Random Forest and Gradient Boosting."),
    ("11_tendencias_specs", "Spec Trends to 2032", "Projected evolution of RAM, battery, camera, refresh rate, storage and 5G adoption through 2032."),
    ("12_bubble_marcas", "Brands: Price vs. Camera vs. Volume", "Top 15 brands positioned by average price and average camera resolution, bubble size = number of models."),
]

kpi_html = "\n".join(
    f"""      <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
      </div>"""
    for icon, value, label in kpi_cards
)

section_html = "\n".join(
    f"""    <section class="chart-section">
      <h2>{title}</h2>
      <p class="chart-desc">{desc}</p>
      <div class="chart-box">{load_fragment(frag)}</div>
    </section>"""
    for frag, title, desc in sections
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smartphones Dataset — Insights Dashboard</title>
<script src="plotly.min.js"></script>
<style>
  :root {{
    --mint: #7FAE95;
    --rose: #D98A99;
    --bg: #211F1C;
    --panel: #2A2723;
    --panel-alt: #302C27;
    --grid: #433E37;
    --text: #F5F1EA;
    --muted: #B0A89D;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: "Helvetica Neue", "Segoe UI", Arial, sans-serif;
  }}
  header {{
    padding: 40px 6vw 24px;
    background: linear-gradient(180deg, rgba(127,174,149,0.18), transparent);
    border-bottom: 1px solid var(--grid);
  }}
  header h1 {{
    margin: 0;
    font-size: 2.4rem;
    letter-spacing: -0.5px;
  }}
  header h1 span {{ color: var(--mint); }}
  header p {{
    color: var(--muted);
    max-width: 760px;
    margin-top: 10px;
  }}
  main {{ padding: 10px 6vw 60px; }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
    margin: 24px 0 48px;
  }}
  .kpi-card {{
    background: var(--panel);
    border: 1px solid var(--grid);
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}
  .kpi-card:hover {{
    transform: translateY(-4px);
    border-color: var(--mint);
  }}
  .kpi-icon {{ font-size: 1.6rem; }}
  .kpi-value {{
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--rose);
    margin: 6px 0 2px;
  }}
  .kpi-label {{
    font-size: 0.8rem;
    color: var(--muted);
  }}
  .chart-section {{
    background: var(--panel-alt);
    border: 1px solid var(--grid);
    border-radius: 14px;
    padding: 24px 24px 8px;
    margin-bottom: 28px;
  }}
  .chart-section h2 {{
    margin: 0 0 4px;
    font-size: 1.3rem;
  }}
  .chart-desc {{
    color: var(--muted);
    margin: 0 0 12px;
    font-size: 0.9rem;
  }}
  .chart-box {{ width: 100%; }}
  .chart-box .plotly-graph-div {{ width: 100% !important; }}
  footer {{
    text-align: center;
    color: var(--muted);
    padding: 30px;
    font-size: 0.85rem;
    border-top: 1px solid var(--grid);
  }}
</style>
</head>
<body>
  <header>
    <h1><span>SMARTPHONES</span> Dataset — Insights Dashboard</h1>
    <p>Exploratory analysis with pandas and NumPy, and predictive models with
    scikit-learn (Linear Regression, Random Forest and Gradient Boosting) over
    15,000 smartphone listings. Every chart below is interactive: hover, zoom,
    or click a legend entry to filter series.</p>
  </header>
  <main>
    <div class="kpi-grid">
{kpi_html}
    </div>
{section_html}
  </main>
  <footer>Smartphones Dataset · Pipeline: pandas -&gt; numpy -&gt; scikit-learn -&gt; Plotly</footer>
</body>
</html>
"""

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n[DONE] Dashboard generated -> {DASHBOARD_PATH}")
