"""
Build BM25 Index

Build BM25 keyword search index from documents in ChromaDB.
Run this after uploading documents and before using KeywordSearchAgent.

Usage:
    python build_bm25_index.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.retrieval.bm25_index import BM25Index
from src.storage.chroma_store import ChromaVectorStore


def build_index():
    """Build BM25 index from ChromaDB."""
    
    print("=" * 60)
    print("BUILD BM25 INDEX")
    print("=" * 60)
    
    # Check if vector store has data
    print("\n📊 Checking ChromaDB...")
    store = ChromaVectorStore()
    count = store.count()
    
    if count == 0:
        print("❌ No documents in ChromaDB!")
        print("\nPlease upload documents through the Streamlit app first:")
        print("  streamlit run app.py")
        return
    
    print(f"✅ Found {count} chunks in ChromaDB")
    
    # Build index
    print("\n🔨 Building BM25 index...")
    print("-" * 60)
    
    index = BM25Index()
    
    try:
        # Build from vector store
        index.build_from_vector_store(store)
        
        # Save to disk
        index.save()
        
        # Show stats
        stats = index.get_stats()
        
        print("\n" + "=" * 60)
        print("INDEX BUILD COMPLETE")
        print("=" * 60)
        print(f"✅ Total chunks indexed: {stats['total_chunks']}")
        print(f"✅ Index saved to: {stats['index_path']}")
        
        # Test search
        print("\n🧪 Testing index...")
        test_query = "python"
        results = index.search(test_query, top_k=3)
        
        print(f"\nTest query: '{test_query}'")
        print(f"Results: {len(results)}")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. Score: {result['score']:.3f}")
            print(f"   {result['text'][:100]}...")
        
        print("\n✅ Index is ready to use!")
        print("\n💡 Next steps:")
        print("   1. Run the Streamlit app: streamlit run app.py")
        print("   2. Ask a question in Agentic mode to use BM25 with vector and graph retrieval")
        
    except Exception as e:
        print(f"\n❌ Failed to build index: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        build_index()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
