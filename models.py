# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class Voter(UserMixin, db.Model):
    __tablename__ = 'voters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    voter_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    has_voted = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    id_document_path = db.Column(db.String(255), nullable=True)
    mfa_secret = db.Column(db.String(32), nullable=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    votes = db.relationship('Vote', backref='voter', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Generate a password reset token"""
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if reset token is valid"""
        if self.reset_token == token and self.reset_token_expiry > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f'<Voter {self.voter_id}>'

class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(255), nullable=False)
    promises = db.Column(db.Text, nullable=False)
    assets = db.Column(db.Text, nullable=False)
    liabilities = db.Column(db.Text, nullable=False)
    background = db.Column(db.Text, nullable=False)
    political_views = db.Column(db.Text, nullable=False)
    regional_views = db.Column(db.Text, nullable=False)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    manifesto_url = db.Column(db.String(255), nullable=True)
    social_media_links = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    votes = db.relationship('Vote', backref='candidate', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def vote_count(self):
        """Get total votes for this candidate"""
        return self.votes.count()

    def __repr__(self):
        return f'<Candidate {self.name}>'

class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reference_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Vote {self.reference_number}>'

class Election(db.Model):
    __tablename__ = 'elections'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    enable_live_results = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_ongoing(self):
        """Check if election is currently ongoing"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date

    def has_ended(self):
        """Check if election has ended"""
        return datetime.utcnow() > self.end_date

    def __repr__(self):
        return f'<Election {self.title}>'

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Announcement {self.title}>'

from datetime import timedelta

# ==============================================================================
# Blockchain Integration Models (Phase 1)
# ==============================================================================

class BlockchainVote(db.Model):
    """Links traditional votes with blockchain transactions for immutability verification"""
    __tablename__ = 'blockchain_votes'

    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id', ondelete='CASCADE'), nullable=False, unique=True)
    vote_hash = db.Column(db.String(66), nullable=False)  # Cryptographic hash of vote
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False, index=True)  # Blockchain tx hash
    block_number = db.Column(db.Integer, nullable=False)  # Block where vote was recorded
    blockchain_timestamp = db.Column(db.DateTime, nullable=False)  # Block timestamp
    gas_used = db.Column(db.Integer, nullable=True)  # Gas consumed
    status = db.Column(db.String(20), default='confirmed')  # confirmed, pending, failed
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    vote = db.relationship('Vote', backref=db.backref('blockchain_record', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<BlockchainVote vote_id={self.vote_id} tx={self.transaction_hash[:10]}...>'

class BlockchainElection(db.Model):
    """Links traditional elections with blockchain election contracts"""
    __tablename__ = 'blockchain_elections'

    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False, unique=True)
    blockchain_election_id = db.Column(db.Integer, nullable=False)  # ID on blockchain
    contract_address = db.Column(db.String(42), nullable=False, index=True)  # Ethereum address format
    creation_tx_hash = db.Column(db.String(66), nullable=False)
    is_active_on_chain = db.Column(db.Boolean, default=False)
    activation_tx_hash = db.Column(db.String(66), nullable=True)
    deactivation_tx_hash = db.Column(db.String(66), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    election = db.relationship('Election', backref=db.backref('blockchain_record', uselist=False))

    def __repr__(self):
        return f'<BlockchainElection election_id={self.election_id} contract={self.contract_address[:10]}...>'

class BlockchainTransaction(db.Model):
    """Comprehensive log of all blockchain transactions for audit trail"""
    __tablename__ = 'blockchain_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_hash = db.Column(db.String(66), unique=True, nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False)  # vote_record, election_create, voter_register, etc.
    from_address = db.Column(db.String(42), nullable=False)  # Sender wallet
    to_address = db.Column(db.String(42), nullable=False)  # Contract address
    block_number = db.Column(db.Integer, nullable=False, index=True)
    gas_used = db.Column(db.Integer, nullable=True)
    gas_price = db.Column(db.BigInteger, nullable=True)  # in wei
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    error_message = db.Column(db.Text, nullable=True)  # If transaction failed
    retry_count = db.Column(db.Integer, default=0)
    metadata = db.Column(db.JSON, nullable=True)  # Additional transaction data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<BlockchainTransaction {self.transaction_type} tx={self.transaction_hash[:10]}...>'

class BlockchainSyncStatus(db.Model):
    """Track synchronization status between local DB and blockchain"""
    __tablename__ = 'blockchain_sync_status'

    id = db.Column(db.Integer, primary_key=True)
    last_synced_block = db.Column(db.Integer, nullable=False, default=0)
    total_votes_on_chain = db.Column(db.Integer, default=0)
    total_votes_in_db = db.Column(db.Integer, default=0)
    sync_status = db.Column(db.String(20), default='in_sync')  # in_sync, syncing, out_of_sync, error
    last_sync_time = db.Column(db.DateTime, nullable=True)
    next_sync_time = db.Column(db.DateTime, nullable=True)
    error_count = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text, nullable=True)
    network = db.Column(db.String(20), default='mumbai')  # mumbai, polygon

    def __repr__(self):
        return f'<BlockchainSyncStatus network={self.network} status={self.sync_status}>'