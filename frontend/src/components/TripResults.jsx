export default function TripResults({ tripResult }) {
  return (
        <div className="results">
            <h2>Trip Results</h2>
            <p>Origin: {tripResult.trip_details.origin}</p>
            <p>Destination: {tripResult.trip_details.destination}</p>
            <p>Start Date: {tripResult.trip_details.start_date}</p>
            <p>End Date: {tripResult.trip_details.end_date}</p>
            <p>1 {tripResult.origin_currency.code} = {tripResult.exchange_rate.rate} {tripResult.destination_currency.code}</p>
            {tripResult.weather.time.map((date, index) => (
              <div key={date}>
                <h6>{date}</h6>
                <h6>Max: {tripResult.weather.temperature_2m_max[index]} ºC</h6>
                <h6>Min: {tripResult.weather.temperature_2m_min[index]} ºC</h6>
                <h6>Precipitation: {tripResult.weather.precipitation_sum[index] }  mm</h6>
              </div>
            ))}
        </div>
  );
}


