# Geolocation / Imagery OSINT Reference

## Image Metadata Extraction

### EXIF Data
When the user uploads an image, extract metadata immediately:

```bash
# If exiftool is available
exiftool image.jpg

# Python fallback
python3 -c "
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
img = Image.open('image.jpg')
exif = img._getexif()
if exif:
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f'{tag}: {value}')
"
```

**Key EXIF fields:**
- GPS coordinates (latitude, longitude, altitude)
- Camera make/model (narrows down device type)
- Date/time taken (plus timezone if available)
- Software (editing history)
- Orientation (how the photo was held)
- Focal length, aperture (lens/distance estimation)
- Thumbnail (may contain original uncropped image)

### GPS Coordinate Conversion
If GPS data is in DMS (degrees, minutes, seconds):
```python
# Convert DMS to decimal
def dms_to_dd(degrees, minutes, seconds, direction):
    dd = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        dd *= -1
    return dd
```

Then search: `web_search "{latitude}, {longitude}"` to identify the location.

## Visual Geolocation (No Metadata)

When images lack EXIF data, use visual clues systematically:

### Clue Hierarchy (check in this order)

1. **Text and signage**
   - Language on signs, shops, advertisements
   - Road signs (format, colors, fonts vary by country)
   - License plates (format reveals country/state)
   - Phone numbers (country/area codes)
   - Business names (searchable)

2. **Infrastructure**
   - Road markings (line styles, colors, side of road)
   - Power line/pole styles (wooden vs concrete, wire configs)
   - Traffic lights and street furniture
   - Building architecture (materials, roof styles)
   - Rail tracks and gauge

3. **Vegetation and terrain**
   - Tree species (palm, birch, eucalyptus — climate indicators)
   - Terrain type (desert, tropical, tundra, temperate)
   - Agricultural patterns (rice paddies, vineyards, wheat fields)
   - Season indicators (leaf color, snow, dry/wet)

4. **Sun and shadows**
   - Shadow direction + time → approximate latitude
   - Sun position and angle → hemisphere and season
   - Use SunCalc or similar for precise calculations

5. **Cultural indicators**
   - Clothing styles
   - Vehicle types and brands
   - Currency visible
   - Religious buildings
   - Flag or national symbols

### Search Techniques for Visual Clues
- `image_search` with descriptive queries: "red brick building clock tower European"
- `web_search` for unique text found in images
- Search for distinctive landmarks: "spiral church tower copper roof Scandinavia"
- Use Google Maps/Earth terminology: "aerial view [description] [suspected region]"

## Reverse Image Search

Claude can't directly do reverse image search, but can guide:

### Suggest to User
```
Upload the image to:
1. Google Lens (lens.google.com) — best for landmarks, products, text
2. TinEye (tineye.com) — best for finding exact matches and older copies
3. Yandex Images (yandex.com/images) — best for faces and Eastern European content
4. Bing Visual Search — good general alternative
```

### Finding the Image Online
- Search for unique text or watermarks visible in the image
- Search for the filename if provided (sometimes reveals origin)
- Check image dimensions — non-standard sizes may indicate specific platforms
- Calculate and search for image hash

## Location Verification

When you have a suspected location, verify it:

1. **Cross-reference with maps**: `web_search "address" OR "location name" maps`
2. **Street view**: `web_search "location" street view` to find matching imagery
3. **Satellite imagery**: Compare features visible from above
4. **Local business search**: `web_search "nearby business name" "location"`
5. **Historical imagery**: Check if Google Earth historical view matches the timeframe

## Temporal Analysis

### Time Estimation from Images
- **Shadows**: Short shadows = midday, long = morning/evening
- **Sun position**: Calculate using latitude and shadow angle
- **Lighting**: Golden hour, blue hour, overcast — time of day indicators
- **Activity**: Rush hour traffic, empty streets, school hours
- **Seasonal**: Snow, autumn leaves, blooming flowers, dry season

### Timeline Correlation
When investigating an event:
- Cross-reference claimed time with sun position
- Check weather records: `web_search "[location] weather [date]"` — does it match?
- Compare with nearby CCTV footage timestamps if available
- Check social media posts from the same location/time

## Physical Site Reconnaissance (via OSINT)

### Building and Address Investigation
- `web_search "[address]"` for property records, businesses registered there
- Check Google Maps for satellite view, street view, nearby businesses
- Search for planning permits or building records
- Check if the address appears in corporate filings (shell company indicator)

### Facility Analysis
From satellite/aerial imagery:
- Estimate building size and purpose
- Identify security features (fences, cameras, barriers)
- Vehicle types and counts (activity level)
- Antenna or satellite dish installations (communications)
- Loading docks, warehouses (logistics)
- Parking lot occupancy patterns (work hours, activity)

### Kali Follow-up
```bash
# Extract metadata from bulk images
exiftool -r -gps:all -csv ./images/ > gps_data.csv

# Correlate GPS coordinates
python3 << 'EOF'
import csv
import json

with open('gps_data.csv') as f:
    reader = csv.DictReader(f)
    locations = []
    for row in reader:
        if row.get('GPSLatitude') and row.get('GPSLongitude'):
            locations.append({
                'file': row['SourceFile'],
                'lat': row['GPSLatitude'],
                'lon': row['GPSLongitude'],
                'time': row.get('DateTimeOriginal', 'unknown')
            })

with open('locations.json', 'w') as f:
    json.dump(locations, f, indent=2)
print(f"Found {len(locations)} geotagged images")
EOF
```
