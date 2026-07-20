import json
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.graph_objects as go

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

# ── Paleta "cores sabão" (mesma usada em analise_preditiva.py, para consistência) ──
SABAO = [
    "#B5D5C5", "#F7C5CC", "#C3D4F0", "#F5E6C8", "#D4C5F0",
    "#C8EAE2", "#F0D4C5", "#D5EAB5", "#F0C5E0", "#C5D5F0",
]
BG, GRID, FONT_CLR = "#F8F6F2", "#E8E4DE", "#4A4540"
LAYOUT_BASE = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=FONT_CLR, family="Segoe UI, Arial"),
    title_font=dict(size=18, color=FONT_CLR),
    legend=dict(bgcolor=BG, bordercolor=GRID, borderwidth=1),
)

FRAG_DIR = os.path.join("outputs", "fragments")
os.makedirs(FRAG_DIR, exist_ok=True)


def save_fragment(fig, name):
    fig.write_html(os.path.join(FRAG_DIR, f"{name}.html"),
                    full_html=False, include_plotlyjs=False,
                    config={"displaylogo": False})
    print(f"[✓] fragment: {name}.html")


df = pd.read_csv("smartphones.csv")

# ── 1. Visão geral ──────────────────────────────────────────────────────────
print("=" * 60)
print("VISÃO GERAL DO DATASET")
print("=" * 60)
print(f"Registros : {len(df):,}")
print(f"Colunas   : {df.shape[1]}")
print(f"\nEstatísticas descritivas (numéricas):")
print(df[["price", "battery_capacity", "ram", "storage",
          "camera_mp", "refresh_rate", "screen_size"]].describe().round(2))

# ── 2. Marcas mais presentes ────────────────────────────────────────────────
top_brands = df["brand_name"].value_counts().head(10)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Análise de Smartphones", fontsize=15, fontweight="bold")

ax = axes[0, 0]
top_brands.plot(kind="bar", ax=ax, color=sns.color_palette("muted", 10))
ax.set_title("Top 10 Marcas (quantidade)")
ax.set_xlabel("")
ax.set_ylabel("Quantidade")
ax.tick_params(axis="x", rotation=30)

# ── 3. Distribuição de preço por marca (top 6) ──────────────────────────────
ax = axes[0, 1]
top6 = df["brand_name"].value_counts().head(6).index
sns.boxplot(data=df[df["brand_name"].isin(top6)],
            x="brand_name", y="price", ax=ax,
            palette="muted", order=top6)
