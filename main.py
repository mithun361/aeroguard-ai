from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="AeroGuard AI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IMD_OBS = (
    "https://wis2box.imd.gov.in/oapi/collections/"
    "urn%3Awmo%3Amd%3Ain-imd%3Asurface-based-observations.synop/items"
)

IMD_STATIONS = (
    "https://wis2box.imd.gov.in/oapi/collections/stations/items"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "aeroguard-api"
    }


@app.get("/stations")
async def stations(limit: int = 25):
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "AeroGuard-AI/1.0"}
        ) as client:

            response = await client.get(
                IMD_STATIONS,
                params={
                    "limit": min(limit, 50),
                    "f": "json"
                }
            )

            response.raise_for_status()
            return response.json()

    except Exception as e:
        return {
            "type": "FeatureCollection",
            "features": [],
            "source": "IMD WIS2",
            "error": str(e)
        }


@app.get("/observations")
async def observations(limit: int = 100):
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={
                "User-Agent": "AeroGuard-AI/1.0",
                "Accept": "application/geo+json, application/json"
            }
        ) as client:

            response = await client.get(
                IMD_OBS,
                params={
                    "limit": min(limit, 100),
                    "f": "json"
                }
            )

            response.raise_for_status()

            data = response.json()

            return {
                "source": "IMD WIS2",
                "status": "ok",
                "count": len(data.get("features", [])),
                "data": data
            }

    except Exception as e:
        return {
            "source": "IMD WIS2",
            "status": "error",
            "count": 0,
            "data": {
                "type": "FeatureCollection",
                "features": []
            },
            "error": str(e)
        }


@app.get("/anomaly")
def anomaly(
    value: float,
    baseline: float = 25.0,
    scale: float = 20.0
):
    score = min(
        0.99,
        abs(value - baseline) / scale
    )

    return {
        "score": round(score, 3),
        "status": "review" if score > 0.55 else "normal",
        "note": (
            "Starter screening rule; production model "
            "should be trained on station history."
        )
    }
