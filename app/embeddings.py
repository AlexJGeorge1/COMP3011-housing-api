"""
Model: all-MiniLM-L6-v2
"""

from typing import List

def _build_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

# only loads the model the first time it's needed
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = _build_model()
    return _model


def embed_text(text: str) -> List[float]:
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_listing(listing) -> List[float]:
    parts = []
    if listing.property_type:
        parts.append(listing.property_type.capitalize())
    if listing.bedrooms:
        parts.append(f"{listing.bedrooms}-bedroom")
    parts.append("property")
    if listing.address:
        parts.append(f"at {listing.address}")
    if listing.region:
        parts.append(f"in {listing.region}")
    parts.append(f"sold for £{listing.price:,}")
    if listing.transaction_date:
        parts.append(f"in {listing.transaction_date.year}")

    text = " ".join(parts)
    return embed_text(text)
