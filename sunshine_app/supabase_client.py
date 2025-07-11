from supabase import create_client
import os

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def upload_to_supabase(bucket: str, file_path: str, file_bytes: bytes):
    file_name = os.path.basename(file_path)
    response = supabase.storage.from_(bucket).upload(file_name, file_bytes, {"content-type": "application/pdf", "upsert": True})
    if response.status_code == 200:
        url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"
        return url
    return None

def delete_from_supabase(bucket: str, file_name: str):
    return supabase.storage.from_(bucket).remove([file_name])
