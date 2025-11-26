path_dim_customer = "./data/DIM_Customer.csv"
path_dim_products = "./data/DIM_Products.csv"
path_dim_delivery = "./data/DIM_Delivery.csv"
path_fact_orders = "./data/FACT_Orders.csv"
path_dim_shopping = "./data/DIM_Shopping.csv"


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
print("Diretório atual:", os.getcwd())

pd.set_option("display.max_columns", 50)
plt.style.use("default")

os.makedirs("./kpis", exist_ok=True)
os.makedirs("./images", exist_ok=True)

path_dim_customer = PROJECT_ROOT / "data" / "DIM_Customer.csv"
path_dim_products = PROJECT_ROOT / "data" / "DIM_Products.csv"
path_dim_delivery = PROJECT_ROOT / "data" / "DIM_Delivery.csv"
path_fact_orders = PROJECT_ROOT / "data" / "FACT_Orders.csv"
path_dim_shopping = PROJECT_ROOT / "data" / "DIM_Shopping.csv"
dim_customer = pd.read_csv(path_dim_customer)
dim_products = pd.read_csv(path_dim_products)
dim_delivery = pd.read_csv(path_dim_delivery)
fact_orders = pd.read_csv(path_fact_orders)
dim_shopping = pd.read_csv(path_dim_shopping)


def resumo_qualidade(df, nome):
    print(f"\n===== {nome} =====")
    print("Shape:", df.shape)
    print("\nTipos:")
    print(df.dtypes)
    print("\nNulos por coluna:")
    print(df.isna().sum())
    print("\nDuplicados por Id (se existir coluna 'Id'):")
    if "Id" in df.columns:
        print(df.duplicated(subset=["Id"]).sum())
    else:
        print("N/A")


for nome, df_tmp in [
    ("DIM_Customer", dim_customer),
    ("DIM_Products", dim_products),
    ("DIM_Delivery", dim_delivery),
    ("FACT_Orders", fact_orders),
    ("DIM_Shopping", dim_shopping),
]:
    resumo_qualidade(df_tmp, nome)

def trim_string_columns(df):
    obj_cols = df.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


dim_customer = trim_string_columns(dim_customer)
dim_products = trim_string_columns(dim_products)
dim_delivery = trim_string_columns(dim_delivery)
fact_orders = trim_string_columns(fact_orders)
dim_shopping = trim_string_columns(dim_shopping)
fact_orders["Order_Date"] = pd.to_datetime(fact_orders["Order_Date"])
dim_delivery["D_Date"] = pd.to_datetime(dim_delivery["D_Date"])
dim_delivery["D_Forecast"] = pd.to_datetime(dim_delivery["D_Forecast"])
before_len = len(dim_delivery)
dim_delivery = dim_delivery.dropna(subset=["D_Date", "D_Forecast"])
print(f"\nRemovidas {before_len - len(dim_delivery)} linhas em DIM_Delivery sem datas críticas.")

before_len = len(fact_orders)
fact_orders = fact_orders.dropna(subset=["Order_Date", "Total", "Subtotal"])
print(f"Removidas {before_len - len(fact_orders)} linhas em FACT_Orders sem dados críticos.")

# Garantir unicidade por pedido em FACT_Orders
dup_orders = fact_orders.duplicated(subset=["Id"]).sum()
print(f"\nPedidos duplicados em FACT_Orders (Id): {dup_orders}")
fact_orders = fact_orders.drop_duplicates(subset=["Id"])
df = (
    fact_orders
    .merge(dim_delivery, on="Id", how="left", suffixes=("", "_deliv"))
    .merge(
        dim_customer[["Id", "Customer_Id", "State", "Region"]],
        on="Id",
        how="left",
    )
    .merge(
        dim_products[["Id", "Category", "Subcategory"]],
        on="Id",
        how="left",
    )
)

print("\nRegistros sem correspondência em DIM_Delivery:", df["D_Date"].isna().sum())
print("Registros sem correspondência em DIM_Customer:", df["Customer_Id"].isna().sum())
print("Registros sem correspondência em DIM_Products:", df["Category"].isna().sum())
df["delivery_delay_days"] = (df["D_Date"] - df["D_Forecast"]).dt.days
df["delivery_lead_time"] = (df["D_Date"] - df["Order_Date"]).dt.days
df["is_late"] = (df["D_Date"] > df["D_Forecast"]).astype(int)
df["is_confirmed"] = (df["Purchase_Status"] == "Confirmado").astype(int)
df["freight_share"] = df["P_Sevice"] / df["Total"]
df["discount_abs"] = df["Discount"] * df["Subtotal"]
df["month"] = df["Order_Date"].dt.to_period("M").astype(str)
def detectar_outliers_iqr(series, k=1.5):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    li = q1 - k * iqr
    ls = q3 + k * iqr
    mask = (series >= li) & (series <= ls)
    return mask, li, ls


