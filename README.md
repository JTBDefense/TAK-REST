# CoT REST Service for ATAK

This is a Python-based REST API that allows external systems to post object locations which are converted into CoT (Cursor on Target) messages and forwarded to ATAK over UDP.

## Features

- FastAPI-based REST interface
- Sends CoT XML via UDP using configurable host and port
- Supports `person`, `car`, `helicopter`, `drone` object types
- Optional UID and hashtag per object
- API key authorization
- All configuration is stored in a single `config.json` file

---

## Installation

```bash
git clone https://github.com/JTBDefense/TAK-REST.git
cd TAK-REST
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a file named `config.json` in the root directory:

```json
{
  "atak_host": "127.0.0.1",
  "atak_port": 8088,
  "api_keys": [
    "your-api-key-here",
	"your-api-key-here"
  ]
}
```

---

## Running the Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

API documentation is available at: `http://localhost:8000/docs`

---

## REST Usage

### Endpoint

`POST /position`

### JSON Body

```json
{
  "api_key": "your-api-key-here",
  "stale_minutes": 10,
  "objects": [
    {
      "name": "RescueDrone42",
      "type": "drone",
      "lat": 52.2297,
      "lon": 21.0122,
      "hashtag": "#search"
    },
    {
      "uid": "car-unit-001",
      "name": "MedicTeam1",
      "type": "car",
      "lat": 52.2301,
      "lon": 21.0130
    }
  ]
}
```

### Response

```json
{
  "status": "sent",
  "count": 2
}
```

---

## Notes

- UID defaults to `REST_<name>` with non-alphanumeric characters replaced by `_`
- Hashtag is added as `<remarks>` field in the CoT message
- Messages are sent immediately to the host/port defined in `config.json`