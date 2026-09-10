import httpx
import sys

BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 120.0

def run_tests():
    print("Running AEROWATCH REGRESSION TESTS...\n")
    
    # 1. JFK -> assert HTTP 422
    print("Testing 'JFK'...")
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'JFK', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("PASS: JFK -> 422")

    # 2. 1234 -> assert HTTP 422
    print("Testing '1234'...")
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': '1234', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("PASS: 1234 -> 422")

    # 3. empty query -> assert HTTP 422
    print("Testing empty query...")
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'KJFK', 'query': ''}, timeout=TIMEOUT)
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("PASS: empty query -> 422")

    # 4. kjfk -> assert HTTP 200 and returned airport == KJFK
    print("Testing 'kjfk'...")
    try:
        r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'kjfk', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}. Response: {r.text}"
        data = r.json()
        assert data.get('airport') == 'KJFK', f"Expected KJFK, got {data.get('airport')}"
        
        # Check successful investigation structure
        assert 'analysis' in data, "analysis missing"
        assert 'verification' in data, "verification missing"
        assert isinstance(data['verification'].get('approved'), bool), "verification.approved is not boolean"
        assert isinstance(data.get('revision_count'), int), "revision_count is not an integer"
        print("PASS: kjfk -> 200 (Success structure validated)")
    except httpx.ConnectError as e:
        print(f"BLOCKED: Network provider unreachable during kjfk test: {e}")
        sys.exit(1)
        
    print("\nALL AUTOMATED TESTS PASSED.")

if __name__ == '__main__':
    run_tests()
