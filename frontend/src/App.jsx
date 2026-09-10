import { useState } from "react";
import "./App.css";
import { investigateAirport } from "./services/api";

function App() {
  const [airport, setAirport] = useState("");
  const [query, setQuery] = useState(
    "Investigate current operational conditions."
  );

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInvestigate = async () => {
    const normalizedAirport = airport.trim().toUpperCase();
    const normalizedQuery = query.trim();

    if (!normalizedAirport) {
      setError("Please enter an airport ICAO code.");
      return;
    }

    if (normalizedAirport.length !== 4) {
      setError("Airport code must contain exactly 4 letters.");
      return;
    }

    if (!/^[A-Z]{4}$/.test(normalizedAirport)) {
      setError("Airport code must contain only letters.");
      return;
    }

    if (!normalizedQuery) {
      setError("Please enter an investigation query.");
      return;
    }

    setError("");
    setResult(null);
    setLoading(true);

    try {
      const investigationResult = await investigateAirport(
        normalizedAirport,
        normalizedQuery
      );

      setResult(investigationResult);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Unable to complete the investigation."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">
            <span className="brand-icon-line"></span>
          </div>

          <div>
            <h1>AeroWatch</h1>
            <p>Aviation Disruption Investigation</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          <span>System Online</span>
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="hero-content">
            <span className="eyebrow">
              EVIDENCE-GROUNDED AVIATION INTELLIGENCE
            </span>

            <h2>
              Investigate airport operational conditions.
            </h2>

            <p>
              AeroWatch combines operational and weather
              evidence to produce a verified aviation
              disruption assessment.
            </p>
          </div>
        </section>

        <section className="investigation-panel">
          <div className="panel-header">
            <div>
              <h3>Start Investigation</h3>
              <p>
                Enter an airport and investigation objective.
              </p>
            </div>

            <span className="panel-label">
              INVESTIGATION
            </span>
          </div>

          <div className="form-grid">
            <div className="form-group airport-group">
              <label htmlFor="airport">
                Airport
              </label>

              <input
                id="airport"
                type="text"
                value={airport}
                onChange={(event) =>
                  setAirport(
                    event.target.value
                      .toUpperCase()
                      .slice(0, 4)
                  )
                }
                placeholder="KJFK"
                maxLength={4}
                disabled={loading}
              />

              <span className="input-hint">
                Example: KJFK, KLAX, EGLL
              </span>
            </div>

            <div className="form-group query-group">
              <label htmlFor="query">
                Investigation Query
              </label>

              <input
                id="query"
                type="text"
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                placeholder="What should AeroWatch investigate?"
                disabled={loading}
              />
            </div>

            <div className="panel-actions">
              <button
                className="investigate-button"
                onClick={handleInvestigate}
                disabled={loading}
              >
                <span className="button-mark"></span>

                {loading
                  ? "Investigating..."
                  : "Investigate Airport"}
              </button>
            </div>
          </div>

          {error && (
            <div className="error-message">
              <span className="error-dot"></span>
              {error}
            </div>
          )}
        </section>

        {!result && !loading && !error && (
          <section className="empty-state">
            <div className="empty-state-mark">
              <span></span>
            </div>

            <div>
              <h3>No investigation yet</h3>
              <p>
                Enter an airport above to begin an
                evidence-grounded investigation.
              </p>
            </div>
          </section>
        )}

        {loading && (
          <section className="empty-state loading-state">
            <div className="loading-spinner"></div>

            <div>
              <h3>Investigation in progress</h3>
              <p>
                AeroWatch is collecting operational and
                weather evidence and verifying the analysis.
              </p>
            </div>
          </section>
        )}

        {result && (
          <section className="results-section">
            <div className="results-header">
              <div>
                <span className="eyebrow">
                  INVESTIGATION COMPLETE
                </span>

                <div className="airport-heading">
                  <h3>{result.airport}</h3>

                  <span className="verification-badge">
                    <span className="verification-dot"></span>
                    Verified
                  </span>
                </div>
              </div>

              <div className="revision-info">
                <span>REVISIONS</span>
                <strong>{result.revision_count}</strong>
              </div>
            </div>

            <div className="status-grid">
              <div className="status-card">
                <span className="card-label">
                  Operational Status
                </span>

                <div className="status-value">
                  <span
                    className={`status-indicator ${
                      result.analysis.disruption_detected
                        ? "status-warning"
                        : "status-good"
                    }`}
                  ></span>

                  <strong>
                    {result.analysis.disruption_detected
                      ? "Disruption Detected"
                      : "No Disruption Detected"}
                  </strong>
                </div>
              </div>

              <div className="status-card">
                <span className="card-label">
                  Weather Risk
                </span>

                <div className="status-value">
                  <span
                    className={`status-indicator ${
                      result.analysis.weather_risk_detected
                        ? "status-warning"
                        : "status-good"
                    }`}
                  ></span>

                  <strong>
                    {result.analysis.weather_risk_detected
                      ? "Risk Detected"
                      : "Low Risk"}
                  </strong>
                </div>
              </div>

              <div className="status-card">
                <span className="card-label">
                  Confidence
                </span>

                <strong className="large-value">
                  {result.analysis.confidence}
                </strong>
              </div>

              <div className="status-card">
                <span className="card-label">
                  Revisions
                </span>

                <strong className="large-value">
                  {result.revision_count}
                </strong>
              </div>
            </div>

            <div className="assessment-card">
              <div className="assessment-header">
                <span className="card-label">
                  Overall Assessment
                </span>

                <span className="evidence-label">
                  EVIDENCE GROUNDED
                </span>
              </div>

              <p>
                {result.analysis.overall_assessment}
              </p>
            </div>

            <div className="details-grid">
              <div className="details-card">
                <div className="details-header">
                  <h4>Observed Facts</h4>

                  <span className="count-badge">
                    {result.analysis.observed_facts.length}
                  </span>
                </div>

                {result.analysis.observed_facts.length > 0 ? (
                  <ul>
                    {result.analysis.observed_facts.map(
                      (fact, index) => (
                        <li key={index}>
                          <span className="list-dot"></span>
                          <span>{fact}</span>
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className="muted">
                    No observed facts available.
                  </p>
                )}
              </div>

              <div className="details-card">
                <div className="details-header">
                  <h4>Potential Factors</h4>

                  <span className="count-badge">
                    {result.analysis.potential_factors.length}
                  </span>
                </div>

                {result.analysis.potential_factors.length >
                0 ? (
                  <ul>
                    {result.analysis.potential_factors.map(
                      (factor, index) => (
                        <li key={index}>
                          <span className="list-dot"></span>
                          <span>{factor}</span>
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className="muted">
                    No potential factors identified.
                  </p>
                )}
              </div>
            </div>

            <div className="details-card limitations-card">
              <div className="details-header">
                <h4>Limitations</h4>

                <span className="count-badge">
                  {result.analysis.limitations.length}
                </span>
              </div>

              <ul>
                {result.analysis.limitations.map(
                  (limitation, index) => (
                    <li key={index}>
                      <span className="list-dot"></span>
                      <span>{limitation}</span>
                    </li>
                  )
                )}
              </ul>
            </div>

            <div className="verification-card">
              <div className="verification-content">
                <div className="verification-mark">
                  <span></span>
                </div>

                <div>
                  <span className="card-label">
                    VERIFICATION
                  </span>

                  <h4>
                    {result.verification.approved
                      ? "Analysis approved"
                      : "Analysis requires review"}
                  </h4>

                  <p>
                    {
                      result.verification
                        .verification_summary
                    }
                  </p>
                </div>
              </div>

              <div
                className={`verification-status ${
                  result.verification.approved
                    ? "approved"
                    : "requires-review"
                }`}
              >
                <span></span>

                {result.verification.approved
                  ? "Approved"
                  : "Requires Review"}
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>AeroWatch</span>

        <span>
          Evidence <b>/</b> Analysis <b>/</b> Verification
        </span>
      </footer>
    </div>
  );
}

export default App;