from db import run_query

# ===============================
# COURIER QUERIES
# ===============================
def get_top_couriers(limit=10):
    """
    Fetch top couriers with key metrics.
    limit: number of couriers to return
    """
    query = f"""
    SELECT 
        c.name AS courier_name,
        COUNT(s.shipment_id) AS Shipments_handled,
        ROUND(AVG(TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date)),2) AS Avg_delivery_hours,
        ROUND(100.0*(SUM(CASE WHEN TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) <= r.avg_time_hours THEN 1 ELSE 0 END)/COUNT(*)),2) AS On_Time_Delivery,
        ROUND(AVG(co.fuel_cost+co.misc_cost+co.labor_cost),2) AS Avg_cost_per_shipment,
        c.rating as Rating
    FROM shipments s
    JOIN courier_staff c ON s.courier_id=c.courier_id
    JOIN routes r ON s.route_key=r.route_key
    JOIN costs co ON s.shipment_key=co.shipment_key
    WHERE s.status='Delivered'
    GROUP BY c.name, c.rating
    ORDER BY Shipments_handled DESC,
        Avg_delivery_hours ASC,
        On_Time_Delivery DESC,
        c.rating DESC
    LIMIT {limit};
    """
    return run_query(query)
# -------------------------------
# Shipment Tracking Search QuERY
# -------------------------------
shipment_search_query= """
SELECT s.shipment_id,s.status,s.order_date,s.delivery_date,
    c.name as courier_name,r.origin,r.destination
FROM shipments s
LEFT JOIN courier_staff c ON s.courier_id=c.courier_id
LEFT JOIN routes r ON s.route_key=r.route_key
WHERE s.shipment_id = :shipment_id ;
"""

#Fetch tracking History
tracking_query="""
SELECT status,timestamp
FROM shipment_tracking 
WHERE shipment_key = (SELECT shipment_key FROM shipments WHERE shipment_id = :shipment_id)
ORDER BY `timestamp` ASC;
"""

# ===============================
# CORE KPIs HOMEPAGE
# ===============================
kpi_query = """
SELECT COUNT(*) AS total_shipments,
SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_count,
SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM shipments;
"""

pending_query="""
    SELECT COUNT(*) AS pending_shipments
    FROM shipments
    WHERE status NOT IN ('Delivered','Cancelled');
"""

active_couriers_query="""
    SELECT COUNT(DISTINCT courier_id) As active_couriers
    FROM shipments
    WHERE status != 'Cancelled';
"""
# ==========================
# DELIVERY PERFORMANCE KPIs
# ==========================
avg_pickup_query="""
    SELECT AVG(DATEDIFF(tr.timestamp,s.order_date)) AS avg_pickup_days
    FROM shipments s
    JOIN shipment_tracking tr ON s.shipment_key=tr.shipment_key
    WHERE tr.status='Picked Up';
"""

avg_delivery_query="""
    SELECT AVG(DATEDIFF(delivery_date,order_date)) AS avg_delivery_days
    FROM shipments
    WHERE status='Delivered';
"""
delayed_query="""
    SELECT COUNT(*) AS delayed_shipments
    FROM shipments s
    JOIN routes r ON s.route_key=r.route_key
    WHERE s.status='Delivered' 
    AND TIMESTAMPDIFF(HOUR,s.order_date,s.delivery_date)>r.avg_time_hours;
"""

# ===============================
# LEFT COLUMN: Operational Leaders
# ===============================
top_warehouse_query = """
SELECT
    w.city as warehouse_city,
    w.state,
    w.capacity,
-- Volume
COUNT(s.shipment_id) AS shipments_handled,
-- Dispatch speed: Order Placed → Picked Up (from tracking)
ROUND(AVG(TIMESTAMPDIFF(HOUR, op.timestamp, pu.timestamp)), 2) AS avg_dispatch_hours,
-- Capacity utilization: shipments handled vs warehouse capacity
ROUND(100* COUNT(s.shipment_id) / w.capacity, 2) AS capacity_utilization_pct
FROM shipments s
JOIN warehouses w ON s.origin_warehouse_key = w.warehouse_key
LEFT JOIN shipment_tracking op ON op.shipment_key = s.shipment_key
                                AND op.status = 'Order Placed'
LEFT JOIN shipment_tracking pu ON pu.shipment_key = s.shipment_key
                                AND pu.status = 'Picked Up'
WHERE s.status = 'Delivered'
GROUP BY 
    w.warehouse_key,
    w.city,
    w.state,
    w.capacity
ORDER BY
    shipments_handled DESC,
    avg_dispatch_hours ASC,
    capacity_utilization_pct DESC
LIMIT 1;
"""

best_vehicle_query = """
SELECT 
    c.vehicle_type,
    COUNT(s.shipment_id) AS shipments_handled
FROM shipments s
JOIN courier_staff c ON s.courier_id = c.courier_id
WHERE s.status = 'Delivered'
GROUP BY c.vehicle_type
ORDER BY shipments_handled DESC
LIMIT 1;
"""
# ===============================
# RIGHT COLUMN: Business Leaders
# ===============================
top_origin_query = """
SELECT 
    w.city AS city, 
    COUNT(*) AS total_orders
FROM shipments s
JOIN warehouses w ON s.origin_warehouse_key=w.warehouse_key
GROUP BY w.city
ORDER BY total_orders DESC
LIMIT 1;
"""

