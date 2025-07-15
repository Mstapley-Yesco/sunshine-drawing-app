from supabase import create_client

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(bucket: str, file_name: str, file_bytes: bytes) -> str | None:
    try:
        response = supabase.storage.from_(bucket).upload(
            file_name,
            file_bytes,
            headers = {     "x-upsert": "true" }  
            if file_name.endswith(".pdf"):     
                headers["content-type"] = "application/pdf" elif file_name.endswith(".png"):     
                headers["content-type"] = "image/png"  
            response = supabase.storage.from_(bucket).upload(     
                file_name,     
                file_bytes,     
                headers )
        )
        if "Key" in response:
            print("✅ File uploaded successfully:", response["Key"])
            return {"url": f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_name}"}
        else:
            print("❌ Upload failed:", response)
            return None
    except Exception as e:
        print("❌ Exception during upload:", e)
        return None
