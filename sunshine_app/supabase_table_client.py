import requests

SUPABASE_URL = "https://jjlptduwuthgvetuqsyc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbHB0ZHV3dXRoZ3ZldHVxc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjI0NDAzMiwiZXhwIjoyMDY3ODIwMDMyfQ.bzfQmJvWTgW3IxSEl5YEsqpU0py0T1LhtIbKv2F5H2s"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def insert_drawing_metadata(data: dict):
    url = f"{SUPABASE_URL}/rest/v1/drawings"
    response = requests.post(url, headers=HEADERS, json=[data])
    if response.status_code not in [200, 201]:
        print("Failed to insert metadata:", response.status_code, response.text)
    return response.status_code

def get_all_drawings():
    url = f"{SUPABASE_URL}/rest/v1/drawings?select=*"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch metadata:", response.status_code, response.text)
        return []
