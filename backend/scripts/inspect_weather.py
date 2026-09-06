import httpx
URL="https://aviationweather.gov/api/data/metar"


params={
    "ids":"KJFK",
    "format":"json"

}

response=httpx.get(
    URL,
    params=params,
    timeout=10.0,
    headers={"User-Agent":"AeroWatch/1.0"}

)


print("Status Code:",response.status_code)
print("Content Type:",response.headers.get("content-type"))


print("\n----RAW RESPONSE------\n")

print(response.text[:5000])



