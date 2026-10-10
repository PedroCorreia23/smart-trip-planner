export default function TripResults({ tripResult }) {
  return (
        <div className="results">
            <h2>Trip Results</h2>
            <p>Origin: {tripResult.trip_details.origin}</p>
            <p>Destination: {tripResult.trip_details.destination}</p>
            <p>Start Date: {tripResult.trip_details.start_date}</p>
            <p>End Date: {tripResult.trip_details.end_date}</p>
            <p>1 {tripResult.origin_currency.code} = {tripResult.exchange_rate.rate} {tripResult.destination_currency.code}</p>
        </div>
  );
}


