import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

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
