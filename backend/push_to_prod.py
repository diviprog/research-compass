import requests
from app.db.database import SessionLocal
from app.models.opportunity import Opportunity

BASE_URL = 'https://research-compass-production.up.railway.app'

auth = requests.post(f'{BASE_URL}/api/auth/signin', json={
    'email': 'devansh@gmail.com',
    'password': 'Sumi1234'
})

token = auth.json().get('access_token')
print(f'Token acquired: {bool(token)}')

headers = {'Authorization': f'Bearer {token}'}

# Test the token works
me = requests.get(f'{BASE_URL}/api/auth/me', headers=headers)
print(f'Auth test: {me.status_code} — {me.json()}')

# Test creating one opportunity
db = SessionLocal()
opp = db.query(Opportunity).filter(Opportunity.is_active == True).first()

r = requests.post(
    f'{BASE_URL}/api/opportunities',
    json={'title': opp.title, 'description': opp.description, 'institution': opp.institution or 'UCLA', 'is_active': True},
    headers=headers
)
print(f'Create test: {r.status_code} — {r.text[:200]}')
db.close()