top_dest_query = """
SELECT 
    w.city AS city, 
    COUNT(*) AS total_delivered
FROM shipments s
JOIN warehouses w ON s.destination_warehouse_key=w.warehouse_key
WHERE status='Delivered'
GROUP BY w.city
ORDER BY total_delivered DESC
LIMIT 1;
"""

best_month_query = """
SELECT 
    DATE_FORMAT(order_date,'%Y-%m') AS month, 
    COUNT(*) AS total_orders
FROM shipments
GROUP BY month
ORDER BY total_orders DESC
LIMIT 1;
"""
# ===============================
# SHIPPING TRENDS CHART
# ===============================
shipping_trends_query = """
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN status='Delivered' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status NOT IN ('Delivered','Cancelled') THEN 1 ELSE 0 END) AS in_transit
FROM shipments
GROUP BY month
ORDER BY month;
"""
# ================
# TOTAL WAREHOUSES 
# ================
warehouse_count_query="""
SELECT 
    COUNT(*) AS warehouse_count
FROM warehouses;
"""
# ========================
# AVG CAPACITY UTILISATION 
# ========================
avg_utilization_query="""
SELECT ROUND(AVG(utilization_pct),2) AS avg_capacity_utilization
FROM (
    SELECT 
        w.warehouse_key,
        (COUNT(s.shipment_id) / w.capacity) * 100 AS utilization_pct
    FROM warehouses w
    LEFT JOIN shipments s 
        ON s.origin_warehouse_key = w.warehouse_key
    GROUP BY w.warehouse_key, w.capacity
) warehouse_utilization;
"""
# ==================
# AVG DISPATCH TIME 
# ==================
avg_dispatch_query="""
SELECT 
    ROUND(AVG(TIMESTAMPDIFF(HOUR, op.timestamp, pu.timestamp)),2) 
    AS avg_dispatch_hours
FROM shipments s
JOIN shipment_tracking op 
    ON op.shipment_key = s.shipment_key 
    AND op.status='Order Placed'
JOIN shipment_tracking pu 
    ON pu.shipment_key = s.shipment_key 
    AND pu.status='Picked Up';
"""
# ===============
# CANCELLATIONS
# ===============
cancel_query="""
SELECT 
    w.city AS warehouse_city,
    COUNT(s.shipment_id) AS total_shipments,
    SUM(CASE WHEN s.status='Cancelled' THEN 1 ELSE 0 END) AS cancelled_shipments,
    ROUND(
        100 * SUM(CASE WHEN s.status='Cancelled' THEN 1 ELSE 0 END) 
        / COUNT(s.shipment_id), 
    2) AS cancellation_rate_pct
FROM shipments s
JOIN warehouses w 
    ON s.origin_warehouse_key = w.warehouse_key
GROUP BY w.city
ORDER BY cancellation_rate_pct DESC;
"""
# =======================
# WAREHOUSE LOAD ANALYSIS
# =======================
warehouse_load_query = """
SELECT 
    w.city AS warehouse_city,
    COUNT(*) AS total_shipments
FROM shipments s
JOIN warehouses w ON s.origin_warehouse_key = w.warehouse_key
GROUP BY w.city
ORDER BY total_shipments DESC;
"""
# ====================================
# CONTRIBUTION TO TOTAL NETWORK DELAYS 
# ====================================
delayed_shipments_by_city_query = """
WITH city_delays AS (
    SELECT 
        w.city,
        COUNT(*) AS delayed_shipments
    FROM shipments s
    JOIN warehouses w 
        ON s.origin_warehouse_key = w.warehouse_key
    JOIN routes r 
        ON s.route_key = r.route_key
    WHERE s.status = 'Delivered'
      AND TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) > r.avg_time_hours
    GROUP BY w.city
),
total_delays AS (
    SELECT COUNT(*) AS total_delayed
    FROM shipments s
    JOIN routes r 
        ON s.route_key = r.route_key
    WHERE s.status = 'Delivered'
      AND TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) > r.avg_time_hours
)
SELECT 
    cd.city,
    cd.delayed_shipments,
    ROUND(
        100 * cd.delayed_shipments / NULLIF(td.total_delayed, 0),
        2
    ) AS contribution_to_total_delays_pct
FROM city_delays cd
CROSS JOIN total_delays td
ORDER BY contribution_to_total_delays_pct DESC;
"""
# ==============================
# WAREHOUSE CAPACITY COMPARISON 
# ==============================
warehouse_capacity_query = """
SELECT 
    w.city AS warehouse_city,
    w.capacity AS total_capacity,
    COUNT(s.shipment_id) AS shipments_handled,
    ROUND(100 * COUNT(s.shipment_id) / w.capacity, 2) AS capacity_utilization_pct
FROM warehouses w
LEFT JOIN shipments s ON s.origin_warehouse_key = w.warehouse_key
GROUP BY w.city, w.capacity
ORDER BY capacity_utilization_pct DESC;
"""
# ============================
#  ROUTE ANALYTICS
# ============================
route_query = """
    SELECT 
        r.route_key,
        CONCAT(r.origin, ' → ', r.destination) AS route_name,
        r.distance_km,
        r.avg_time_hours AS planned_transit_hours,
        COUNT(s.shipment_id) AS total_shipments,
        ROUND(AVG(TIMESTAMPDIFF(HOUR, pu.timestamp, s.delivery_date)), 2) AS avg_transit_hours,
    SUM(
        CASE 
            WHEN TIMESTAMPDIFF(HOUR, pu.timestamp, s.delivery_date) > r.avg_time_hours 
            THEN 1 
            ELSE 0 
        END
    ) AS route_delayed_shipments,
    ROUND(
        100 * SUM(
            CASE 
                WHEN TIMESTAMPDIFF(HOUR, pu.timestamp, s.delivery_date) > r.avg_time_hours 
                THEN 1 ELSE 0 
            END
        ) / COUNT(s.shipment_id),
        2
    ) AS route_delay_pct
    FROM shipments s
    JOIN routes r ON s.route_key=r.route_key
    LEFT JOIN shipment_tracking pu 
        ON pu.shipment_key = s.shipment_key
        AND pu.status = 'Picked Up'
    WHERE 
        s.status = 'Delivered'
        AND pu.timestamp IS NOT NULL
    GROUP BY r.route_key, r.origin, r.destination, r.distance_km, r.avg_time_hours
    ORDER BY total_shipments DESC;
    """
