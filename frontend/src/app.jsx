import React, { useState } from "react";

import { fetchGenerationData } from "./api/generation";
import FilterForm from "./components/FilterForm";
import GenerationChart from "./components/GenerationChart";
import "./styles/chart.css";
import "./styles/form.css";

function App() {
  const [startTime, setStartTime] = useState("2025-01-01T00:00");
  const [endTime, setEndTime] = useState("2025-01-02T00:00");
  const [forecastHorizonHours, setForecastHorizonHours] = useState("4");
  const [responseData, setResponseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const result = await fetchGenerationData({
        startTime,
        endTime,
        forecastHorizonHours,
      });

      setResponseData(result);
    } catch (fetchError) {
      setResponseData(null);
      setError(fetchError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">REint Forecast Monitoring</p>
        <h1>UK Wind Generation Dashboard</h1>
        <p className="hero-copy">
          Compare actual generation with the latest valid forecast for a chosen
          time range and forecast horizon.
        </p>
      </header>

      <main className="dashboard-grid">
        <section className="panel panel-large">
          <h2>Controls</h2>
          <p className="panel-copy">
            Choose the target time range and the forecast horizon used for
            selecting the latest valid forecast.
          </p>
          <FilterForm
            startTime={startTime}
            endTime={endTime}
            forecastHorizonHours={forecastHorizonHours}
            onStartTimeChange={setStartTime}
            onEndTimeChange={setEndTime}
            onForecastHorizonChange={setForecastHorizonHours}
            onSubmit={handleSubmit}
          />
        </section>

        <section className="panel">
          <h2>Summary</h2>
          {loading && <p className="panel-copy">Loading generation data...</p>}

          {!loading && error && <p className="panel-copy">{error}</p>}

          {!loading && !error && !responseData && (
            <p className="panel-copy">
              Submit the form to load backend data into the page state.
            </p>
          )}

          {!loading && !error && responseData && (
            <div className="response-preview">
              <p className="panel-copy">
                Response received successfully. Data points:{" "}
                {responseData.data.length}
              </p>
            </div>
          )}
        </section>

        <section className="panel panel-large">
          <h2>Chart</h2>
          <p className="panel-copy">
            Actual and forecast generation are plotted across the selected time
            range. Missing forecast values remain unconnected.
          </p>
          {!loading && !error && <GenerationChart data={responseData?.data ?? []} />}
        </section>
      </main>
    </div>
  );
}

export default App;