metricas_outlier = ["Total", "delivery_lead_time", "delivery_delay_days", "Discount"]
mask_global = pd.Series(True, index=df.index)

for col in metricas_outlier:
    m, li, ls = detectar_outliers_iqr(df[col].dropna())
    m_full = pd.Series(True, index=df.index)
    m_full.loc[df[col].dropna().index] = m
    outliers_col = (~m_full).sum()
    print(f"Outliers (IQR) em {col}: {outliers_col} (limites {li:.2f} a {ls:.2f})")
    mask_global &= m_full

df_clean = df[mask_global].copy()
print(f"\nRegistros totais: {len(df)}, após remoção de outliers em métricas-chave: {len(df_clean)}")
print("===== Estatísticas gerais (dataset original) =====")
print(f"Ticket médio: R$ {df['Total'].mean():,.2f}")
print(f"Lead time médio: {df['delivery_lead_time'].mean():.2f} dias")
print(f"Atraso médio: {df['delivery_delay_days'].mean():.2f} dias")
print(f"Proporção atrasados: {df['is_late'].mean():.2%}")
print(f"Cancelamentos: {(df['Purchase_Status']=='Cancelado').mean():.2%}")

print("\n===== Estatísticas gerais (sem outliers em métricas-chave) =====")
print(f"Ticket médio: R$ {df_clean['Total'].mean():,.2f}")
print(f"Lead time médio: {df_clean['delivery_lead_time'].mean():.2f} dias")
print(f"Atraso médio: {df_clean['delivery_delay_days'].mean():.2f} dias")
print(f"Proporção atrasados: {df_clean['is_late'].mean():.2%}")
print(f"Cancelamentos: {(df_clean['Purchase_Status']=='Cancelado').mean():.2%}")
plt.figure()
plt.hist(df_clean["Total"], bins=50)
plt.title("Distribuição do Ticket (sem outliers)")
plt.tight_layout()
plt.savefig("./images/hist_ticket.png", dpi=120)
plt.close()

plt.figure()
plt.hist(df_clean["delivery_lead_time"], bins=50)
plt.title("Lead Time (sem outliers)")
plt.tight_layout()
plt.savefig("./images/hist_leadtime.png", dpi=120)
plt.close()

plt.figure()
plt.hist(df_clean["delivery_delay_days"], bins=50)
plt.title("Atraso na Entrega (dias, sem outliers)")
plt.tight_layout()
plt.savefig("./images/hist_delay.png", dpi=120)
plt.close()

plt.figure()
plt.hist(df_clean["Discount"], bins=50)
plt.title("Distribuição de Descontos (sem outliers)")
plt.tight_layout()
plt.savefig("./images/hist_discount.png", dpi=120)
plt.close()
plt.figure()
plt.boxplot(df_clean["Total"].dropna())
plt.title("Boxplot Ticket")
plt.tight_layout()
plt.savefig("./images/box_ticket.png", dpi=120)
plt.close()

plt.figure()
plt.boxplot(df_clean["delivery_lead_time"].dropna())
plt.title("Boxplot Lead Time")
plt.tight_layout()
plt.savefig("./images/box_leadtime.png", dpi=120)
plt.close()

plt.figure()
plt.boxplot(df_clean["Discount"].dropna())
plt.title("Boxplot Desconto")
plt.tight_layout()
plt.savefig("./images/box_discount.png", dpi=120)
plt.close()
numeric_cols = [
    "Total",
    "Subtotal",
    "Discount",
    "discount_abs",
    "P_Sevice",
    "freight_share",
    "delivery_lead_time",
    "delivery_delay_days",
]

corr = df_clean[numeric_cols].corr()

plt.figure(figsize=(8, 6))
plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
plt.colorbar()
plt.title("Matriz de Correlação")
plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
plt.yticks(range(len(numeric_cols)), numeric_cols)
plt.tight_layout()
plt.savefig("./images/correlacao.png", dpi=120)
plt.close()
seasonality = (
    df_clean.groupby(["month", "Region"])
    .agg(
        revenue=("Total", "sum"),
        orders=("Id", "count"),
        late_rate=("is_late", "mean"),
    )
    .reset_index()
)

