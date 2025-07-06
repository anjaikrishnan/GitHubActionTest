-- Sample Data for Enterprise Reporting Platform

-- Create sample business data tables for demonstration
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    sales_rep VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    customer_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(200),
    industry VARCHAR(100),
    region VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    supplier VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample categories
INSERT INTO report_categories (name, description, icon, sort_order) VALUES
('Sales Analytics', 'Reports related to sales performance and trends', 'TrendingUp', 1),
('Financial Reports', 'Financial performance and revenue analysis', 'DollarSign', 2),
('Customer Analytics', 'Customer behavior and segmentation reports', 'Users', 3),
('Product Performance', 'Product sales and inventory reports', 'Package', 4),
('Marketing Metrics', 'Marketing campaign and lead generation reports', 'Target', 5);

-- Insert sample reports
INSERT INTO reports (category_id, name, description, sql_query, chart_config) VALUES
(
    (SELECT id FROM report_categories WHERE name = 'Sales Analytics'),
    'Monthly Sales Trend',
    'Monthly sales revenue trend over the past year',
    'SELECT 
        DATE_TRUNC(''month'', sale_date) as month,
        SUM(total_amount) as revenue,
        COUNT(*) as transactions
     FROM sales_data 
     WHERE sale_date >= CURRENT_DATE - INTERVAL ''12 months''
     GROUP BY DATE_TRUNC(''month'', sale_date)
     ORDER BY month',
    '{"type": "line", "xAxis": "month", "yAxis": "revenue", "title": "Monthly Sales Revenue"}'
),
(
    (SELECT id FROM report_categories WHERE name = 'Sales Analytics'),
    'Sales by Region',
    'Sales performance across different regions',
    'SELECT 
        region,
        SUM(total_amount) as revenue,
        COUNT(*) as transactions,
        AVG(total_amount) as avg_order_value
     FROM sales_data 
     WHERE sale_date >= CURRENT_DATE - INTERVAL ''3 months''
     GROUP BY region
     ORDER BY revenue DESC',
    '{"type": "bar", "xAxis": "region", "yAxis": "revenue", "title": "Sales by Region"}'
),
(
    (SELECT id FROM report_categories WHERE name = 'Sales Analytics'),
    'Top Products',
    'Best selling products by revenue',
    'SELECT 
        product_name,
        SUM(total_amount) as revenue,
        SUM(quantity) as units_sold,
        AVG(unit_price) as avg_price
     FROM sales_data 
     WHERE sale_date >= CURRENT_DATE - INTERVAL ''1 month''
     GROUP BY product_name
     ORDER BY revenue DESC
     LIMIT 10',
    '{"type": "bar", "xAxis": "product_name", "yAxis": "revenue", "title": "Top 10 Products by Revenue"}'
),
(
    (SELECT id FROM report_categories WHERE name = 'Customer Analytics'),
    'Customer Distribution',
    'Customer distribution by industry',
    'SELECT 
        industry,
        COUNT(*) as customer_count,
        AVG(CASE WHEN s.customer_id IS NOT NULL THEN s.total_revenue END) as avg_revenue_per_customer
     FROM customers c
     LEFT JOIN (
         SELECT customer_id, SUM(total_amount) as total_revenue
         FROM sales_data 
         GROUP BY customer_id
     ) s ON c.id = s.customer_id
     GROUP BY industry
     ORDER BY customer_count DESC',
    '{"type": "pie", "dataKey": "customer_count", "nameKey": "industry", "title": "Customers by Industry"}'
),
(
    (SELECT id FROM report_categories WHERE name = 'Financial Reports'),
    'Revenue Summary',
    'Overall revenue summary and key metrics',
    'SELECT 
        ''Total Revenue'' as metric,
        SUM(total_amount) as value
     FROM sales_data
     UNION ALL
     SELECT 
        ''Average Order Value'' as metric,
        AVG(total_amount) as value
     FROM sales_data
     UNION ALL
     SELECT 
        ''Total Transactions'' as metric,
        COUNT(*) as value
     FROM sales_data',
    '{"type": "metric", "title": "Key Business Metrics"}'
);

-- Insert sample customers
INSERT INTO customers (customer_name, email, company, industry, region) VALUES
('John Smith', 'john.smith@techcorp.com', 'TechCorp Inc', 'Technology', 'North America'),
('Sarah Johnson', 'sarah.j@retailplus.com', 'RetailPlus', 'Retail', 'Europe'),
('Mike Chen', 'mike.chen@manufacturing.com', 'Manufacturing Co', 'Manufacturing', 'Asia'),
('Emma Wilson', 'emma.w@healthcare.com', 'HealthCare Ltd', 'Healthcare', 'North America'),
('Carlos Rodriguez', 'carlos.r@finance.com', 'Finance Group', 'Financial Services', 'South America');

-- Insert sample products
INSERT INTO products (product_name, category, price, cost, supplier) VALUES
('Laptop Pro 15"', 'Electronics', 1299.99, 899.99, 'Tech Supplier A'),
('Wireless Mouse', 'Electronics', 49.99, 25.99, 'Tech Supplier B'),
('Office Chair', 'Furniture', 299.99, 199.99, 'Furniture Supplier A'),
('Standing Desk', 'Furniture', 599.99, 399.99, 'Furniture Supplier A'),
('Monitor 27"', 'Electronics', 349.99, 229.99, 'Tech Supplier A');

-- Generate sample sales data
INSERT INTO sales_data (sale_date, product_name, category, region, sales_rep, quantity, unit_price, total_amount, customer_id)
SELECT 
    CURRENT_DATE - (random() * 365)::integer,
    p.product_name,
    p.category,
    (ARRAY['North America', 'Europe', 'Asia', 'South America'])[ceil(random() * 4)],
    (ARRAY['Alice Cooper', 'Bob Johnson', 'Charlie Brown', 'Diana Prince'])[ceil(random() * 4)],
    ceil(random() * 10)::integer,
    p.price,
    p.price * ceil(random() * 10)::integer,
    c.id
FROM 
    products p,
    customers c,
    generate_series(1, 1000) as series
WHERE 
    random() < 0.2; -- 20% chance to create a sale record

-- Insert sample data source
INSERT INTO data_sources (name, type, connection_string) VALUES
('Primary Database', 'postgres', 'postgresql://postgres:postgres123@postgres:5432/enterprise_reporting');

-- Create a default admin user (will be updated when Keycloak sync happens)
INSERT INTO users (keycloak_id, username, email, first_name, last_name) VALUES
('admin-temp-id', 'admin', 'admin@company.com', 'System', 'Administrator');