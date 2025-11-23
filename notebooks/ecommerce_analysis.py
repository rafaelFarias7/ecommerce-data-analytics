# AJUSTE DOS PATHS PARA OS ARQUIVOS DE DADOS
path_dim_customer = "./data/DIM_Customer.csv"
path_dim_products = "./data/DIM_Products.csv"
path_dim_delivery = "./data/DIM_Delivery.csv"
path_fact_orders = "./data/FACT_Orders.csv"
path_dim_shopping = "./data/DIM_Shopping.csv"


# %% [markdown]
# # Análise de Dados - E-commerce (Brasil)
# 
# Pipeline completo:
# - Carregamento e preparação dos dados
# - Feature Engineering
# - Análise exploratória (EDA) com gráficos
# - KPIs
# - Inferência Estatística

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

# %% [markdown]
# ## Ajustar diretório raiz do projeto

# %%
# 🔥 Ajustar diretório raiz do projeto (ESSENCIAL para caminhos relativos)
os.chdir(r"C:\Users\rafaf\OneDrive\Desktop\ecommerce-data-analytics-pipeline")
print("Diretório atual:", os.getcwd())

# Configurações gerais
pd.set_option("display.max_columns", 50)
plt.style.use("default")

# Criar pastas de saída se não existirem
os.makedirs("./kpis", exist_ok=True)
os.makedirs("./images", exist_ok=True)

# %% [markdown]
# ## 1. Carregamento dos dados

# %%
# Caminhos dos arquivos na pasta ./data/
path_dim_customer = "./data/DIM_Customer.csv"
path_dim_products = "./data/DIM_Products.csv"
path_dim_delivery = "./data/DIM_Delivery.csv"
path_fact_orders = "./data/FACT_Orders.csv"
path_dim_shopping = "./data/DIM_Shopping.csv"

# Carregar os CSVs
dim_customer = pd.read_csv(path_dim_customer)
dim_products = pd.read_csv(path_dim_products)
dim_delivery = pd.read_csv(path_dim_delivery)
fact_orders = pd.read_csv(path_fact_orders)
dim_shopping = pd.read_csv(path_dim_shopping)

dim_customer.head()

# %% [markdown]
# ## 2. Qualidade dos dados & tipos

# %%
def resumo_qualidade(df, nome):
    print(f"\n===== {nome} =====")
    print("Shape:", df.shape)
    print("\nTipos:")
    print(df.dtypes)
    print("\nNulos por coluna:")
    print(df.isna().sum())

for nome, df in [
    ("DIM_Customer", dim_customer),
    ("DIM_Products", dim_products),
    ("DIM_Delivery", dim_delivery),
    ("FACT_Orders", fact_orders),
    ("DIM_Shopping", dim_shopping),
]:
    resumo_qualidade(df, nome)

# %% [markdown]
# ## 3. Conversão de tipos e joins

# %%
fact_orders["Order_Date"] = pd.to_datetime(fact_orders["Order_Date"])
dim_delivery["D_Date"] = pd.to_datetime(dim_delivery["D_Date"])
dim_delivery["D_Forecast"] = pd.to_datetime(dim_delivery["D_Forecast"])

df = (
    fact_orders
    .merge(dim_delivery, on="Id", how="left", suffixes=("", "_deliv"))
    .merge(dim_customer[["Id", "Customer_Id", "State", "Region"]], on="Id", how="left")
)

df.head()

# %% [markdown]
# ## 4. Feature Engineering

# %%
df["delivery_delay_days"] = (df["D_Date"] - df["D_Forecast"]).dt.days
df["delivery_lead_time"] = (df["D_Date"] - df["Order_Date"]).dt.days
df["is_late"] = (df["D_Date"] > df["D_Forecast"]).astype(int)
df["is_confirmed"] = (df["Purchase_Status"] == "Confirmado").astype(int)
df["freight_share"] = df["P_Sevice"] / df["Total"]
df["discount_abs"] = df["Discount"] * df["Subtotal"]
df["month"] = df["Order_Date"].dt.to_period("M").astype(str)

df.head()

# %% [markdown]
# ## 5. Estatísticas descritivas

