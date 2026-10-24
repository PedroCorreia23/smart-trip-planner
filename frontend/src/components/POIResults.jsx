export default function POIResults({ pois }) {
  return (
    <section className="poi-results">
      <h2>Places to Visit</h2>
      <p>{pois.length} places found</p>
    </section>
  );
}