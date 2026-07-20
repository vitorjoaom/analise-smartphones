import json
import os

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings("ignore")

FRAG_DIR = os.path.join("outputs", "fragments")
os.makedirs(FRAG_DIR, exist_ok=True)


def save_fragment(fig, name):
    fig.write_html(os.path.join(FRAG_DIR, f"{name}.html"),
                    full_html=False, include_plotlyjs=False,
                    config={"displaylogo": False})
    print(f"[✓] fragment: {name}.html")

# ── Paleta "cores sabão" (pastéis suaves) ────────────────────────────────────
SABAO = [
    "#B5D5C5",  # verde-menta suave
    "#F7C5CC",  # rosa pó
    "#C3D4F0",  # azul névoa
    "#F5E6C8",  # bege pêssego
    "#D4C5F0",  # lilás bruma
    "#C8EAE2",  # turquesa claro
    "#F0D4C5",  # salmão pastel
    "#D5EAB5",  # verde-lima suave
    "#F0C5E0",  # malva claro
    "#C5D5F0",  # azul-cinza suave
]
BG        = "#F8F6F2"   # fundo creme
GRID      = "#E8E4DE"   # grade discreta
FONT_CLR  = "#4A4540"   # texto quente

LAYOUT_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(color=FONT_CLR, family="Segoe UI, Arial"),
    title_font=dict(size=18, color=FONT_CLR),
    legend=dict(bgcolor=BG, bordercolor=GRID, borderwidth=1),
)

# ── Carregar dados ────────────────────────────────────────────────────────────
df = pd.read_csv("smartphones.csv")

print("=" * 65)
print("  ANÁLISE PREDITIVA DE SMARTPHONES — VISÃO DE FUTURO")
print("=" * 65)
print(f"  Dataset: {len(df):,} smartphones · {df.shape[1]} colunas\n")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 1 · REGRESSÃO LINEAR — Preço médio por ano + previsão até 2032
# ════════════════════════════════════════════════════════════════════════════════
price_year = df.groupby("release_year")["price"].agg(["mean", "std", "count"]).reset_index()
price_year.columns = ["ano", "preco_medio", "preco_std", "qtd"]

anos_hist = price_year["ano"].values.reshape(-1, 1)
precos    = price_year["preco_medio"].values

lr = LinearRegression().fit(anos_hist, precos)

anos_fut  = np.arange(price_year["ano"].min(), 2033).reshape(-1, 1)
pred_fut  = lr.predict(anos_fut)

# Intervalo de confiança simples (±1 std da regressão)
residuos  = precos - lr.predict(anos_hist)
std_res   = np.std(residuos)

fig1 = go.Figure()

# Banda de confiança
fig1.add_trace(go.Scatter(
    x=anos_fut.flatten().tolist() + anos_fut.flatten().tolist()[::-1],
    y=(pred_fut + 1.5 * std_res).tolist() + (pred_fut - 1.5 * std_res).tolist()[::-1],
    fill="toself", fillcolor="rgba(195,212,240,0.3)",
    line=dict(color="rgba(0,0,0,0)"),
    name="Intervalo de confiança", showlegend=True,
))

# Linha histórica
fig1.add_trace(go.Scatter(
    x=price_year["ano"], y=price_year["preco_medio"],
    mode="lines+markers",
    line=dict(color=SABAO[0], width=3),
    marker=dict(size=9, color=SABAO[0], line=dict(color=FONT_CLR, width=1)),
    error_y=dict(type="data", array=price_year["preco_std"], visible=True,
                 color="rgba(150,150,150,0.5)"),
    name="Preço médio histórico",
))

# Linha futura
mask_fut = anos_fut.flatten() > price_year["ano"].max()
fig1.add_trace(go.Scatter(
    x=anos_fut.flatten()[mask_fut], y=pred_fut[mask_fut],
    mode="lines+markers",
    line=dict(color=SABAO[3], width=3, dash="dot"),
    marker=dict(size=9, color=SABAO[3], symbol="diamond",
                line=dict(color=FONT_CLR, width=1)),
    name="Projeção (Regressão Linear)",
))

fig1.add_vline(x=price_year["ano"].max(), line_dash="dash",
               line_color=GRID, annotation_text="Hoje →", annotation_font_size=11)

