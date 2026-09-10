const API_BASE_URL = "http://127.0.0.1:8000";

async function testInvestigation() {
  const response = await fetch(
    `${API_BASE_URL}/investigate`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        airport: "KJFK",
        query: "Investigate current operational conditions.",
      }),
    }
  );

  const data = await response.json();

  console.log(
    JSON.stringify(data, null, 2)
  );
}

testInvestigation();