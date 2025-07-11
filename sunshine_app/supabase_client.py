from supabase import create_client
import os

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(bucket, file_name, file_bytes):
    try:
        response = supabase.storage.from_(bucket).upload(
            file_name,
            file_bytes,
            {"content-type": "application/pdf", "x-upsert": "true"}
        )
        if response.status_code >= 200 and response.status_code < 300:
            print("✅ File uploaded successfully.")
        else:
            print("❌ Upload failed:", response.json())
        return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"
    except Exception as e:
        print("❌ Exception during upload:", e)
        return None
