CREATE OR REPLACE VIEW vw_ecommerce_analytic AS
SELECT
    f.Id,
    f.Order_Date,
    f.Subtotal,
    f.Total,
    f.P_Sevice,
    f.Discount,
    f.Purchase_Status,
    f.payment,
    d.D_Date,
    d.D_Forecast,
    d.Services,
    c.Customer_Id,
    c.State,
    c.Region,
    p.Category,
    p.Subcategory,
    DATE_PART('day', d.D_Date   - d.D_Forecast) AS delivery_delay_days,
    DATE_PART('day', d.D_Date   - f.Order_Date) AS delivery_lead_time,
    CASE WHEN d.D_Date > d.D_Forecast THEN 1 ELSE 0 END AS is_late,
    CASE WHEN f.Purchase_Status = 'Confirmado' THEN 1 ELSE 0 END AS is_confirmed,
    CASE WHEN f.Total <> 0 THEN f.P_Sevice / f.Total ELSE NULL END AS freight_share,
    (f.Discount * f.Subtotal) AS discount_abs
FROM FACT_Orders   f
LEFT JOIN DIM_Delivery d ON f.Id = d.Id
LEFT JOIN DIM_Customer c ON f.Id = c.Id
LEFT JOIN DIM_Products p ON f.Id = p.Id;