# =================
#   COST ANALYTICS
# =================
cost_metrics_query = """
SELECT 
    r.route_key,
    CONCAT(r.origin, ' → ', r.destination) AS route_name,
    r.distance_km,

    COUNT(s.shipment_id) AS total_shipments,

    SUM(c.fuel_cost + c.labor_cost + c.misc_cost) AS total_cost,

    ROUND(
        SUM(c.fuel_cost + c.labor_cost + c.misc_cost) 
        / COUNT(s.shipment_id), 2
    ) AS avg_cost_per_shipment,

    ROUND(
        SUM(c.fuel_cost + c.labor_cost + c.misc_cost)
        / SUM(r.distance_km), 2
    ) AS cost_per_km

FROM shipments s

JOIN costs c 
    ON s.shipment_key = c.shipment_key

JOIN routes r 
    ON s.route_key = r.route_key

WHERE s.status = 'Delivered'

GROUP BY 
    r.route_key,
    r.origin,
    r.destination,
    r.distance_km

ORDER BY total_cost DESC;
"""
# ================
# COSTS BREAKDOWN
# ================
cost_query = """
    SELECT 
    s.shipment_id,
    r.route_key,
    CONCAT(r.origin, ' → ', r.destination) AS route_name,  -- keep AS route_name
    r.distance_km,
    COUNT(s.shipment_id) AS total_shipments,
    SUM(c.fuel_cost + c.labor_cost + c.misc_cost) AS total_cost,
    SUM(c.fuel_cost) AS fuel,
    SUM(c.labor_cost) AS labor,
    SUM(c.misc_cost) AS misc
FROM shipments s
JOIN costs c ON s.shipment_key = c.shipment_key
JOIN routes r ON s.route_key = r.route_key
WHERE s.status='Delivered'
GROUP BY r.route_key, r.origin, r.destination, r.distance_km,s.shipment_id
ORDER BY total_cost DESC;
"""

# ===================
# COURIER ANALYTICS
# ===================
courier_performance_query= """
SELECT 
    c.courier_id,
    c.name AS courier_name,
    COUNT(s.shipment_id) AS total_shipments,
    SUM(CASE WHEN TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) <= r.avg_time_hours THEN 1 ELSE 0 END) AS on_time_shipments,
    ROUND(100.0 * SUM(CASE WHEN TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) <= r.avg_time_hours THEN 1 ELSE 0 END) / COUNT(s.shipment_id), 2) AS on_time_pct
FROM shipments s
JOIN courier_staff c ON s.courier_id = c.courier_id
JOIN routes r ON s.route_key = r.route_key
WHERE s.status = 'Delivered'
GROUP BY c.courier_id, c.name
ORDER BY total_shipments DESC;
"""
# ==============================
# SHIPMENT COUNT VS VEHICLE TYPE
# ==============================
vehicle_query="""
SELECT 
    c.vehicle_type,
    COUNT(s.shipment_id) AS shipments_handled,
    ROUND(AVG(TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date)),2) AS avg_delivery_hours,
    ROUND(100 * SUM(CASE WHEN TIMESTAMPDIFF(HOUR, s.order_date, s.delivery_date) <= r.avg_time_hours THEN 1 ELSE 0 END)/COUNT(*),2) AS on_time_pct
FROM shipments s
JOIN courier_staff c ON s.courier_id = c.courier_id
JOIN routes r ON s.route_key = r.route_key
WHERE s.status='Delivered'
GROUP BY c.vehicle_type
ORDER BY shipments_handled DESC;
"""




