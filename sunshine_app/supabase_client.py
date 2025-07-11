import requests

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

def upload_to_supabase(bucket: str, file_name: str, file_bytes: bytes) -> str:
    try:
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_name}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/pdf",
            "x-upsert": "true"
        }
        response = requests.post(url, headers=headers, data=file_bytes)

        if response.status_code in [200, 201]:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"
        else:
            print("Upload failed:", response.status_code, response.text)
            return None
    except Exception as e:
        print(f"Custom upload error: {e}")
        return None
