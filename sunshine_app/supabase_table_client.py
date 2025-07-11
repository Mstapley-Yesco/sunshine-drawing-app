from supabase_client import supabase

def insert_drawing_metadata(metadata: dict):
    print("📤 Attempting to insert this metadata into Supabase:")
    for key, value in metadata.items():
        print(f"  - {key}: {repr(value)} ({type(value).__name__})")

    try:
        response = supabase.table("drawings").insert(metadata).execute()
        print("✅ Supabase response:", response)
        return response
    except Exception as e:
        print("❌ Exception during Supabase insert:", str(e))
        return None
