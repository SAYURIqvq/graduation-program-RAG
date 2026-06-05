"""Test Entity extractor"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.graph.entity_extractor import EntityExtractor


def test_entity_extraction():
    """Test basic entity extraction."""
    
    print("\n🧪 Testing Entity Extractor\n")
    
    extractor = EntityExtractor()
    
    # Test text
    text = """
    Machine learning is a subset of artificial intelligence. 
    Google and Facebook use machine learning extensively.
    Python and TensorFlow are popular tools.
    The technology originated in the United States.
    """
    
    # Extract
    entities = extractor.extract(text)
    
    print(f"📊 Extracted {len(entities)} entities:\n")
    
    for ent in entities:
        print(f"  {ent.label:15} → {ent.text}")
    
    # Deduplicate
    grouped = extractor.deduplicate_entities(entities)
    
    print(f"\n📋 Grouped by type:")
    for label, texts in grouped.items():
        print(f"  {label}: {', '.join(texts)}")
    
    # Frequency
    freq = extractor.get_entity_frequency(entities)
    
    print(f"\n🔢 Frequency:")
    for (text, label), count in freq.items():
        print(f"  {text} ({label}): {count}x")


if __name__ == "__main__":
    test_entity_extraction()