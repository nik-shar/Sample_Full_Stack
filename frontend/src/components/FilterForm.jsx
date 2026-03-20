import React from "react";

function FilterForm({
  startTime,
  endTime,
  forecastHorizonHours,
  onStartTimeChange,
  onEndTimeChange,
  onForecastHorizonChange,
  onSubmit,
}) {
  return (
    <form className="filter-form" onSubmit={onSubmit}>
      <div className="field-group">
        <label htmlFor="start-time">Start Time</label>
        <input
          id="start-time"
          name="start-time"
          type="datetime-local"
          value={startTime}
          onChange={(event) => onStartTimeChange(event.target.value)}
          required
        />
      </div>

      <div className="field-group">
        <label htmlFor="end-time">End Time</label>
        <input
          id="end-time"
          name="end-time"
          type="datetime-local"
          value={endTime}
          onChange={(event) => onEndTimeChange(event.target.value)}
          required
        />
      </div>

      <div className="field-group">
        <label htmlFor="forecast-horizon">Forecast Horizon (Hours)</label>
        <input
          id="forecast-horizon"
          name="forecast-horizon"
          type="number"
          min="0"
          max="48"
          value={forecastHorizonHours}
          onChange={(event) => onForecastHorizonChange(event.target.value)}
          required
        />
      </div>

      <button className="primary-button" type="submit">
        Load Data
      </button>
    </form>
  );
}

export default FilterForm;
