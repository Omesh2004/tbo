# JSON Data Output - Enhanced Guide

## ✅ Enhancement Complete

The JSON file output now includes **API status tracking** to help you debug any API connectivity issues.

## 📄 Sample JSON Output Format

```json
{
  "flights": [],
  "hotels": [],
  "hotel_price_range": {},
  "activities": [...],
  "source": "TBO_TEKTRAVELS",
  "timestamp": "2026-02-28T12:05:35.010694",
  "api_status": {
    "flights": "error",
    "flights_error": "ConnectionError: Unable to connect to API",
    "hotels": "success",
    "hotels_error": null
  }
}
```

## 🔍 API Status Values

### Status Field
Each API (flights, hotels) will have one of these statuses:

| Status | Meaning | Action |
|--------|---------|--------|
| `"success"` | ✅ API responded and returned data | Data is in the respective array |
| `"empty_response"` | ⚠️ API responded but no data | Check if the dates/destination are valid |
| `"error"` | ❌ API call failed | Check error message in `*_error` field |
| `"pending"` | ⏳ API not yet called | Initial state |

### Error Field
The `*_error` field contains the exception message:
- If `flights_error` is not null, it contains the error why flights couldn't be fetched
- If `hotels_error` is not null, it contains the error why hotels couldn't be fetched

## 🧪 How to Debug Using the JSON File

### 1. Check the JSON Output
```bash
# View the JSON file
cat travel_package_data_tbo.json | python -m json.tool
```

### 2. Look at api_status Section
```json
"api_status": {
  "flights": "error",
  "flights_error": "ConnectionError: Failed to connect to TekTravels API",
  "hotels": "success",
  "hotels_error": null
}
```

### 3. Interpret the Results

**Flights error:**
```
"flights_error": "ConnectionError: Failed to connect to https://api.tektravels.com"
```
→ **Problem**: Network connectivity or API endpoint is wrong
→ **Solution**: Check internet connection, verify API URL

**Hotels normal API response but empty:**
```
"hotels": "empty_response",
"hotels_error": null
```
→ **Problem**: API returned response but no data
→ **Solution**: Check if dates are too far in future, or destination code is wrong

**Hotels with data:**
```
"hotels": "success",
"hotels_error": null
```
→ **Success**: Hotels data is in the `hotels` array

## 🛠️ Run Test Script for Detailed Debugging

I've created `test_apis.py` to test API connectivity directly:

```bash
# From Docker
docker exec tbo-pipeline python test_apis.py

# From manual setup
cd tbo_tektravels
python test_apis.py
```

This will show:
- ✅ If APIs are responding
- Response status codes
- Sample data from each API
- Detailed error messages

## 📊 Complete Data Structure

```json
{
  "flights": [
    {
      "id": "flight-001",
      "airline": "Iberia",
      "departure": "2026-03-15T09:00:00Z",
      "arrival": "2026-03-15T13:30:00Z",
      "price": 185.50
    }
  ],
  "hotels": [
    {
      "hotelId": "ATH123",
      "hotelName": "Hotel Athens",
      "price": 95.00,
      "rating": 4.5
    }
  ],
  "hotel_price_range": {
    "min": 45.00,
    "max": 250.00,
    "avg": 95.50,
    "currency": "USD"
  },
  "activities": [
    {
      "id": "act-001",
      "name": "Acropolis Guided Tour",
      "price": 45.00,
      "rating": 4.8
    }
  ],
  "source": "TBO_TEKTRAVELS",
  "timestamp": "2026-02-28T12:05:35.010694",
  "api_status": {
    "flights": "success|error|empty_response",
    "flights_error": null|"ErrorType: error message",
    "hotels": "success|error|empty_response",
    "hotels_error": null|"ErrorType: error message"
  }
}
```

## 🚀 How to Use This Information

### Scenario 1: Flights are empty but hotels have data

**JSON Output:**
```json
"api_status": {
  "flights": "empty_response",
  "hotels": "success"
}
```

**Debugging Steps:**
1. Run `python test_apis.py` to test TekTravels Flight API directly
2. Check if the origin (MAD) and destination (ATH) codes are valid
3. Verify the departure date (2026-03-15) is valid for the API
4. Check TekTravels API documentation for rate limiting

### Scenario 2: Both APIs return errors

**JSON Output:**
```json
"api_status": {
  "flights": "error",
  "flights_error": "ConnectionError: Failed to connect",
  "hotels": "error",
  "hotels_error": "Unknown host: api.tbotechnology.in"
}
```

**Debugging Steps:**
1. Check internet connectivity: `ping google.com`
2. Verify API endpoints are accessible:
   ```bash
   curl -I https://api.tektravels.com
   curl -I http://api.tbotechnology.in/TBOHolidays_HotelAPI/CountryList
   ```
3. Check firewall/proxy settings
4. Verify credentials in `.env` file

### Scenario 3: Hotels return error

**JSON Output:**
```json
"hotel_error": "Unauthorized: Invalid credentials"
```

**Debugging Steps:**
1. Check `.env` file for correct credentials:
   ```bash
   echo $TBO_HOTEL_USERNAME
   echo $TBO_HOTEL_PASSWORD
   ```
2. Run test script to verify: `python test_apis.py`
3. Re-enter credentials in `.env` file if needed

## 📈 Files You're Saving

| File | Location | Format | Frequency |
|------|----------|--------|-----------|
| **travel_package_data_tbo.json** | `/tbo_tektravels/` | JSON | Every 15 minutes |
| **API Status Info** | Inside JSON | JSON field | Every 15 minutes |
| **Error Messages** | Inside JSON | Text in API errors | When errors occur |

## ✅ Quick Check Procedure

1. **Run the pipeline:**
   ```bash
   docker-compose up
   # or
   python testamad_tbo.py
   ```

2. **Wait for first run (30-45 seconds)**

3. **Check the JSON file:**
   ```bash
   cat travel_package_data_tbo.json | python -m json.tool
   ```

4. **Look at api_status section:**
   - Both "success" → All good! ✅
   - Any "error" → Check error message and use test_apis.py
   - Any "empty_response" → Check API documentation for valid parameters

5. **If there are errors, run test script:**
   ```bash
   python test_apis.py
   ```

## 🔄 Automated Saving

The JSON file is automatically:
- Created every time the pipeline runs
- Updated every 15 minutes (default schedule)
- Overwritten with newest data
- Saved with proper JSON formatting (indent=2 for readability)

## 📋 Files You Can Check

### Development Setup
```bash
# View JSON file directly
cat travel_package_data_tbo.json

# Pretty print it
cat travel_package_data_tbo.json | python -m json.tool

# View specific section (api_status)
cat travel_package_data_tbo.json | python -m json.tool | grep -A 10 "api_status"
```

### Docker Setup
```bash
# View from inside container
docker exec tbo-pipeline cat travel_package_data_tbo.json

# Copy to host and view
docker cp tbo-pipeline:/app/travel_package_data_tbo.json ./
cat travel_package_data_tbo.json | python -m json.tool
```

## 🎯 Summary

✅ **JSON file is being saved to**: `travel_package_data_tbo.json`
✅ **Format**: Pretty-printed JSON with 2-space indentation
✅ **Frequency**: Every scheduled run (15 minutes)
✅ **API Status**: Included in every JSON output
✅ **Error Details**: Stored in `api_status` section
✅ **Testing**: Use `test_apis.py` script to debug API issues

---

**Next Step**: Run the pipeline and check the JSON file to see the api_status section!
