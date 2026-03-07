-- Create the second database
CREATE DATABASE "export_intel";

-- Switch to it
\connect "export-intel";

-- Now create your schema inside export-intel

-- CREATE TABLE countries (
--     id SERIAL PRIMARY KEY,
--     name TEXT UNIQUE
-- );

-- CREATE TABLE products (
--     id SERIAL PRIMARY KEY,
--     hs_code TEXT UNIQUE,
--     description TEXT
-- );

-- CREATE TABLE trade_raw (
--     id SERIAL PRIMARY KEY,
--     country_id INT REFERENCES countries(id),
--     product_id INT REFERENCES products(id),
--     year INT,
--     import_value_usd NUMERIC
-- );

-- CREATE TABLE market_intelligence (
--     id SERIAL PRIMARY KEY,
--     country_id INT REFERENCES countries(id),
--     product_id INT REFERENCES products(id),
--     avg_growth_5y NUMERIC,
--     volatility NUMERIC,
--     total_import NUMERIC,
--     opportunity_score NUMERIC,
--     ai_summary TEXT
-- );

CREATE TABLE trade_raw (
    id SERIAL PRIMARY KEY,
    country TEXT,
    hs_code TEXT,
    year INT,
    import_value_usd NUMERIC
);

CREATE TABLE market_intelligence (
    id SERIAL PRIMARY KEY,
    country TEXT,
    hs_code TEXT,
    avg_growth_5y NUMERIC,
    volatility NUMERIC,
    total_import NUMERIC,
    opportunity_score NUMERIC,
    ai_summary TEXT
);

DROP TABLE IF EXISTS country_risk;

CREATE TABLE country_risk (
    country TEXT PRIMARY KEY,
    stability_index NUMERIC,
    risk_score NUMERIC
);