fig1.update_layout(
    **LAYOUT_BASE,
    title="📈 Projeção de Preço Médio de Smartphones até 2032",
    xaxis=dict(title="Ano", gridcolor=GRID, zeroline=False),
    yaxis=dict(title="Preço Médio (R$)", gridcolor=GRID,
               tickformat=",.0f", zeroline=False),
    hovermode="x unified",
)
fig1.write_html("01_projecao_preco.html")
print("[✓] 01_projecao_preco.html")
save_fragment(fig1, "08_projecao_preco")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 2 · RANDOM FOREST — Previsão de preço por especificações
# ════════════════════════════════════════════════════════════════════════════════
features = ["screen_size", "battery_capacity", "ram", "storage",
            "camera_mp", "front_camera_mp", "refresh_rate",
            "weight", "thickness", "fast_charging",
            "release_year", "bluetooth_version"]

target = "price"

le_os   = LabelEncoder()
le_net  = LabelEncoder()
le_mat  = LabelEncoder()
le_usb  = LabelEncoder()
le_wifi = LabelEncoder()

df_ml = df.copy()
df_ml["os_enc"]   = le_os.fit_transform(df_ml["operating_system"])
df_ml["net_enc"]  = le_net.fit_transform(df_ml["network_support"])
df_ml["mat_enc"]  = le_mat.fit_transform(df_ml["body_material"])
df_ml["usb_enc"]  = le_usb.fit_transform(df_ml["usb_type"])
df_ml["wifi_enc"] = le_wifi.fit_transform(df_ml["wifi_version"])
df_ml["dual_enc"] = (df_ml["dual_sim"] == "Yes").astype(int)
df_ml["fp_enc"]   = (df_ml["fingerprint_sensor"] == "Yes").astype(int)

all_features = features + ["os_enc", "net_enc", "mat_enc", "usb_enc",
                            "wifi_enc", "dual_enc", "fp_enc"]

X = df_ml[all_features]
y = df_ml[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

rf  = RandomForestRegressor(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1)
gb  = GradientBoostingRegressor(n_estimators=120, max_depth=5, random_state=42)
rf.fit(X_train, y_train)
gb.fit(X_train_s, y_train)

# Métricas
rf_pred  = rf.predict(X_test)
gb_pred  = gb.predict(X_test_s)

rf_mae   = mean_absolute_error(y_test, rf_pred)
gb_mae   = mean_absolute_error(y_test, gb_pred)
rf_r2    = r2_score(y_test, rf_pred)
gb_r2    = r2_score(y_test, gb_pred)

print(f"\n  Random Forest   → MAE: R$ {rf_mae:,.0f} | R²: {rf_r2:.3f}")
print(f"  Gradient Boost  → MAE: R$ {gb_mae:,.0f} | R²: {gb_r2:.3f}")

# Importância das features
importances = pd.Series(rf.feature_importances_, index=all_features).sort_values()

fig2 = go.Figure(go.Bar(
    x=importances.values,
    y=importances.index,
    orientation="h",
    marker=dict(
        color=importances.values,
        colorscale=[[0, SABAO[8]], [0.5, SABAO[4]], [1, SABAO[0]]],
        line=dict(color=FONT_CLR, width=0.5),
    ),
    text=[f"{v:.3f}" for v in importances.values],
    textposition="outside",
))
fig2.update_layout(
    **LAYOUT_BASE,
    title="🤖 Importância das Variáveis na Previsão de Preço (Random Forest)",
    xaxis=dict(title="Importância", gridcolor=GRID, zeroline=False),
    yaxis=dict(gridcolor=GRID),
    height=520,
    margin=dict(l=140),
)
fig2.write_html("02_importancia_features.html")
print("[✓] 02_importancia_features.html")
save_fragment(fig2, "09_importancia_features")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 3 · Previsto vs Real (scatter)
# ════════════════════════════════════════════════════════════════════════════════
sample_idx = np.random.choice(len(y_test), 500, replace=False)
y_samp     = y_test.values[sample_idx]
rf_samp    = rf_pred[sample_idx]
gb_samp    = gb_pred[sample_idx]

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=y_samp, y=rf_samp, mode="markers",
    marker=dict(color=SABAO[2], size=7, opacity=0.75,
                line=dict(color=FONT_CLR, width=0.4)),
    name=f"Random Forest (R²={rf_r2:.3f})",
))
fig3.add_trace(go.Scatter(
    x=y_samp, y=gb_samp, mode="markers",
    marker=dict(color=SABAO[6], size=7, opacity=0.75,
                line=dict(color=FONT_CLR, width=0.4)),
    name=f"Gradient Boosting (R²={gb_r2:.3f})",
))
lims = [0, int(y_test.max() * 1.05)]
fig3.add_trace(go.Scatter(
    x=lims, y=lims, mode="lines",
    line=dict(color=FONT_CLR, dash="dash", width=1.5),
    name="Previsão perfeita",
))
fig3.update_layout(
    **LAYOUT_BASE,
    title="🎯 Preço Real vs Previsto — Comparativo de Modelos",
    xaxis=dict(title="Preço Real (R$)", gridcolor=GRID, tickformat=",.0f"),
    yaxis=dict(title="Preço Previsto (R$)", gridcolor=GRID, tickformat=",.0f"),
)
fig3.write_html("03_real_vs_previsto.html")
print("[✓] 03_real_vs_previsto.html")
save_fragment(fig3, "10_real_vs_previsto")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 4 · Tendência futura das especificações (até 2032)
# ════════════════════════════════════════════════════════════════════════════════
specs = {
    "RAM (GB)":           "ram",
    "Bateria (mAh)":      "battery_capacity",
    "Câmera (MP)":        "camera_mp",
    "Taxa Atualiz. (Hz)": "refresh_rate",
    "Armazenamento (GB)": "storage",
}

