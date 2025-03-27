from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta
import socket
import xml.etree.ElementTree as ET
import json
import re

# Load configuration
with open("config.json") as f:
    CONFIG = json.load(f)

ATAK_HOST = CONFIG["atak_host"]
ATAK_PORT = CONFIG["atak_port"]
API_KEYS = set(CONFIG["api_keys"])

app = FastAPI()

class ObjectType(str, Enum):
    person = "person"
    car = "car"
    helicopter = "helicopter"
    drone = "drone"

COT_TYPE_MAP = {
    ObjectType.person: "a-f-G-U",
    ObjectType.car: "a-f-G-E-V-C-U-L",
    ObjectType.helicopter: "a-f-A-C-H",
    ObjectType.drone: "a-f-A-C-H",
}

class CoTObject(BaseModel):
    uid: Optional[str] = None
    name: str
    type: ObjectType
    lat: float
    lon: float
    hae: float = 0.0
    remarks: Optional[str] = None

class CoTRequest(BaseModel):
    api_key: str
    objects: List[CoTObject]
    stale_minutes: Optional[int] = 5

def isoformat_z(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"

def sanitize_uid(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())

def generate_cot_xml(obj: CoTObject, stale_minutes: int) -> bytes:
    now = datetime.utcnow()
    stale = now + timedelta(minutes=stale_minutes)
    uid = obj.uid or f"REST_{sanitize_uid(obj.name)}"

    event = ET.Element("event")
    event.set("version", "2.0")
    event.set("uid", uid)
    event.set("type", COT_TYPE_MAP[obj.type])
    event.set("how", "m-g")
    event.set("time", isoformat_z(now))
    event.set("start", isoformat_z(now))
    event.set("stale", isoformat_z(stale))

    pt_attr = {
        "lat": str(obj.lat),
        "lon": str(obj.lon),
        "hae": str(obj.hae),
        "ce": "10",
        "le": "10"
    }
    ET.SubElement(event, "point", attrib=pt_attr)

    detail = ET.SubElement(event, "detail")
    ET.SubElement(detail, "contact", attrib={"callsign": obj.name})

    if obj.remarks:
        ET.SubElement(detail, "remarks").text = obj.remarks

    return ET.tostring(event, encoding="utf-8")

def send_to_atak(xml_data: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(xml_data, (ATAK_HOST, ATAK_PORT))

@app.post("/position")
def position(request: CoTRequest):
    if request.api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    for obj in request.objects:
        xml = generate_cot_xml(obj, request.stale_minutes)
        send_to_atak(xml)
    return {"status": "sent", "count": len(request.objects)}