ax.set_title("Distribuição de Preço — Top 6 Marcas")
ax.set_xlabel("")
ax.set_ylabel("Preço (R$)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.tick_params(axis="x", rotation=20)

# ── 4. Sistema operacional ───────────────────────────────────────────────────
ax = axes[1, 0]
os_counts = df["operating_system"].value_counts()
ax.pie(os_counts, labels=os_counts.index, autopct="%1.1f%%",
       colors=sns.color_palette("muted", len(os_counts)), startangle=90)
ax.set_title("Sistemas Operacionais")

# ── 5. Preço médio por ano de lançamento ────────────────────────────────────
ax = axes[1, 1]
price_year = df.groupby("release_year")["price"].mean().sort_index()
price_year.plot(ax=ax, marker="o", color="#4878CF")
ax.set_title("Preço Médio por Ano de Lançamento")
ax.set_xlabel("Ano")
ax.set_ylabel("Preço Médio (R$)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

plt.tight_layout()
plt.savefig("graficos_visao_geral.png", bbox_inches="tight")
plt.close()
print("\n[Salvo] graficos_visao_geral.png")

# ── 6. Correlações ───────────────────────────────────────────────────────────
num_cols = ["price", "battery_capacity", "ram", "storage",
            "camera_mp", "screen_size", "refresh_rate",
            "fast_charging", "weight", "thickness"]
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, ax=ax, linewidths=0.5)
ax.set_title("Mapa de Correlação entre Variáveis Numéricas", fontsize=13)
plt.tight_layout()
plt.savefig("correlacao.png", bbox_inches="tight")
plt.close()
print("[Salvo] correlacao.png")

# ── 7. Insights textuais ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("INSIGHTS")
print("=" * 60)

print(f"\nMarca mais comum    : {df['brand_name'].value_counts().idxmax()}")
print(f"Marca mais cara (média): {df.groupby('brand_name')['price'].mean().idxmax()}")
print(f"Preço médio geral   : R$ {df['price'].mean():,.0f}")
print(f"Preço mediano       : R$ {df['price'].median():,.0f}")

pct_5g = (df["network_support"] == "5G").mean() * 100
print(f"\nAparelhos com 5G    : {pct_5g:.1f}%")

pct_fp = (df["fingerprint_sensor"] == "Yes").mean() * 100
print(f"Com sensor de digital: {pct_fp:.1f}%")

pct_dsim = (df["dual_sim"] == "Yes").mean() * 100
print(f"Com Dual SIM        : {pct_dsim:.1f}%")

corr_price_ram = df["price"].corr(df["ram"])
print(f"\nCorrelação preço×RAM   : {corr_price_ram:.3f}")
corr_price_cam = df["price"].corr(df["camera_mp"])
print(f"Correlação preço×câmera: {corr_price_cam:.3f}")

# ── 8. Gráficos extras: RAM e armazenamento ──────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
df["ram"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#4878CF")
ax.set_title("Distribuição de RAM (GB)")
ax.set_xlabel("RAM (GB)")
ax.set_ylabel("Quantidade")
ax.tick_params(axis="x", rotation=0)

ax = axes[1]
df["storage"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#6ACC65")
ax.set_title("Distribuição de Armazenamento (GB)")
ax.set_xlabel("Armazenamento (GB)")
ax.set_ylabel("Quantidade")
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig("ram_storage.png", bbox_inches="tight")
plt.close()
print("[Salvo] ram_storage.png")

print("\nAnálise concluída!")

# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICOS INTERATIVOS (Plotly) — mesmas análises, versão interativa para o dashboard
# ════════════════════════════════════════════════════════════════════════════════

# 01 · Top 10 marcas
fig_brands = go.Figure(go.Bar(
    x=top_brands.index, y=top_brands.values,
    marker=dict(color=SABAO[:len(top_brands)], line=dict(color=FONT_CLR, width=0.5)),
    text=top_brands.values, textposition="outside",
))
fig_brands.update_layout(
    **LAYOUT_BASE, title="🏷️ Top 10 Marcas por Quantidade de Modelos",
    xaxis=dict(title="", gridcolor=GRID), yaxis=dict(title="Quantidade", gridcolor=GRID),
)
save_fragment(fig_brands, "01_top_brands")

# 02 · Distribuição de preço — top 6 marcas (boxplot)
fig_price_box = go.Figure()
for i, brand in enumerate(top6):
    fig_price_box.add_trace(go.Box(
        y=df.loc[df["brand_name"] == brand, "price"], name=brand,
        marker_color=SABAO[i % len(SABAO)], boxmean=True,
    ))
fig_price_box.update_layout(
    **LAYOUT_BASE, title="💸 Distribuição de Preço — Top 6 Marcas",
    yaxis=dict(title="Preço (R$)", gridcolor=GRID, tickformat=",.0f"),
    showlegend=False,
)
save_fragment(fig_price_box, "02_price_by_brand")

# 03 · Participação por sistema operacional
fig_os = go.Figure(go.Pie(
    labels=os_counts.index, values=os_counts.values, hole=0.45,
    marker=dict(colors=SABAO, line=dict(color=BG, width=2)),
))
fig_os.update_layout(**LAYOUT_BASE, title="📱 Participação por Sistema Operacional")
save_fragment(fig_os, "03_os_share")

# 04 · Preço médio por ano de lançamento
fig_price_year = go.Figure(go.Scatter(
    x=price_year.index, y=price_year.values, mode="lines+markers",
    line=dict(color=SABAO[0], width=3),
    marker=dict(size=9, color=SABAO[0], line=dict(color=FONT_CLR, width=1)),
))
fig_price_year.update_layout(
    **LAYOUT_BASE, title="📈 Preço Médio por Ano de Lançamento",
    xaxis=dict(title="Ano", gridcolor=GRID),
    yaxis=dict(title="Preço Médio (R$)", gridcolor=GRID, tickformat=",.0f"),
)
save_fragment(fig_price_year, "04_price_by_year")

# 05 · Distribuição de RAM e Armazenamento
ram_counts = df["ram"].value_counts().sort_index()
storage_counts = df["storage"].value_counts().sort_index()
fig_ram_storage = go.Figure()
fig_ram_storage.add_trace(go.Bar(x=ram_counts.index.astype(str), y=ram_counts.values,
                                  name="RAM (GB)", marker_color=SABAO[0]))
fig_ram_storage.update_layout(
    **LAYOUT_BASE, title="💾 Distribuição de RAM (GB)",
    xaxis=dict(title="RAM (GB)", gridcolor=GRID, type="category"),
    yaxis=dict(title="Quantidade", gridcolor=GRID),
)
save_fragment(fig_ram_storage, "05_ram_distribution")

fig_storage = go.Figure(go.Bar(
    x=storage_counts.index.astype(str), y=storage_counts.values,
    marker_color=SABAO[7],
))
fig_storage.update_layout(
    **LAYOUT_BASE, title="🗄️ Distribuição de Armazenamento (GB)",
    xaxis=dict(title="Armazenamento (GB)", gridcolor=GRID, type="category"),
    yaxis=dict(title="Quantidade", gridcolor=GRID),
)
save_fragment(fig_storage, "06_storage_distribution")

# 07 · Mapa de correlação
fig_corr = go.Figure(go.Heatmap(
    z=corr.values, x=corr.columns, y=corr.columns,
    colorscale=[[0, SABAO[1]], [0.5, BG], [1, SABAO[0]]],
    zmid=0, text=corr.round(2).values, texttemplate="%{text}",
    textfont=dict(size=10, color=FONT_CLR),
))
fig_corr.update_layout(
    **LAYOUT_BASE, title="🔗 Mapa de Correlação entre Variáveis Numéricas",
    height=560, xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID, autorange="reversed"),
)
save_fragment(fig_corr, "07_correlation_heatmap")

# ── KPIs para o dashboard ────────────────────────────────────────────────────
kpis_eda = {
    "total_smartphones": int(len(df)),
    "n_columns": int(df.shape[1]),
    "n_brands": int(df["brand_name"].nunique()),
    "top_brand": df["brand_name"].value_counts().idxmax(),
    "priciest_brand": df.groupby("brand_name")["price"].mean().idxmax(),
    "avg_price": round(float(df["price"].mean()), 2),
    "median_price": round(float(df["price"].median()), 2),
    "pct_5g": round(float(pct_5g), 1),
    "pct_fingerprint": round(float(pct_fp), 1),
    "pct_dual_sim": round(float(pct_dsim), 1),
    "corr_price_ram": round(float(corr_price_ram), 3),
    "corr_price_camera": round(float(corr_price_cam), 3),
}
os.makedirs("outputs", exist_ok=True)
with open(os.path.join("outputs", "kpis_eda.json"), "w", encoding="utf-8") as f:
    json.dump(kpis_eda, f, ensure_ascii=False, indent=2)
print("[✓] outputs/kpis_eda.json")