# %%
print("===== Estatísticas gerais =====")
print(f"Ticket médio: R$ {df['Total'].mean():,.2f}")
print(f"Lead time médio: {df['delivery_lead_time'].mean():.2f} dias")
print(f"Atraso médio: {df['delivery_delay_days'].mean():.2f} dias")
print(f"Proporção atrasados: {df['is_late'].mean():.2%}")
print(f"Cancelamentos: {(df['Purchase_Status']=='Cancelado').mean():.2%}")

# %% [markdown]
# ## 6. EDA – Gráficos

# %%
plt.hist(df["Total"], bins=50)
plt.title("Distribuição do Ticket")
plt.tight_layout()
plt.savefig("./images/hist_ticket.png", dpi=120)
plt.show()

plt.hist(df["delivery_lead_time"], bins=50)
plt.title("Lead Time")
plt.tight_layout()
plt.savefig("./images/hist_leadtime.png", dpi=120)
plt.show()

# Correlação
numeric_cols = [
    "Total","Subtotal","Discount","discount_abs",
    "P_Sevice","freight_share","delivery_lead_time","delivery_delay_days"
]

corr = df[numeric_cols].corr()

plt.figure(figsize=(8,6))
plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
plt.colorbar()
plt.title("Matriz de Correlação")
plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45)
plt.yticks(range(len(numeric_cols)), numeric_cols)
plt.tight_layout()
plt.savefig("./images/correlacao.png", dpi=120)
plt.show()

# %% [markdown]
# ## 7. KPIs por dimensão

# %%
kpis_by_service = df.groupby("Services").agg(
    orders=("Id","count"),
    avg_ticket=("Total","mean"),
    avg_lead_time=("delivery_lead_time","mean"),
    avg_delay=("delivery_delay_days","mean"),
    late_rate=("is_late","mean"),
    cancel_rate=("Purchase_Status", lambda x:(x=="Cancelado").mean()),
    freight_share_mean=("freight_share","mean")
).reset_index()

kpis_by_payment = df.groupby("payment").agg(
    orders=("Id","count"),
    confirm_rate=("is_confirmed","mean"),
    cancel_rate=("Purchase_Status", lambda x:(x=="Cancelado").mean()),
    avg_ticket=("Total","mean")
).reset_index()

kpis_by_region = df.groupby("Region").agg(
    orders=("Id","count"),
    avg_ticket=("Total","mean"),
    avg_lead_time=("delivery_lead_time","mean"),
    late_rate=("is_late","mean"),
).reset_index()

print(kpis_by_service)
print(kpis_by_payment)
print(kpis_by_region)

# %% [markdown]
# ## 8. Funções de Intervalo de Confiança

# %%
def ic_media(series, alpha=0.05):
    x = series.dropna().values
    n = len(x)
    media = np.mean(x)
    s = np.std(x, ddof=1)
    se = s / np.sqrt(n)
    t_crit = stats.t.ppf(1 - alpha/2, df=n-1)
    li = media - t_crit * se
    ls = media + t_crit * se
    return media, se, li, ls

def ic_proporcao(x, alpha=0.05):
    x = np.asarray(x).astype(int)
    n = len(x)
    p_hat = x.mean()
    se = np.sqrt(p_hat*(1-p_hat)/n)
    z = stats.norm.ppf(1 - alpha/2)
    li = p_hat - z*se
    ls = p_hat + z*se
    return p_hat, se, li, ls

# %% [markdown]
# ## 9. ICs principais

# %%
print("\nIC Ticket Médio:", ic_media(df["Total"]))
print("\nIC Atraso Médio:", ic_media(df["delivery_delay_days"]))
print("\nIC Atraso (%) :", ic_proporcao(df["is_late"]))
print("\nIC Cancelamentos (%) :", ic_proporcao((df["Purchase_Status"]=="Cancelado").astype(int)))

# %% [markdown]
# ## 10. Exportar KPIs para o relatório

# %%
kpis_by_service.to_csv("./kpis/kpis_by_service.csv", index=False)
kpis_by_payment.to_csv("./kpis/kpis_by_payment.csv", index=False)
kpis_by_region.to_csv("./kpis/kpis_by_region.csv", index=False)

print("Arquivos exportados para /kpis e figuras para /images.")
