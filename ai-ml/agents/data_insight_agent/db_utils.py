
import psycopg2
import json

def fetch_latest_uploaded_data(file_id='demo'):
    conn = psycopg2.connect(
        dbname="scope3",
        user="postgres",
        password="P@ssw0rd",
        host="host.docker.internal",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT data FROM uploaded_records WHERE file_id = %s LIMIT 1", (file_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return json.dumps(result[0]) if result else "{}"
