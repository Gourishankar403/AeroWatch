import httpx
import sys

BASE_URL = 'http://127.0.0.1:8000'
TIMEOUT = 120.0

def print_header(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def test_root():
    r = httpx.get(f'{BASE_URL}/', timeout=TIMEOUT)
    print('GET / :', r.status_code, r.json())
    assert r.status_code == 200

def test_health():
    r = httpx.get(f'{BASE_URL}/health', timeout=TIMEOUT)
    print('GET /health :', r.status_code, r.json())
    assert r.status_code == 200

def test_invalid_requests():
    print_header('PHASE 3: API VALIDATION TESTS')
    
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'JFK', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    print('TEST 1 (JFK):', r.status_code)

    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': '1234', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    print('TEST 2 (1234):', r.status_code)

    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'KJFK', 'query': ''}, timeout=TIMEOUT)
    print('TEST 3 (empty query):', r.status_code)

    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'kjfk', 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    print('TEST 4 (kjfk):', r.status_code)
    if r.status_code == 200:
        print('Returned airport:', r.json().get('airport'))

def test_multi_airport():
    print_header('PHASE 4: MULTI-AIRPORT LIVE TESTING')
    airports = ['KJFK', 'KLAX', 'KORD', 'KDEN', 'EGLL']
    
    for a in airports:
        print(f'\nInvestigating {a}...')
        r = httpx.post(f'{BASE_URL}/investigate', json={'airport': a, 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
        print('Status:', r.status_code)
        if r.status_code == 200:
            data = r.json()
            analysis = data.get('analysis', {})
            verif = data.get('verification', {})
            print(f"Airport: {data.get('airport')}")
            print(f"Disruption detected: {analysis.get('disruption_detected')}")
            print(f"Weather risk: {analysis.get('weather_risk_detected')}")
            print(f"Confidence: {analysis.get('confidence')}")
            print(f"Revisions: {data.get('revision_count')}")
            print(f"Observed facts count: {len(analysis.get('observed_facts', []))}")
            print(f"Potential factors count: {len(analysis.get('potential_factors', []))}")
            print(f"Limitations count: {len(analysis.get('limitations', []))}")
            print(f"Verification approved: {verif.get('approved')}")
            print(f"Verification summary: {verif.get('verification_summary')}")
        else:
            print("Response:", r.text)

def test_different_queries():
    print_header('PHASE 5: DIFFERENT QUERY TESTING')
    queries = [
        "Investigate current operational conditions.",
        "Check for operational disruption and weather risk.",
        "Assess current airport conditions and possible disruption factors.",
        "Determine whether available evidence supports an operational disruption."
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'KJFK', 'query': q}, timeout=TIMEOUT)
        print('Status:', r.status_code)

def test_evidence_consistency():
    print_header('PHASE 6: EVIDENCE CONSISTENCY')
    a = 'KORD'
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': a, 'query': 'Investigate current operational conditions.'}, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        print('Returned Airport:', data.get('airport'))
        ev = data.get('evidence', {})
        faa_ev = ev.get('operations_evidence', {})
        wx_ev = ev.get('weather_evidence', {})
        print('FAA evidence airport:', faa_ev.get('airport'))
        print('Weather evidence airport:', wx_ev.get('airport'))

def test_causal_reasoning():
    print_header('PHASE 7: CAUSAL REASONING')
    r = httpx.post(f'{BASE_URL}/investigate', json={'airport': 'KJFK', 'query': 'Why is KJFK experiencing delays? Determine whether weather is causing the delays.'}, timeout=TIMEOUT)
    if r.status_code == 200:
        analysis = r.json().get('analysis', {})
        print('Overall Assessment:', analysis.get('overall_assessment'))
        print('Observed Facts:', analysis.get('observed_facts'))
        print('Potential Factors:', analysis.get('potential_factors'))
        print('Limitations:', analysis.get('limitations'))

if __name__ == '__main__':
    test_root()
    test_health()
    test_invalid_requests()
    test_multi_airport()
    test_different_queries()
    test_evidence_consistency()
    test_causal_reasoning()
