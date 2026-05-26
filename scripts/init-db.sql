"""
scripts/init-db.sql — PostgreSQL + TimescaleDB Schema Initialization
====================================================================
Creates tables for operational events, findings, telemetry, and compliance data.
"""

-- Create extensions
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    mission_goal TEXT,
    target_scope TEXT,
    intensity_level INT,
    status TEXT DEFAULT 'active',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Operational events (hypertable for time-series data)
CREATE TABLE IF NOT EXISTS operational_events (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    session_id UUID REFERENCES sessions(session_id),
    trace_id UUID NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    exception JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

SELECT create_hypertable(
    'operational_events',
    'time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_operational_events_session_id
    ON operational_events (session_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_operational_events_trace_id
    ON operational_events (trace_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_operational_events_level
    ON operational_events (level, time DESC);

-- Findings table
CREATE TABLE IF NOT EXISTS findings (
    finding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id),
    trace_id UUID NOT NULL,
    target_ip INET NOT NULL,
    target_port INT,
    cve_id TEXT,
    cwe_id TEXT,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    cvss_score FLOAT,
    evidence TEXT,
    remediation TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_findings_session_id
    ON findings (session_id);
CREATE INDEX IF NOT EXISTS idx_findings_cve_id
    ON findings (cve_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity
    ON findings (severity);
CREATE INDEX IF NOT EXISTS idx_findings_target_ip
    ON findings (target_ip);

-- Discovery results table
CREATE TABLE IF NOT EXISTS discovery_results (
    discovery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id),
    ip INET NOT NULL,
    hostname TEXT,
    mac_address MACADDR,
    open_ports INT[],
    os_guess TEXT,
    tags TEXT[],
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_discovery_results_session_id
    ON discovery_results (session_id);
CREATE INDEX IF NOT EXISTS idx_discovery_results_ip
    ON discovery_results (ip);

-- Service fingerprints table
CREATE TABLE IF NOT EXISTS service_fingerprints (
    fingerprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discovery_id UUID REFERENCES discovery_results(discovery_id),
    port INT NOT NULL,
    protocol TEXT NOT NULL,
    service_name TEXT,
    product TEXT,
    version TEXT,
    cpe TEXT[],
    banners JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_service_fingerprints_discovery_id
    ON service_fingerprints (discovery_id);
CREATE INDEX IF NOT EXISTS idx_service_fingerprints_port
    ON service_fingerprints (port);

-- Compliance controls mapping
CREATE TABLE IF NOT EXISTS compliance_controls (
    control_id TEXT PRIMARY KEY,
    framework TEXT NOT NULL,
    control_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance report mapping table
CREATE TABLE IF NOT EXISTS compliance_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id),
    framework TEXT NOT NULL,
    control_id TEXT REFERENCES compliance_controls(control_id),
    status TEXT NOT NULL,
    related_findings INT DEFAULT 0,
    gap_description TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_compliance_reports_session_id
    ON compliance_reports (session_id);
CREATE INDEX IF NOT EXISTS idx_compliance_reports_framework
    ON compliance_reports (framework);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO acosp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO acosp;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO acosp;
