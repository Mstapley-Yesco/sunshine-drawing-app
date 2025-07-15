from supabase import create_client

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(bucket, file_name, file_bytes):
    try:
        headers = {"x-upsert": "true"}

        if file_name.endswith(".pdf"):
            headers["content-type"] = "application/pdf"
        elif file_name.endswith(".png"):
            headers["content-type"] = "image/png"

        response = supabase.storage.from_(bucket).upload(
            file_name,
            file_bytes,
            headers
        )

        print("📤 Raw upload response:", response)

        # Supabase-py returns a dict-like object. If "Key" is not present, we still return the constructed URL.
        if isinstance(response, dict) and "Key" in response:
            print("✅ File uploaded successfully:", response["Key"])
        else:
            print("⚠️ Upload may have succeeded but did not return a 'Key':", response)

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"
        print("🔗 Constructed public URL:", public_url)
        return public_url

    except Exception as e:
        print("❌ Exception during upload:", e)
        return None