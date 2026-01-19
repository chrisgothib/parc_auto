# core/security.py
import hashlib

def hasher_motdepasse(motdepasse: str) -> str:
    return hashlib.sha256(motdepasse.encode()).hexdigest()
