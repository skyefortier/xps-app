import sys, json, io
sys.path.insert(0, '/Users/skyefortier/xps-app')
import os
os.chdir('/Users/skyefortier/xps-app')
from app import create_app
SCR='/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad'
app = create_app(upload_folder=SCR+'/up')
c = app.test_client()
def upload(csv):
    r = c.post('/api/upload', data={'file': (io.BytesIO(csv.encode()), 'spectrum.csv')}, content_type='multipart/form-data')
    return r.get_json()['session_id']
def post(path, body, raw=False):
    r = c.post(path, data=json.dumps(body) if not isinstance(body,str) else body, content_type='application/json')
    txt = r.get_data(as_text=True)
    if raw: return r.status_code, txt
    try: return r.status_code, json.loads(txt)
    except Exception: return r.status_code, txt
