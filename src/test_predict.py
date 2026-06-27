import urllib.request
import json

def test_api():
    url = "http://127.0.0.1:5000/predict"
    
    # Test client data (typical approved profile: good income, employed, married, etc.)
    data = {
        "CODE_GENDER": "0", # Female
        "AGE": "35",
        "NAME_FAMILY_STATUS": "Married",
        "NAME_EDUCATION_TYPE": "Higher education",
        "CNT_CHILDREN": "0",
        "CNT_FAM_MEMBERS": "2",
        "NAME_HOUSING_TYPE": "House / apartment",
        "AMT_INCOME_TOTAL": "150000",
        "NAME_INCOME_TYPE": "Working",
        "OCCUPATION_TYPE": "Core staff",
        "YEARS_EMPLOYED": "10",
        "FLAG_OWN_CAR": 1,
        "FLAG_OWN_REALTY": 1,
        "UNEMPLOYED": 0,
        "FLAG_WORK_PHONE": 1,
        "FLAG_PHONE": 1,
        "FLAG_EMAIL": 1
    }
    
    headers = {"Content-Type": "application/json"}
    
    print("Sending POST request to /predict API...")
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            print("API response:")
            print(json.dumps(res_json, indent=4))
    except Exception as e:
        print(f"API request failed: {e}")

if __name__ == "__main__":
    test_api()
