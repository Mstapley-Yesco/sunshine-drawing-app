from supabase import create_client

url = "https://jjlptduwuthgvetuqsyc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

supabase = create_client(url, key)

def upload_to_supabase(bucket: str, file_name: str, file_bytes: bytes) -> str:
    try:
        response = supabase.storage.from_(bucket).upload(
            file_name,
            file_bytes,
            {"content-type": "application/pdf"},
            True  # upsert flag
        )
        public_url = supabase.storage.from_(bucket).get_public_url(file_name)
        return public_url
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return None
