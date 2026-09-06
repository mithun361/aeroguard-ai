from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app=FastAPI(title='AeroGuard AI API',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
IMD_OBS='https://wis2box.imd.gov.in/oapi/collections/urn%3Awmo%3Amd%3Ain-imd%3Asurface-based-observations.synop/items'
IMD_STATIONS='https://wis2box.imd.gov.in/oapi/collections/stations/items'

@app.get('/health')
def health(): return {'status':'ok','service':'aeroguard-api'}

@app.get('/stations')
async def stations(limit:int=25):
    async with httpx.AsyncClient(timeout=20) as c:
        r=await c.get(IMD_STATIONS,params={'limit':limit,'f':'json'});r.raise_for_status();return r.json()

@app.get('/observations')
async def observations(limit:int=200):
    async with httpx.AsyncClient(timeout=20) as c:
        r=await c.get(IMD_OBS,params={'limit':limit,'f':'json'});r.raise_for_status();return r.json()

@app.get('/anomaly')
async def anomaly(value:float,baseline:float=25.0,scale:float=20.0):
    score=min(0.99,abs(value-baseline)/scale)
    return {'score':round(score,3),'status':'review' if score>.55 else 'normal',
            'note':'Starter screening rule; production model should be trained on station history.'}
