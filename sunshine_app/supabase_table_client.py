from supabase_client import supabase

def insert_drawing_metadata(metadata: dict):
    try:
        response = supabase.table("drawings").insert(metadata).execute()
        return response
    except Exception as e:
        print("❌ Error inserting metadata:", e)
        return None

def get_all_drawings():
    try:
        response = supabase.table("drawings").select("*").execute()
        return response.data
    except Exception as e:
        print("❌ Error fetching metadata:", e)
        return []
