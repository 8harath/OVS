# models.py
from dataclasses import dataclass

@dataclass
class Voter:
    id: int
    name: str
    last_name: str
    date_of_birth: str
    phone_number: str
    voter_id: str
    password: str
    has_voted: bool = False

@dataclass
class Candidate:
    id: int
    name: str
    party: str
    photo_url: str
    promises: str
    assets: str
    liabilities: str
    background: str
    political_views: str
    regional_views: str

@dataclass
class Vote:
    id: int
    voter_id: int
    candidate_id: int
    timestamp: str
    reference_number: str