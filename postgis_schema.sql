-- Spatial Operations Platform / PostgreSQL & PostGIS Schema
-- Specification: Blueprint 6 November 2026
-- Standards: OGC SensorThings 1.1, W3C PROV-O, PostGIS 3.0+

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Source Adapters Register
CREATE TABLE IF NOT EXISTS source_adapters (
    source_id VARCHAR(64) PRIMARY KEY,
    provider VARCHAR(128) NOT NULL,
    layer VARCHAR(64) NOT NULL,
    rights_profile VARCHAR(64) NOT NULL,
    data_classification VARCHAR(32) NOT NULL DEFAULT 'COMMERCIAL',
    is_allowlisted BOOLEAN NOT NULL DEFAULT true,
    max_freshness_seconds INTEGER NOT NULL DEFAULT 300,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Evidence History (Bi-temporal partition by tenant & availability)
CREATE TABLE IF NOT EXISTS evidence_history (
    observation_id VARCHAR(128) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    source_id VARCHAR(64) NOT NULL REFERENCES source_adapters(source_id),
    upstream_event_id VARCHAR(128) NOT NULL,
    revision VARCHAR(64),
    root_origin_id VARCHAR(128) NOT NULL,
    subject VARCHAR(64) NOT NULL,
    kind VARCHAR(32) NOT NULL,
    
    -- Multi-clock provenance (OGC SensorThings alignment)
    observed_at TIMESTAMPTZ,
    source_revised_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    first_available_to_tenant_at TIMESTAMPTZ NOT NULL,
    clock_quality VARCHAR(32) NOT NULL DEFAULT 'GPS_SYNC',
    
    -- Geospatial geometry & uncertainty
    geom GEOMETRY(Geometry, 4326),
    error_bound_meters DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    
    -- Cryptographic integrity & retention
    payload_sha256 CHAR(64) NOT NULL,
    raw_payload JSONB NOT NULL,
    is_retracted BOOLEAN NOT NULL DEFAULT false,
    retracted_at TIMESTAMPTZ,
    retraction_reason TEXT,
    
    PRIMARY KEY (tenant_id, observation_id, first_available_to_tenant_at)
) PARTITION BY HASH (tenant_id);

CREATE INDEX IF NOT EXISTS idx_evidence_tenant_avail 
ON evidence_history (tenant_id, first_available_to_tenant_at);

CREATE INDEX IF NOT EXISTS idx_evidence_subject_time 
ON evidence_history (subject, observed_at);

CREATE INDEX IF NOT EXISTS idx_evidence_spatial 
ON evidence_history USING GIST (geom);

-- 3. Versioned Zone Polygons
CREATE TABLE IF NOT EXISTS zones (
    zone_id VARCHAR(64) NOT NULL,
    site VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    PRIMARY KEY (zone_id, version)
);

CREATE INDEX IF NOT EXISTS idx_zones_spatial 
ON zones USING GIST (boundary);

-- 4. Spatial Uncertainty Relation Function
-- Implements: "A boundary intersecting a position’s uncertainty region yields an unresolved spatial relation."
CREATE OR REPLACE FUNCTION evaluate_zone_relation(
    point_geom GEOMETRY,
    error_radius_m DOUBLE PRECISION,
    zone_geom GEOMETRY
) RETURNS VARCHAR(16) AS $$
DECLARE
    dist_to_boundary DOUBLE PRECISION;
    is_inside BOOLEAN;
BEGIN
    IF point_geom IS NULL OR zone_geom IS NULL THEN
        RETURN 'unknown';
    END IF;

    is_inside := ST_Contains(zone_geom, point_geom);
    -- Calculate distance in meters to polygon boundary
    dist_to_boundary := ST_Distance(point_geom::geography, ST_Boundary(zone_geom)::geography);

    -- If uncertainty region intersects the zone boundary
    IF dist_to_boundary < error_radius_m THEN
        RETURN 'unresolved';
    ELSIF is_inside THEN
        RETURN 'inside';
    ELSE
        RETURN 'outside';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 5. Adjudicated Cases & Decision Bundles
CREATE TABLE IF NOT EXISTS cases (
    case_id VARCHAR(128) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    site VARCHAR(64) NOT NULL,
    subject VARCHAR(64) NOT NULL,
    zone_id VARCHAR(64) NOT NULL,
    target_time TIMESTAMPTZ NOT NULL,
    tolerance_seconds INTEGER NOT NULL DEFAULT 5,
    policy_version VARCHAR(64) NOT NULL DEFAULT '2026.11-two-origin-consensus',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS case_decisions (
    decision_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id VARCHAR(128) NOT NULL REFERENCES cases(case_id),
    decision_cutoff TIMESTAMPTZ NOT NULL,
    verdict VARCHAR(32) NOT NULL,
    reason TEXT NOT NULL,
    independent_origins_count INTEGER NOT NULL,
    evidence_bundle_sha256 CHAR(64) NOT NULL,
    exported_bundle JSONB NOT NULL,
    adjudicated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_case_decisions_replay 
ON case_decisions (case_id, decision_cutoff);

-- 6. VectorLink Evidence Requests
-- Specification: "After the operator pilot, let an authorised user request a fresh frame or read-only robot observation through VectorLink."
CREATE TABLE IF NOT EXISTS evidence_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id VARCHAR(128) NOT NULL REFERENCES cases(case_id),
    tenant_id VARCHAR(64) NOT NULL,
    requested_by_user VARCHAR(64) NOT NULL,
    target_asset_or_site VARCHAR(128) NOT NULL,
    purpose TEXT NOT NULL,
    device_clock TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_APPROVAL',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

