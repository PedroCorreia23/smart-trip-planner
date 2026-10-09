export default function TripResults({ tripResult }) {
  return (
        <div className="results">
            <h2>Trip Results</h2>
            <p>Origin: {tripResult.trip_details.origin}</p>
            <p>Destination: {tripResult.trip_details.destination}</p>
        </div>
  );
}


