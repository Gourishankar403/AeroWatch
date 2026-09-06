import httpx


URL="https://nasstatus.faa.gov/api/airport-status-information"

def inspect_faa_data():
    response=httpx.get(URL)

    print("Status Code:",response.status_code)
    print("Content Type : ",response.headers.get("content-type"))

    print("\n-- RAW RESPONSE (first 5000 characters )----\n")

    print(response.text[:5000])




if __name__=="__main__":
    inspect_faa_data()