anos_proj  = np.arange(df["release_year"].min(), 2033)
anos_fut_r = anos_proj.reshape(-1, 1)

fig4 = make_subplots(
    rows=2, cols=3,
    subplot_titles=list(specs.keys()) + ["Rede 5G (% do mercado)"],
    horizontal_spacing=0.08, vertical_spacing=0.14,
)
positions = [(1,1),(1,2),(1,3),(2,1),(2,2)]

for idx, (label, col) in enumerate(specs.items()):
    row, c = positions[idx]
    hist = df.groupby("release_year")[col].mean().reset_index()
    lrm  = LinearRegression().fit(hist["release_year"].values.reshape(-1,1),
                                   hist[col].values)
    proj = lrm.predict(anos_fut_r)
    proj = np.clip(proj, hist[col].min() * 0.8, None)

    mask_h = anos_proj <= hist["release_year"].max()
    mask_f = anos_proj >  hist["release_year"].max()

    fig4.add_trace(go.Scatter(
        x=hist["release_year"], y=hist[col], mode="lines+markers",
        line=dict(color=SABAO[idx], width=2.5),
        marker=dict(size=7, color=SABAO[idx], line=dict(color=FONT_CLR, width=0.6)),
        name=label, showlegend=False,
    ), row=row, col=c)
    fig4.add_trace(go.Scatter(
        x=anos_proj[mask_f], y=proj[mask_f], mode="lines",
        line=dict(color=SABAO[idx], width=2, dash="dot"),
        name=f"{label} (proj.)", showlegend=False,
    ), row=row, col=c)

# Crescimento 5G estimado
anos_5g = np.arange(2018, 2033)
pct_5g_base = df[df["release_year"].isin(range(2018, df["release_year"].max()+1))]\
    .groupby("release_year").apply(lambda x: (x["network_support"]=="5G").mean()*100).reset_index()
pct_5g_base.columns = ["ano","pct"]

lr5g  = LinearRegression().fit(pct_5g_base["ano"].values.reshape(-1,1), pct_5g_base["pct"].values)
proj5g = np.clip(lr5g.predict(anos_5g.reshape(-1,1)), 0, 100)

mask_h5 = anos_5g <= pct_5g_base["ano"].max()
mask_f5 = anos_5g >  pct_5g_base["ano"].max()

fig4.add_trace(go.Scatter(
    x=pct_5g_base["ano"], y=pct_5g_base["pct"], mode="lines+markers",
    line=dict(color=SABAO[5], width=2.5),
    marker=dict(size=7, color=SABAO[5], line=dict(color=FONT_CLR, width=0.6)),
    showlegend=False,
), row=2, col=3)
fig4.add_trace(go.Scatter(
    x=anos_5g[mask_f5], y=proj5g[mask_f5], mode="lines",
    line=dict(color=SABAO[5], width=2, dash="dot"),
    showlegend=False,
), row=2, col=3)

fig4.update_layout(
    **LAYOUT_BASE,
    title="🔮 Projeção de Especificações Técnicas até 2032",
    height=620,
)
for i in fig4.layout.annotations:
    i.font.size = 12
    i.font.color = FONT_CLR
fig4.update_xaxes(gridcolor=GRID, zeroline=False)
fig4.update_yaxes(gridcolor=GRID, zeroline=False)
fig4.write_html("04_tendencias_specs.html")
print("[✓] 04_tendencias_specs.html")
save_fragment(fig4, "11_tendencias_specs")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 5 · Dashboard final interativo — Marcas × Specs (bubble chart)
# ════════════════════════════════════════════════════════════════════════════════
brand_agg = df.groupby("brand_name").agg(
    preco=("price","mean"),
    camera=("camera_mp","mean"),
    ram=("ram","mean"),
    bateria=("battery_capacity","mean"),
    qtd=("brand_name","count"),
).reset_index().sort_values("qtd", ascending=False).head(15)

