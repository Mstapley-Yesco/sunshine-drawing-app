from supabase_client import supabase

def get_all_drawings():
    try:
        response = supabase.table("drawings").select("*").execute(count="exact")
        return response.data
    except Exception as e:
        print("❌ Error fetching metadata:", e)
        return []

def insert_drawing_metadata(metadata: dict):
    print("📤 Attempting to insert metadata:")
    for key, value in metadata.items():
        print(f"  - {key}: {repr(value)} ({type(value).__name__})")
    try:
        response = supabase.table("drawings").insert(metadata).execute()
        print("✅ Supabase insert response:", response)
        return response
    except Exception as e:
        print("❌ Error inserting metadata:", str(e))
        return None
