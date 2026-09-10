const API_BASE_URL = "http://127.0.0.1:8000";


export async function investigateAirport(airport, query) {
  const response = await fetch(
    `${API_BASE_URL}/investigate`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        airport: airport.trim().toUpperCase(),
        query: query.trim(),
      }),
    }
  );


  if (!response.ok) {
    let errorMessage = "Investigation request failed.";

    try {
      const errorData = await response.json();

      if (errorData?.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : "Invalid investigation request.";
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(errorMessage);
  }


  return response.json();
}