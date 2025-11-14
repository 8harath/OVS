-- Migration: Add Blockchain Integration Tables
-- Phase 1: Proof of Concept
-- Date: 2025-11-14
-- Description: Add tables to link traditional database with blockchain records

-- Table: blockchain_votes
-- Links traditional votes to blockchain transactions
CREATE TABLE IF NOT EXISTS blockchain_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_id INTEGER NOT NULL UNIQUE,
    vote_hash VARCHAR(66) NOT NULL,
    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
    block_number INTEGER NOT NULL,
    blockchain_timestamp DATETIME NOT NULL,
    gas_used INTEGER,
    status VARCHAR(20) DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vote_id) REFERENCES votes(id) ON DELETE CASCADE
);

CREATE INDEX idx_blockchain_votes_vote_id ON blockchain_votes(vote_id);
CREATE INDEX idx_blockchain_votes_tx_hash ON blockchain_votes(transaction_hash);
CREATE INDEX idx_blockchain_votes_status ON blockchain_votes(status);

-- Table: blockchain_elections
-- Links traditional elections to blockchain records
CREATE TABLE IF NOT EXISTS blockchain_elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL UNIQUE,
    blockchain_election_id INTEGER NOT NULL,
    contract_address VARCHAR(42) NOT NULL,
    creation_tx_hash VARCHAR(66),
    activation_tx_hash VARCHAR(66),
    status VARCHAR(20) DEFAULT 'created',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE
);

CREATE INDEX idx_blockchain_elections_election_id ON blockchain_elections(election_id);
CREATE INDEX idx_blockchain_elections_status ON blockchain_elections(status);

-- Table: blockchain_transactions
-- General blockchain transaction log for auditing
CREATE TABLE IF NOT EXISTS blockchain_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
    transaction_type VARCHAR(50) NOT NULL, -- 'vote', 'election_create', 'election_activate', etc.
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42) NOT NULL,
    block_number INTEGER NOT NULL,
    gas_used INTEGER,
    gas_price_gwei DECIMAL(20, 9),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmed_at DATETIME
);

CREATE INDEX idx_blockchain_tx_hash ON blockchain_transactions(transaction_hash);
CREATE INDEX idx_blockchain_tx_type ON blockchain_transactions(transaction_type);
CREATE INDEX idx_blockchain_tx_status ON blockchain_transactions(status);
CREATE INDEX idx_blockchain_tx_created_at ON blockchain_transactions(created_at);

-- Table: blockchain_sync_status
-- Track synchronization between local DB and blockchain
CREATE TABLE IF NOT EXISTS blockchain_sync_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_synced_block INTEGER NOT NULL DEFAULT 0,
    last_sync_time DATETIME,
    total_votes_local INTEGER DEFAULT 0,
    total_votes_blockchain INTEGER DEFAULT 0,
    sync_percentage DECIMAL(5, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'synced', -- 'synced', 'syncing', 'out_of_sync', 'error'
    error_message TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial sync status
INSERT INTO blockchain_sync_status (last_synced_block, status)
VALUES (0, 'initialized');

-- Migration metadata
CREATE TABLE IF NOT EXISTS blockchain_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO blockchain_migrations (version, description)
VALUES ('001', 'Add blockchain integration tables for Phase 1');

-- Views for easy querying

-- View: votes_with_blockchain
-- Join votes with their blockchain records
CREATE VIEW IF NOT EXISTS votes_with_blockchain AS
SELECT
    v.id as vote_id,
    v.reference_number,
    v.timestamp as vote_timestamp,
    v.voter_id,
    v.candidate_id,
    bv.id as blockchain_vote_id,
    bv.vote_hash,
    bv.transaction_hash,
    bv.block_number,
    bv.blockchain_timestamp,
    bv.gas_used,
    bv.status as blockchain_status,
    CASE
        WHEN bv.id IS NOT NULL THEN 'on_chain'
        ELSE 'not_on_chain'
    END as sync_status
FROM votes v
LEFT JOIN blockchain_votes bv ON v.id = bv.vote_id;

-- View: blockchain_stats
-- Quick blockchain statistics
CREATE VIEW IF NOT EXISTS blockchain_stats AS
SELECT
    (SELECT COUNT(*) FROM votes) as total_votes_local,
    (SELECT COUNT(*) FROM blockchain_votes WHERE status = 'confirmed') as total_votes_blockchain,
    (SELECT COUNT(*) FROM votes WHERE id NOT IN (SELECT vote_id FROM blockchain_votes)) as votes_not_on_chain,
    (SELECT SUM(gas_used) FROM blockchain_votes) as total_gas_used,
    (SELECT AVG(gas_used) FROM blockchain_votes) as avg_gas_per_vote,
    (SELECT MAX(block_number) FROM blockchain_votes) as latest_block_recorded;

-- Comments for documentation
-- SQLite doesn't support COMMENT ON, but we can add a metadata table

CREATE TABLE IF NOT EXISTS blockchain_table_docs (
    table_name VARCHAR(100) PRIMARY KEY,
    description TEXT
);

INSERT OR REPLACE INTO blockchain_table_docs VALUES
('blockchain_votes', 'Links traditional votes to blockchain transaction records'),
('blockchain_elections', 'Links traditional elections to blockchain smart contract records'),
('blockchain_transactions', 'General log of all blockchain transactions for auditing'),
('blockchain_sync_status', 'Tracks synchronization status between local DB and blockchain'),
('blockchain_migrations', 'Tracks applied database migrations'),
('votes_with_blockchain', 'View: Votes joined with their blockchain records'),
('blockchain_stats', 'View: Quick blockchain statistics for monitoring');
