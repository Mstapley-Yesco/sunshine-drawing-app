from .supabase_client import supabase

def insert_drawing_metadata(metadata):
    try:
        response = supabase.table("drawings").insert(metadata).execute()
        if response.status_code >= 200 and response.status_code < 300:
            print("✅ Metadata successfully inserted.")
        else:
            print("❌ Failed to insert metadata:", response.json())
    except Exception as e:
        print("❌ Exception occurred while inserting metadata:", e)

def fetch_all_drawings():
    try:
        response = supabase.table("drawings").select("*").execute()
        return response.data
    except Exception as e:
        print("❌ Error fetching drawings:", e)
        return []
