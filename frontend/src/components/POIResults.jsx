export default function POIResults({ pois }) {
  return (
    <section className="poi-results">
      <h2>Places to Visit</h2>

      {pois.length === 0 ? (
        <p>No places found near this destination.</p>
      ) : (
        pois.map((poi) => (
          <div key={poi.id}>
            <h3>{poi.name}</h3>
            <p>{poi.category}</p>
          </div>
        ))
      )}
    </section>
  );
}