seasonality.to_csv("./kpis/seasonality_month_region.csv", index=False)
kpis_by_service = df_clean.groupby("Services").agg(
    orders=("Id", "count"),
    avg_ticket=("Total", "mean"),
    avg_lead_time=("delivery_lead_time", "mean"),
    avg_delay=("delivery_delay_days", "mean"),
    late_rate=("is_late", "mean"),
    cancel_rate=("Purchase_Status", lambda x: (x == "Cancelado").mean()),
    freight_share_mean=("freight_share", "mean"),
).reset_index()

kpis_by_payment = df_clean.groupby("payment").agg(
    orders=("Id", "count"),
    confirm_rate=("is_confirmed", "mean"),
    cancel_rate=("Purchase_Status", lambda x: (x == "Cancelado").mean()),
    avg_ticket=("Total", "mean"),
    avg_discount=("Discount", "mean"),
).reset_index()

kpis_by_region = df_clean.groupby("Region").agg(
    orders=("Id", "count"),
    avg_ticket=("Total", "mean"),
    avg_lead_time=("delivery_lead_time", "mean"),
    late_rate=("is_late", "mean"),
).reset_index()

kpis_by_category = (
    df_clean.groupby(["Category", "Subcategory"])
    .agg(
        orders=("Id", "count"),
        revenue=("Total", "sum"),
        avg_ticket=("Total", "mean"),
        avg_discount=("Discount", "mean"),
    )
    .reset_index()
)

print(kpis_by_service)
print(kpis_by_payment)
print(kpis_by_region)
print(kpis_by_category.head())
bins = [-0.01, 0.0, 0.05, 0.10, 0.20, 1.0]
labels = ["0%", "0–5%", "5–10%", "10–20%", "20%+"]
df_clean["discount_bucket"] = pd.cut(df_clean["Discount"], bins=bins, labels=labels)

elasticity_discount = (
    df_clean.groupby("discount_bucket")
    .agg(
        revenue=("Total", "sum"),
        orders=("Id", "count"),
        avg_ticket=("Total", "mean"),
    )
    .reset_index()
)

print(elasticity_discount)


def ic_media(series, alpha=0.05):
    x = series.dropna().values
    n = len(x)
    media = np.mean(x)
    s = np.std(x, ddof=1)
    se = s / np.sqrt(n)
    t_crit = stats.t.ppf(1 - alpha / 2, df=n - 1)
    li = media - t_crit * se
    ls = media + t_crit * se
    return media, se, li, ls


def ic_proporcao(x, alpha=0.05):
    x = np.asarray(x).astype(int)
    n = len(x)
    p_hat = x.mean()
    se = np.sqrt(p_hat * (1 - p_hat) / n)
    z = stats.norm.ppf(1 - alpha / 2)
    li = p_hat - z * se
    ls = p_hat + z * se
    return p_hat, se, li, ls


def checar_normalidade(series):
    from scipy.stats import shapiro

    x = series.dropna()
    stat, p_value = shapiro(x.sample(min(5000, len(x)), random_state=42))
    print(f"Shapiro-Wilk p-valor: {p_value:.4f} (H0: normalidade)")
    return stat, p_value


def checar_independencia(series):
    x = series.dropna()
    if len(x) < 3:
        return np.nan
    autocorr = x.autocorr(lag=1)
    print(f"Autocorrelação lag-1: {autocorr:.4f}")
    return autocorr
print("\nIC Ticket Médio:", ic_media(df_clean["Total"]))
checar_normalidade(df_clean["Total"])
checar_independencia(df_clean["Total"])

print("\nIC Atraso Médio:", ic_media(df_clean["delivery_delay_days"]))
checar_normalidade(df_clean["delivery_delay_days"])
checar_independencia(df_clean["delivery_delay_days"])

print("\nIC Atraso (%) :", ic_proporcao(df_clean["is_late"]))
print(
    "\nIC Cancelamentos (%) :",
    ic_proporcao((df_clean["Purchase_Status"] == "Cancelado").astype(int)),
)
kpis_by_service.to_csv("./kpis/kpis_by_service.csv", index=False)
kpis_by_payment.to_csv("./kpis/kpis_by_payment.csv", index=False)
kpis_by_region.to_csv("./kpis/kpis_by_region.csv", index=False)
kpis_by_category.to_csv("./kpis/kpis_by_category.csv", index=False)
elasticity_discount.to_csv("./kpis/elasticity_discount.csv", index=False)

df_clean.to_csv("./kpis/fact_analytic_clean.csv", index=False)

print(
    "Arquivos exportados para /kpis e figuras para /images (inclui base analítica para Power BI)."
)
