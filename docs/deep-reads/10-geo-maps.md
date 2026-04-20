# DEEP-wave8: Geo/Maps Intelligence for AR Glasses SDK

## Table of Contents
1. [Overpass API & overpass-turbo](#1-overpass-api--overpass-turbo)
2. [Gemini API - Grounding with Google Maps](#2-gemini-api---grounding-with-google-maps)
3. [Scaniverse / Niantic Spatial](#3-scaniverse--niantic-spatial)
4. [Plonkit - GeoGuessr Geolocation Guide](#4-plonkit---geoguessr-geolocation-guide)
5. [LearnableMeta - Geo Learning Platform](#5-learnablemeta---geo-learning-platform)
6. [FirstOnMaps YouTube Channel](#6-firstonmaps-youtube-channel)
7. [AR Glasses Integration Patterns](#7-ar-glasses-integration-patterns)

---

## 1. Overpass API & overpass-turbo

### Overview
Overpass API is the primary read-only API for querying OpenStreetMap data. overpass-turbo
is the web-based IDE for constructing and visualizing Overpass API queries.

### API Endpoints

**Default Overpass API Server:**
```
https://overpass-api.de/api/
```

**Public Instances (from configs.ts):**
- `https://overpass-api.de/api/`
- `https://maps.mail.ru/osm/tools/overpass/api/`
- `https://overpass.private.coffee/api/`

**Key API Endpoints:**
- `{server}interpreter` - Main query endpoint (POST or GET)
- `{server}kill_my_queries` - Abort running queries
- `{server}status` - Server status

**Nominatim Geocoding (from nominatim.ts):**
```
https://nominatim.openstreetmap.org/search?format=json&q={search}
```
Returns: JSON array with lat, lon, boundingbox, osm_type, osm_id

### Query Languages Supported
From overpass.ts - three query languages:
- **OverpassQL** - Primary query language
- **XML** - XML-based query format
- **SQL** - PostGIS-compatible SQL queries (via Postpass)

### Overpass Query Patterns (from source code analysis)

#### Basic Query Structure (OverpassQL)
```
[out:json][timeout:25];
// query statements
nwr["amenity"="restaurant"]({{bbox}});
out geom;
```

#### Wizard/FFS (Free Form Search) System (ffs.ts)
The wizard converts natural language into Overpass queries. Key patterns:

**Bounds Types:**
- `bbox` - Current map viewport: `({{bbox}})`
- `area` - Named area: `{{geocodeArea:CityName}}->.searchArea;` then `(area.searchArea)`
- `around` - Radius search: `(around:{{radius}},{{geocodeCoords:PlaceName}})`
- `global` - No bounds restriction

**Query Clause Types (from get_query_clause):**
- `key`: `["key"]` - Has tag
- `nokey`: `["key"!~".*"]` - Does not have tag
- `eq`: `["key"="value"]` - Exact match
- `neq`: `["key"!="value"]` - Not equal
- `like`: `["key"~"regex"]` - Regex match
- `likelike`: `[~"key_regex"~"value_regex"]` - Both key and value are regex
- `notlike`: `["key"!~"regex"]` - Negative regex match
- `meta/id`: `(id_number)` - Filter by OSM ID
- `meta/newer`: `(newer:"date")` - Filter by timestamp
- `meta/user`: `(user:"username")` - Filter by editor
- `meta/uid`: `(uid:number)` - Filter by user ID

**Entity Types:**
- `nwr` = node + way + relation (shorthand for all three)
- `node`, `way`, `relation` individually

#### Template/Shortcut System (shortcuts.ts)
Mustache-style templates `{{name:instruction}}`:

- `{{bbox}}` - Current map bounding box (s,w,n,e for OverpassQL)
- `{{center}}` - Map center coordinates (lat,lng)
- `{{date:offset}}` - Relative date (e.g., `{{date:-1day}}`, `{{date:-6months}}`)
- `{{geocodeId:name}}` - Nominatim lookup returns `type(id)` (e.g., `way(12345)`)
- `{{geocodeArea:name}}` - Area ID with offset (+2400000000 for ways, +3600000000 for relations)
- `{{geocodeBbox:name}}` - Bounding box from Nominatim
- `{{geocodeCoords:name}}` - Lat/lon from Nominatim
- `{{radius=1000}}` - User-defined constant (default 1000m)

#### Query Parser (query.ts)
- Supports user-defined constants: `{{VarName=value}}`
- Template replacement with shortcut callbacks
- Recursive parsing for async geocoding operations

#### Auto-Repair System (autorepair.ts)
Automatically fixes common query issues:
- Missing `(._;>;);` recurse statements before `out` statements
- Wrong output format (converts to xml for map display)
- Missing `meta` mode in print/out statements
- Overpass geometry mode fixes (center, bb, geom)

#### Free-Form Search Presets (ffs/free.ts)
Uses `@openstreetmap/id-tagging-schema` presets for natural language queries:
- Converts terms like "restaurant", "hospital", "park" to OSM tag queries
- Fuzzy matching with Levenshtein distance for typo correction
- Geometry type mapping: point/vertex → node, line → way, area → way+relation

#### Example Queries for AR Glasses

**Find nearby restaurants:**
```
[out:json][timeout:25];
nwr["amenity"="restaurant"](around:500,{user_lat},{user_lng});
out geom;
```

**Find all POIs in view:**
```
[out:json][timeout:25];
(
  node["amenity"]({{bbox}});
  node["shop"]({{bbox}});
  node["tourism"]({{bbox}});
);
out geom;
```

**Find walking paths:**
```
[out:json][timeout:25];
way["highway"="footway"](around:200,{lat},{lng});
out geom;
```

**Building information:**
```
[out:json][timeout:25];
way["building"](around:50,{lat},{lng});
out body geom;
```

### Response Data Formats
From overpass.ts analysis:
- **JSON (osm3s)**: Contains `elements[]` with nodes/ways/relations, `osm3s.timestamp_osm_base`
- **XML**: Standard OSM XML with `<node>`, `<way>`, `<relation>` elements
- **GeoJSON**: FeatureCollection with geometry and properties
- Stats tracked: nodes, ways, relations, areas counts

### Map Rendering
- Uses Leaflet with custom GeoJsonNoVanish layer
- MapCSS styling system for feature visualization
- Default tile server: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
- Max zoom: 20
- Default view: lat 41.89, lon 12.492, zoom 16 (Rome)

---

## 2. Gemini API - Grounding with Google Maps

### Overview
Grounding with Google Maps connects Gemini's generative AI with Google Maps' database
of 250+ million places worldwide. Launched October 17, 2025.

### API Configuration

**Enable Maps Grounding (JSON):**
```json
{
  "contents": [{"parts": [{"text": "Restaurants near Times Square."}]}],
  "tools": {"googleMaps": {}},
  "toolConfig": {
    "retrievalConfig": {
      "latLng": {
        "latitude": 40.758896,
        "longitude": -73.985130
      }
    }
  }
}
```

**Enable Widget (JSON):**
```json
{
  "tools": {"googleMaps": {"enableWidget": true}}
}
```

### Python SDK Usage
```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents="What are the best Italian restaurants within a 15-minute walk from here?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(retrieval_config=types.RetrievalConfig(
            lat_lng=types.LatLng(latitude=34.050481, longitude=-118.248526))),
    ),
)

# Access grounding metadata
if grounding := response.candidates[0].grounding_metadata:
    if grounding.grounding_chunks:
        for chunk in grounding.grounding_chunks:
            print(f'- [{chunk.maps.title}]({chunk.maps.uri})')
```

### Response Structure - groundingMetadata

```json
{
  "candidates": [{
    "content": {"parts": [{"text": "CanteenM is an American restaurant..."}], "role": "model"},
    "groundingMetadata": {
      "groundingChunks": [{
        "maps": {
          "uri": "https://maps.google.com/?cid=13100894621228039586",
          "title": "Heaven on 7th Marketplace",
          "placeId": "places/ChIJ0-zA1vBZwokRon0fGj-6z7U"
        }
      }],
      "groundingSupports": [{
        "segment": {
          "startIndex": 0,
          "endIndex": 79,
          "text": "CanteenM is an American restaurant with a 4.6-star rating and is open 24 hours."
        },
        "groundingChunkIndices": [0]
      }],
      "webSearchQueries": ["restaurants near me"],
      "googleMapsWidgetContextToken": "widgetcontent/..."
    }
  }]
}
```

### Key Response Fields
- **groundingChunks**: Array of maps sources (uri, placeId, title)
- **groundingSupports**: Links text segments to sources via startIndex/endIndex
- **googleMapsWidgetContextToken**: Token for rendering interactive Places widget
- **webSearchQueries**: The search queries used

### Widget Rendering
```html
<gmp-place-contextual context-token="{widget_token}"></gmp-place-contextual>
```
Requires Google Maps JavaScript API loaded.

### Supported Models
| Model | Supported |
|-------|-----------|
| Gemini 3.1 Pro Preview | ✔️ |
| Gemini 3.1 Flash-Lite Preview | ✔️ |
| Gemini 3 Flash Preview | ✔️ |
| Gemini 2.5 Pro | ✔️ |
| Gemini 2.5 Flash | ✔️ |
| Gemini 2.5 Flash-Lite | ✔️ |
| Gemini 2.0 Flash | ✔️ |

### Pricing
- **$25 per 1,000 grounded prompts**
- **Free tier: 500 requests/day**
- Only counted when prompt successfully returns Google Maps grounded results
- Multiple Maps queries from single request = 1 request for billing

### Use Cases for AR Glasses
1. **Place-specific questions**: "Is there a cafe near the corner of 1st and Main that has outdoor seating?"
2. **Location-based personalization**: "Which family-friendly restaurants near here have the best playground reviews?"
3. **Itinerary planning**: "Plan a day in San Francisco for me"
4. **Combine with Google Search**: Maps for structured data (addresses, hours, ratings) + Search for timely context (events, news)

### Service Requirements
- Must display Google Maps sources immediately following grounded content
- Must use Google Maps text attribution (Roboto font, specific styling)
- Must link sources using uri or googleMapsUri from response
- Can cache: googleMapsWidgetContextToken, placeId, reviewId

### Limitations
- Text input/output only (no multimodal beyond text + map widgets)
- Tool is OFF by default - must explicitly enable
- Prohibited territories: China, Crimea, Cuba, Iran, North Korea, Syria, Vietnam, etc.
- Not for emergency response services

---

## 3. Scaniverse / Niantic Spatial

### Overview
Scaniverse (now part of Niantic Spatial) has evolved from a mobile 3D scanning app
into a full spatial data platform. Redirects to nianticspatial.com.

### Product Suite
1. **Capture** - 3D data collection from mobile, drones, 360° cameras
2. **Reconstruct** - Create digital twins of objects and large areas
3. **Localize** - Vision-based positioning for machines (VPS)
4. **Understand** - Semantic querying at every 3D point

### Key Capabilities
- **High-fidelity 3D scanning** from iOS and Android devices
- **Gaussian Splats and meshes** processed on-device
- **SPZ format** - Open-source format, 90% file size reduction
- **Collaborative tools** for team-based scanning
- **On-demand data capture** service for large areas
- **Multi-sensor hardware** for centimeter-level accuracy
- **BYOD (Bring Your Own Data)** integrations

### AR Glasses Relevance
- Real-world 3D capture for spatial understanding
- VPS (Visual Positioning System) for precise AR anchoring
- Large Geospatial Model foundation
- Digital twin creation for indoor/outdoor navigation
- SDK available: `nianticspatial.com/docs/`

---

## 4. Plonkit - GeoGuessr Geolocation Guide

### Overview
Comprehensive geolocation guide for identifying countries and regions from street-view
imagery. Covers countries across all continents with official Google Street View.

### Guide Structure
For each country, three sections:
1. **Identifying the country** - Visual clues for country recognition
2. **Regional/subdivision-specific clues** - Narrowing down within a country
3. **Spotlight** - Very specific, detailed clues

### Coverage by Continent
- **Africa**: Botswana, Egypt, Eswatini, Ghana, Kenya, Lesotho, Madagascar, Mali, Namibia, Nigeria, Reunion, Rwanda, Senegal, South Africa, São Tomé and Príncipe, Tanzania, Tunisia, Uganda
- **Asia**: Multiple countries
- **Europe**: Comprehensive coverage
- **North America**: US, Canada, Mexico, Caribbean
- **Oceania**: Australia, New Zealand, Pacific islands
- **South America**: Major countries

### AR Glasses Relevance - Visual Geolocation Clues
Key clue categories useful for AR visual recognition:
- Road signs, markings, and infrastructure styles
- Vehicle types and license plate formats
- Language/script identification on signage
- Vegetation and terrain patterns
- Architectural styles
- Utility pole designs
- Sun position and shadow angles
- Google Street View camera metadata patterns

---

## 5. LearnableMeta - Geo Learning Platform

### Overview
Interactive platform for learning geolocation skills. URL: learnablemeta.com.
"New way to learn Geoguessr" - provides structured learning paths and practice maps.

### Features
- **How To** guides for geolocation techniques
- **Maps** collection for practice
- **Personal Maps** - Custom map creation
- **Map Creator Tools** - For content creators
- **Discord community** for collaboration

### AR Glasses Relevance
- Visual pattern recognition training data
- Country/region identification methodology
- Structured geolocation knowledge base

---

## 6. FirstOnMaps YouTube Channel

### Overview
YouTube channel (`@FirstOnMaps`) focused on map techniques and geolocation strategies,
primarily in Shorts format. Content covers practical GeoGuessr and mapping techniques.

### AR Glasses Relevance
- Visual recognition techniques for real-world navigation
- Quick-reference geo identification patterns
- Community-sourced geolocation intelligence

---

## 7. AR Glasses Integration Patterns

### Architecture: Local Search & Navigation System

```
┌─────────────────────────────────────────────────┐
│                AR GLASSES HUD                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Camera   │ │ GPS/IMU  │ │ User Voice/Gaze  │ │
│  │ Feed     │ │ Sensors  │ │ Input            │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       │            │                │             │
│       ▼            ▼                ▼             │
│  ┌─────────────────────────────────────────┐     │
│  │         Query Router / Agent             │     │
│  └──┬──────────┬──────────────┬────────────┘     │
│     │          │              │                   │
│     ▼          ▼              ▼                   │
│  ┌──────┐  ┌────────┐  ┌──────────────┐         │
│  │Overpass│  │Gemini  │  │Niantic       │         │
│  │API    │  │Maps    │  │Spatial VPS   │         │
│  │(OSM)  │  │Ground  │  │(3D Position) │         │
│  └──┬────┘  └───┬────┘  └──────┬───────┘         │
│     │           │              │                   │
│     ▼           ▼              ▼                   │
│  ┌─────────────────────────────────────────┐     │
│  │     Spatial Context Fusion Layer         │     │
│  │  - Place data + Reviews + Navigation     │     │
│  │  - OSM building/road data overlay        │     │
│  │  - 3D spatial anchoring                  │     │
│  └──────────────────┬──────────────────────┘     │
│                     │                             │
│                     ▼                             │
│  ┌─────────────────────────────────────────┐     │
│  │         AR Overlay Renderer              │     │
│  │  - POI labels + ratings                  │     │
│  │  - Navigation arrows                     │     │
│  │  - Building info panels                  │     │
│  │  - Contextual recommendations            │     │
│  └─────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

### Integration Pattern 1: Overpass API for OSM Data Overlay
**Use case**: Show building names, road types, POI markers on AR view

```typescript
// Query nearby POIs for AR overlay
async function getArPois(lat: number, lng: number, radius: number = 200) {
  const query = `
    [out:json][timeout:10];
    (
      node["amenity"](around:${radius},${lat},${lng});
      node["shop"](around:${radius},${lat},${lng});
      node["tourism"](around:${radius},${lat},${lng});
      node["name"](around:${radius},${lat},${lng});
    );
    out body;
  `;
  const response = await fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    body: `data=${encodeURIComponent(query)}`
  });
  return response.json(); // {elements: [{type, id, lat, lon, tags}...]}
}
```

### Integration Pattern 2: Gemini Maps for Contextual Questions
**Use case**: User asks "What's that building?" or "Find me coffee nearby"

```typescript
async function askAboutLocation(question: string, lat: number, lng: number) {
  const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent', {
    method: 'POST',
    headers: {'Content-Type': 'application/json', 'x-goog-api-key': API_KEY},
    body: JSON.stringify({
      contents: [{parts: [{text: question}]}],
      tools: {googleMaps: {enableWidget: true}},
      toolConfig: {retrievalConfig: {latLng: {latitude: lat, longitude: lng}}}
    })
  });
  const data = await response.json();
  // Extract places from groundingMetadata.groundingChunks
  return {
    text: data.candidates[0].content.parts[0].text,
    places: data.candidates[0].groundingMetadata?.groundingChunks?.map(c => ({
      name: c.maps.title,
      url: c.maps.uri,
      placeId: c.maps.placeId
    })) || []
  };
}
```

### Integration Pattern 3: Combined OSM + Gemini Pipeline
**Use case**: Rich contextual AR with both structural and AI data

```typescript
async function getFullArContext(lat: number, lng: number, userQuery?: string) {
  // 1. Get structural data from OSM (buildings, roads, POIs)
  const osmData = await getArPois(lat, lng, 300);

  // 2. If user has a question, use Gemini Maps grounding
  let geminiResponse = null;
  if (userQuery) {
    geminiResponse = await askAboutLocation(userQuery, lat, lng);
  }

  // 3. Merge data for AR overlay
  return {
    osmPois: osmData.elements.map(el => ({
      lat: el.lat, lng: el.lon,
      name: el.tags?.name,
      type: el.tags?.amenity || el.tags?.shop || el.tags?.tourism,
      tags: el.tags
    })),
    aiResponse: geminiResponse?.text,
    aiPlaces: geminiResponse?.places,
    // For navigation: extract ways with highway tag
    roads: osmData.elements.filter(el => el.tags?.highway)
  };
}
```

### Integration Pattern 4: Niantic Spatial VPS for Precise AR Anchoring
**Use case**: Anchor AR content to precise 3D positions

```
Niantic Spatial SDK provides:
- Visual Positioning System (VPS) for cm-level accuracy
- Gaussian Splat rendering for photorealistic 3D
- Semantic understanding of scanned environments
- SPZ format for efficient 3D data transfer
```

### Key API Rate Limits & Considerations

| Service | Rate Limit | Cost | Best For |
|---------|-----------|------|----------|
| Overpass API | ~10K/day (fair use) | Free | Structural map data, bulk POI queries |
| Gemini Maps | 500/day free, then $25/1K | Paid | AI-powered place questions, reviews, recommendations |
| Nominatim | 1 req/sec | Free | Geocoding text to coordinates |
| Niantic Spatial | SDK-based | Varies | 3D positioning, spatial understanding |

### Recommended AR Glasses Data Flow

1. **Continuous (low-frequency)**: Poll Overpass API every 30s for nearby POIs as user moves
2. **On-demand (user-triggered)**: Use Gemini Maps grounding for voice questions about places
3. **Background**: Niantic VPS for precise spatial anchoring when available
4. **Cache aggressively**: OSM data changes slowly; cache POI results by geohash tiles
5. **Offline fallback**: Pre-download OSM data tiles for known areas via Overpass

### Overpass Query Templates for AR Use Cases

**Nearby Everything (200m radius):**
```
[out:json][timeout:10];
(node["name"](around:200,{LAT},{LNG});
 way["building"]["name"](around:200,{LAT},{LNG}););
out body geom;
```

**Restaurants with cuisine:**
```
[out:json][timeout:10];
nwr["amenity"="restaurant"](around:500,{LAT},{LNG});
out body;
```

**Public transit stops:**
```
[out:json][timeout:10];
node["public_transport"="stop_position"](around:500,{LAT},{LNG});
out body;
```

**Wheelchair accessible places:**
```
[out:json][timeout:10];
nwr["wheelchair"="yes"](around:300,{LAT},{LNG});
out body;
```

**Emergency services:**
```
[out:json][timeout:10];
(node["amenity"="hospital"](around:2000,{LAT},{LNG});
 node["amenity"="pharmacy"](around:1000,{LAT},{LNG});
 node["amenity"="police"](around:2000,{LAT},{LNG}););
out body;
```

**Walking navigation paths:**
```
[out:json][timeout:15];
way["highway"~"footway|pedestrian|path|steps"](around:500,{LAT},{LNG});
out geom;
```

---

## Summary of Sources

| Source | URL | Type | Key Value |
|--------|-----|------|-----------|
| Overpass API | overpass-api.de/api/ | REST API | Free OSM data queries |
| overpass-turbo | overpass-turbo.eu | Web IDE | Query patterns & wizard system |
| Gemini Maps Grounding | ai.google.dev/gemini-api/docs/maps-grounding | API Docs | AI-powered place intelligence |
| Google Blog | blog.google/.../grounding-google-maps-gemini-api/ | Blog | Feature announcement & use cases |
| Scaniverse/Niantic | nianticspatial.com | Platform | 3D spatial capture & VPS |
| Plonkit | plonkit.net/guide | Guide | Visual geolocation clue database |
| LearnableMeta | learnablemeta.com | Platform | Geo learning & practice |
| FirstOnMaps | youtube.com/@FirstOnMaps | YouTube | Map technique videos |

---

*Generated: 2026-04-20 | Wave 8 Geo/Maps Deep Intelligence*
*Sources: overpass-turbo repo analysis, Gemini API docs, Niantic Spatial, Plonkit, LearnableMeta*
