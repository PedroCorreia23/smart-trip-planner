export default function TripResults({ tripResult }) {
  return (
        <div className="results">
          <div className="weather">
            <h2>Weather Forecast</h2>
            {tripResult.weather.time.map((date, index) => (
              <div key={date}>
                <p>{date}</p>
                <p>Max: {tripResult.weather.temperature_2m_max[index]} ºC</p>
                <p>Min: {tripResult.weather.temperature_2m_min[index]} ºC</p>
                <p>Precipitation: {tripResult.weather.precipitation_sum[index] }  mm</p>
              </div>
            ))}
          </div>
          <div className="currency">
            <p>1 {tripResult.origin_currency.code} = {tripResult.exchange_rate.rate} {tripResult.destination_currency.code}</p>
          </div>
      </div>
  );
}