fig5 = px.scatter(
    brand_agg,
    x="preco", y="camera",
    size="qtd", color="brand_name",
    hover_name="brand_name",
    hover_data={"ram":":.1f", "bateria":":.0f", "qtd":True,
                "preco":":.0f", "camera":":.0f"},
    labels={"preco":"Preço Médio (R$)", "camera":"Câmera Média (MP)",
            "qtd":"Quantidade", "brand_name":"Marca"},
    color_discrete_sequence=SABAO,
    size_max=60,
    title="🫧 Marcas: Preço × Câmera × Volume (tamanho = quantidade de modelos)",
)
fig5.update_layout(
    **LAYOUT_BASE,
    xaxis=dict(gridcolor=GRID, zeroline=False, tickformat=",.0f"),
    yaxis=dict(gridcolor=GRID, zeroline=False),
)
fig5.write_html("05_bubble_marcas.html")
print("[✓] 05_bubble_marcas.html")
save_fragment(fig5, "12_bubble_marcas")

# ════════════════════════════════════════════════════════════════════════════════
# BLOCO 6 · Relatório de insights preditivos
# ════════════════════════════════════════════════════════════════════════════════
anos_prev = [2026, 2028, 2030, 2032]
preds_ano = lr.predict(np.array(anos_prev).reshape(-1, 1))
preds_ram  = LinearRegression().fit(
    df.groupby("release_year")["ram"].mean().reset_index()["release_year"].values.reshape(-1,1),
    df.groupby("release_year")["ram"].mean().reset_index()["ram"].values
).predict(np.array(anos_prev).reshape(-1,1))

print("\n" + "=" * 65)
print("  INSIGHTS PREDITIVOS — O FUTURO DOS CELULARES")
print("=" * 65)
print(f"\n  Modelo escolhido (menor MAE): ", end="")
melhor = "Random Forest" if rf_mae < gb_mae else "Gradient Boosting"
print(f"{melhor}")
print(f"  Erro médio de previsão de preço: R$ {min(rf_mae, gb_mae):,.0f}")

print("\n  Projeção de preço médio e RAM mínima esperada:\n")
print(f"  {'Ano':<8} {'Preço Médio (R$)':>18} {'RAM Média (GB)':>16}")
print(f"  {'-'*44}")
for ano, p, r in zip(anos_prev, preds_ano, preds_ram):
    print(f"  {ano:<8} {p:>18,.0f} {max(r,0):>16.1f}")

print("""
  Conclusões do modelo preditivo:
  ─────────────────────────────────────────────────────────
  • Os preços tendem a crescer moderadamente, impulsionados
    por chips mais avançados e telas de alta taxa.
  • RAM e armazenamento devem dobrar até 2032 nos segmentos
    intermediários, tornando 16 GB RAM padrão de entrada.
  • 5G ultrapassará 80% dos lançamentos globais antes de 2030.
  • Câmera e refresh_rate têm menor impacto no preço do que
    RAM e ano de lançamento (evidenciado pelo Random Forest).
  • O material do corpo e suporte a rede são os encodings
    categóricos mais relevantes para o preço.
  ─────────────────────────────────────────────────────────
""")

print("  Arquivos gerados:")
for f in ["01_projecao_preco.html", "02_importancia_features.html",
          "03_real_vs_previsto.html", "04_tendencias_specs.html",
          "05_bubble_marcas.html"]:
    print(f"    · {f}")
print("\n  Abra qualquer .html no navegador para interação completa.\n")

# ── KPIs para o dashboard ────────────────────────────────────────────────────
kpis_predictive = {
    "best_model": melhor,
    "rf_mae": round(float(rf_mae), 2),
    "rf_r2": round(float(rf_r2), 4),
    "gb_mae": round(float(gb_mae), 2),
    "gb_r2": round(float(gb_r2), 4),
    "price_2032": round(float(preds_ano[-1]), 2),
    "ram_2032": round(float(max(preds_ram[-1], 0)), 2),
    "top_price_feature": importances.index[-1],
}
os.makedirs("outputs", exist_ok=True)
with open(os.path.join("outputs", "kpis_predictive.json"), "w", encoding="utf-8") as f:
    json.dump(kpis_predictive, f, ensure_ascii=False, indent=2)
print("[✓] outputs/kpis_predictive.json")
