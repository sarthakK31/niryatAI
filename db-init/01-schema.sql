-- ============================================
-- Niryat AI - Database Schema
-- ============================================

-- =========================
-- USERS & AUTH
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    company_name TEXT,
    hs_codes TEXT[],                -- products they export/want to export
    state TEXT,                     -- Indian state
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================
-- TRADE & MARKET INTELLIGENCE (existing)
-- =========================
CREATE TABLE IF NOT EXISTS trade_raw (
    id SERIAL PRIMARY KEY,
    country TEXT,
    hs_code TEXT,
    year INT,
    import_value_usd NUMERIC
);

CREATE TABLE IF NOT EXISTS market_intelligence (
    id SERIAL PRIMARY KEY,
    country TEXT,
    hs_code TEXT,
    avg_growth_5y NUMERIC,
    volatility NUMERIC,
    total_import NUMERIC,
    opportunity_score NUMERIC,
    ai_summary TEXT
);

CREATE TABLE IF NOT EXISTS country_risk (
    country TEXT PRIMARY KEY,
    stability_index NUMERIC,
    risk_score NUMERIC
);

-- Index for fast market queries
CREATE INDEX IF NOT EXISTS idx_mi_hs_code ON market_intelligence(hs_code);
CREATE INDEX IF NOT EXISTS idx_mi_country ON market_intelligence(country);
CREATE INDEX IF NOT EXISTS idx_mi_opportunity ON market_intelligence(opportunity_score DESC);

-- =========================
-- EXPORT READINESS TRACKING
-- =========================
CREATE TABLE IF NOT EXISTS export_steps (
    id SERIAL PRIMARY KEY,
    step_number INT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT                   -- e.g. 'registration', 'compliance', 'logistics'
);

CREATE TABLE IF NOT EXISTS export_substeps (
    id SERIAL PRIMARY KEY,
    step_id INT REFERENCES export_steps(id) ON DELETE CASCADE,
    substep_number INT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    help_doc_s3_key TEXT           -- link to S3 document for guidance
);

CREATE TABLE IF NOT EXISTS user_readiness (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    substep_id INT REFERENCES export_substeps(id),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    UNIQUE(user_id, substep_id)
);

-- =========================
-- CHAT PERSISTENCE
-- =========================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    image_description TEXT,         -- if user sent an image, store extracted text
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id, updated_at DESC);

-- =========================
-- SEED: EXPORT READINESS STEPS
-- =========================
INSERT INTO export_steps (step_number, title, description, category) VALUES
(1, 'Business Registration', 'Register your business entity and obtain necessary identifiers', 'registration'),
(2, 'IEC Registration', 'Obtain Import Export Code from DGFT', 'registration'),
(3, 'RCMC Registration', 'Register with relevant Export Promotion Council and get RCMC', 'registration'),
(4, 'Product Classification', 'Identify correct HS code and comply with product standards', 'compliance'),
(5, 'Market Research', 'Identify target markets using trade intelligence data', 'research'),
(6, 'Buyer Discovery', 'Find and connect with international buyers', 'research'),
(7, 'Export Documentation', 'Prepare commercial invoice, packing list, and shipping bill', 'documentation'),
(8, 'Quality & Compliance', 'Obtain required quality certifications and meet importing country standards', 'compliance'),
(9, 'Logistics Setup', 'Set up freight forwarding, customs broker, and shipping', 'logistics'),
(10, 'Payment & Banking', 'Set up FEMA-compliant banking for export payments', 'finance')
ON CONFLICT DO NOTHING;

INSERT INTO export_substeps (step_id, substep_number, title, description) VALUES
-- Step 1: Business Registration
(1, 1, 'Register with GST', 'Obtain GSTIN for your business'),
(1, 2, 'PAN for business', 'Ensure business PAN card is available'),
(1, 3, 'Open current account', 'Open a current bank account in business name'),
-- Step 2: IEC
(2, 1, 'Apply on DGFT portal', 'Visit dgft.gov.in and apply for IEC'),
(2, 2, 'Upload documents', 'Upload PAN, address proof, bank details'),
(2, 3, 'Receive IEC certificate', 'Download IEC certificate after approval'),
-- Step 3: RCMC
(3, 1, 'Identify Export Promotion Council', 'Find the relevant EPC for your product category'),
(3, 2, 'Apply for RCMC', 'Register and apply through the council portal'),
(3, 3, 'Receive RCMC', 'Get your Registration cum Membership Certificate'),
-- Step 4: Product Classification
(4, 1, 'Identify HS Code', 'Find the correct 6-8 digit HS code for your product'),
(4, 2, 'Check product standards', 'Verify BIS, FSSAI, or other applicable standards'),
(4, 3, 'Check destination regulations', 'Verify importing country product requirements'),
-- Step 5: Market Research
(5, 1, 'Analyze trade data', 'Use Niryat AI to find best markets for your HS code'),
(5, 2, 'Review country risk', 'Assess political and economic stability of target markets'),
(5, 3, 'Shortlist target markets', 'Select 3-5 priority export destinations'),
-- Step 6: Buyer Discovery
(6, 1, 'Register on trade portals', 'Create profiles on IndiaMART, TradeIndia, Alibaba'),
(6, 2, 'Contact Indian embassy trade desk', 'Reach out to embassy commercial sections'),
-- Step 7: Export Documentation
(7, 1, 'Prepare commercial invoice', 'Create export invoice with all required fields'),
(7, 2, 'Create packing list', 'Detailed packing list matching the invoice'),
(7, 3, 'File shipping bill', 'File shipping bill through ICEGATE'),
(7, 4, 'Obtain certificate of origin', 'Get CoO from chamber of commerce if needed'),
-- Step 8: Quality & Compliance
(8, 1, 'Get product tested', 'Get product tested at NABL accredited lab'),
(8, 2, 'Obtain quality certificate', 'Get ISO or relevant quality certification'),
(8, 3, 'Check labeling requirements', 'Ensure packaging meets destination country labeling rules'),
-- Step 9: Logistics
(9, 1, 'Appoint customs broker', 'Hire a licensed customs house agent'),
(9, 2, 'Choose freight forwarder', 'Select a reliable freight forwarding partner'),
(9, 3, 'Arrange cargo insurance', 'Get marine cargo insurance for shipment'),
-- Step 10: Payment & Banking
(10, 1, 'Understand FEMA guidelines', 'Learn RBI/FEMA rules for export payments'),
(10, 2, 'Set up AD bank account', 'Ensure your bank is authorized dealer for forex'),
(10, 3, 'Choose payment terms', 'Decide between LC, TT, DP, DA etc.')
ON CONFLICT DO NOTHING;


-- HS CODE MAPPING TABLE:

CREATE TABLE hs_code_reference (
    id SERIAL PRIMARY KEY,
    hs_code TEXT UNIQUE NOT NULL,
    product_description TEXT,
    india_hs_code TEXT,
    usa_hts_code TEXT,
    eu_cn_code TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


CREATE INDEX idx_hs_reference_code ON hs_code_reference(hs_code);
CREATE INDEX idx_hs_india ON hs_code_reference(india_hs_code);
CREATE INDEX idx_hs_usa ON hs_code_reference(usa_hts_code);
