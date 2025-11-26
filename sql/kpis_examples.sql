SELECT
    payment,
    COUNT(*)                    AS orders,
    AVG(Total)                  AS avg_ticket,
    AVG(Discount)               AS avg_discount,
    AVG(CASE WHEN Purchase_Status = 'Confirmado' THEN 1 ELSE 0 END) AS confirm_rate
FROM vw_ecommerce_analytic
GROUP BY payment;
SELECT
    Services,
    COUNT(*) AS orders,
    AVG(delivery_lead_time)     AS avg_lead_time,
    AVG(delivery_delay_days)    AS avg_delay,
    AVG(is_late)                AS late_rate,
    AVG(CASE WHEN Purchase_Status = 'Cancelado' THEN 1 ELSE 0 END) AS cancel_rate,
    AVG(freight_share)          AS freight_share_mean
FROM vw_ecommerce_analytic
GROUP BY Services;
SELECT
    DATE_TRUNC('month', Order_Date) AS month,
    Region,
    SUM(Total)                      AS revenue,
    COUNT(*)                        AS orders,
    AVG(is_late)                    AS late_rate
FROM vw_ecommerce_analytic
GROUP BY DATE_TRUNC('month', Order_Date), Region
ORDER BY month, Region;
SELECT
    Category,
    Subcategory,
    COUNT(*) AS orders,
    SUM(Total) AS revenue,
    AVG(Total) AS avg_ticket,
    AVG(Discount) AS avg_discount
FROM vw_ecommerce_analytic
GROUP BY Category, Subcategory
ORDER BY revenue DESC;
