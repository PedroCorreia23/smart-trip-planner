export default function POIResults({ pois }) {
  return (
    <section className="poi-results" aria-labelledby="poi-heading">
      <h2 id="poi-heading">Discover Places to Visit</h2>

      {pois.length === 0 ? (
        <p>No places found near this destination.</p>
      ) : (
        <div className="poi-grid">
          {pois.map((poi) => (
            <div className="poi-card" key={poi.id}>
              {poi.image_url ? (
                <img
                  className="poi-image"
                  src={poi.image_url}
                  alt={poi.name}
                  loading="lazy"
                />
              ) : (
                <p className="poi-placeholder">No image available</p>
              )}

              <h3>{poi.name}</h3>
              <p>{poi.category}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}