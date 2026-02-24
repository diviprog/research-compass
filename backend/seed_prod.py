from datetime import datetime
import psycopg2
import json
from app.db.database import SessionLocal
from app.models.opportunity import Opportunity

PROD_DB_URL = "postgresql://postgres:HwofArQghAXMjQqzdLdPnZkHEPFrdlBu@yamanote.proxy.rlwy.net:11185/railway"

db = SessionLocal()
opps = db.query(Opportunity).filter(Opportunity.is_active == True).all()
print(f'Local opportunities: {len(opps)}')
db.close()

conn = psycopg2.connect(PROD_DB_URL)
cur = conn.cursor()

now = datetime.utcnow()
success = 0
for opp in opps:
    try:
        cur.execute("""
            INSERT INTO opportunities 
            (title, description, institution, lab_name, pi_name, 
            location_city, location_state, is_remote, research_topics, 
            degree_levels, paid_type, is_active, contact_email, source_url, scraped_at, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            opp.title, opp.description, opp.institution, opp.lab_name, opp.pi_name,
            opp.location_city, opp.location_state, opp.is_remote or False,
            json.dumps(opp.research_topics or []),
            json.dumps(opp.degree_levels or []),
            opp.paid_type or 'unpaid', True,
            opp.contact_email, opp.source_url, now, now
        ))
        conn.commit()
        success += 1
        print(f'  ✓ {opp.title[:50]}')
    except Exception as e:
        print(f'  ✗ {opp.title[:50]} — {e}')
        conn.rollback()

cur.close()
conn.close()
print(f'Done: {success}/{len(opps)}')