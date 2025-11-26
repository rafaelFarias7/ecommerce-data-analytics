# 📦 *README.md — Ecommerce Data Analytics Pipeline*

# 📊 Ecommerce Data Analytics Pipeline  
### Análise exploratória, inferência estatística e KPIs para um e-commerce brasileiro

![Status](https://img.shields.io/badge/Project-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pandas](https://img.shields.io/badge/Library-Pandas-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📘 Sobre o Projeto

Este projeto apresenta um **pipeline completo de análise de dados para um e-commerce brasileiro**, integrando:

- **Data Cleaning & Data Quality Assessment**
- **Modelagem dimensional estilo Star Schema**
- **Feature Engineering**
- **Análise Exploratória de Dados (EDA)**
- **Inferência Estatística (médias, proporções, ICs)**
- **Construção de KPIs operacionais e comerciais**
- **Sazonalidade, comportamento de cliente e performance logística**

O objetivo é fornecer um **relatório analítico consistente**, com **tratamento estatístico robusto**, capaz de apoiar decisões da diretoria nas áreas de:

- Receita  
- Margem  
- Frete  
- Logística / SLA  
- Conversão  
- Experiência do cliente  

---

## 🗂 Estrutura do Repositório

```
.
├── data/
│   ├── DIM_Customer.csv
│   ├── DIM_Products.csv
│   ├── DIM_Delivery.csv
│   ├── FACT_Orders.csv
│   └── DIM_Shopping.csv
│
├── notebooks/
│   ├── ecommerce_analysis.ipynb
│   └── ecommerce_analysis.py
│
├── reports/
│   └── Ecommerce_Analytics_Report.md
│
├── kpis/
│   ├── kpis_by_service.csv
│   ├── kpis_by_payment.csv
│   ├── kpis_by_region.csv
│   ├── kpis_by_category.csv
│   ├── elasticity_discount.csv
│   ├── seasonality_month_region.csv
│   └── fact_analytic_clean.csv
│
├── images/
│   ├── hist_ticket.png
│   ├── hist_leadtime.png
│   ├── hist_delay.png
│   ├── hist_discount.png
│   ├── box_ticket.png
│   ├── box_leadtime.png
│   ├── box_discount.png
│   └── correlacao.png
│
├── sql/
│   ├── model_joins.sql
│   └── kpis_examples.sql
│
└── README.md

```

---

## 🚀 Como Executar o Projeto

### **1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/ecommerce-data-analytics-pipeline.git
cd ecommerce-data-analytics-pipeline
````

---

### **2. Crie e ative um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

---

### **3. Instale as dependências**

```bash
pip install -r requirements.txt
```

---

### **4. Execute o notebook**

Abra:

```
notebooks/ecommerce_analysis.ipynb
```

ou rode o script equivalente:

```bash
python notebooks/ecommerce_analysis.py
```

---

## 🧠 Principais Análises & Métricas

### ✔ Data Quality

* Tipos de dados corrigidos (datas em `datetime`, numéricos em `float/int`)
* Datas padronizadas (`Order_Date`, `D_Date`, `D_Forecast`)
* Trimming em colunas de texto
* Remoção de nulos críticos em datas e valores financeiros
* Verificação de unicidade por pedido (`Id`) e remoção de duplicados em `FACT_Orders`
* Checagem de integridade de chaves entre fato e dimensões
* Detecção de outliers por regra do IQR (documentados e filtrados em `df_clean`)
* Chave central `Id` unificando tabelas

---

### ✔ Feature Engineering

Variáveis derivadas:

* `delivery_delay_days`
* `delivery_lead_time`
* `is_late`
* `is_confirmed`
* `freight_share`
* `discount_abs`

---

### ✔ KPIs Produzidos

#### **Operacionais**

* Atraso médio
* Lead time médio
* % de entregas atrasadas
* Performance logística por Service (Standard, Same-Day, Scheduled)

#### **Comerciais**

* Ticket médio (global e por método de pagamento / região / categoria)
* Conversão por método de pagamento (PIX, crédito, boleto…)
* Desconto médio e faixas de desconto
* Mix de produtos por Category/Subcategory e elasticidade aproximada vs desconto

#### **Sazonalidade**

* Receita por mês e região (`seasonality_month_region.csv`)
* Demandas por região/UF
* Volume mensal por canal (se derivado de `DIM_Shopping`)

---

## 📈 Resultados Relevantes (Resumo)

* **83% das entregas atrasadas** → desalinhamento entre previsão e capacidade operacional.
* **PIX tem maior conversão e maior ticket médio** → forte oportunidade comercial.
* **Cancelamentos em ~26%** → otimizar checkout, antifraude e comunicação.
* **Same-Day cobra frete alto, mas entrega com alto atraso** → revisão de SLA recomendada.

---

## 📜 Inferência Estatística

O notebook inclui:

* IC 95% para ticket médio (baseado em `df_clean` — sem outliers extremos)
* IC 95% para atraso médio
* IC 95% para proporção de atrasos e cancelamentos
* ICs por *payment* e *service* (via agregações utilizadas em CSV/Power BI)
* Verificação de normalidade (Shapiro–Wilk) e independência (autocorrelação lag-1)

---

## 🏗 Tecnologias Utilizadas

* **Python 3.10+**
* **Pandas**
* **NumPy**
* **Matplotlib**
* **SciPy**
* **Jupyter Notebook**

---

## 🙋 Autores

- **Rafael Farias**  
- **Victor Simas**  
- **Julio Bezerra**  

---

## 📄 Licença

Este projeto está sob a licença MIT – veja `LICENSE` para detalhes.

---

## ⭐ Contribua!

Pull Requests são bem-vindos. Crie uma *issue* se tiver sugestões ou melhorias.