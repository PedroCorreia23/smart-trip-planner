
const categories = [
  { value: "museum", label: "Museums" },
  { value: "monument", label: "Monuments" },
  { value: "park", label: "Parks" },
  { value: "attraction", label: "Attractions" },
]

export default function POIResults({
  pois,
  category,
  onCategoryChange,
  loading,
  error,
  selectedPOIs,
  onTogglePOI,
}) {
  const INITIAL_VISIBLE_COUNT = 6
  return (
    <section className="poi-results" aria-labelledby="poi-heading">
      <h2 id="poi-heading">Discover Places to Visit</h2>

      <div
        className="poi-category-filters"
        role="group"
        aria-label="Filter places by category"
      >
        {categories.map((item) => (
          <button
            key={item.value}
            type="button"
            className={`poi-category-button ${
              category === item.value ? "active" : ""
            }`}
            onClick={() => onCategoryChange(item.value)}
            aria-pressed={category === item.value}
          >
            {item.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="poi-loading-container" role="status">
          <p>Loading places...</p>
        </div>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : pois.length === 0 ? (
        <p>No places found near this destination.</p>
      ) : (
        <div className="poi-grid">
          {pois.slice(0, INITIAL_VISIBLE_COUNT).map((poi) => {
            const isSelected = selectedPOIs.some(
              (selected) => selected.id === poi.id
            )

            return (
              <div
                className={`poi-card ${
                  isSelected ? "poi-card--selected" : ""
                  
                }`}
                
                key={poi.id}
              >
                <div className="poi-card-select-area">
                  {isSelected && (
                    <span className="poi-selected-indicator" aria-hidden="true">
                      ✓
                    </span>
                  )}
                  {poi.image_url ? (
                    <img
                      className="poi-image"
                      src={poi.image_url}
                      alt={poi.name}
                      loading="lazy"
                    />
                  ) : (
                    <p className="poi-placeholder">
                      No image available
                    </p>
                  )}

                  <h3>{poi.name}</h3>
                  <p>{poi.category}</p>

                  <button
                    type="button"
                    className="poi-card-select-button"
                    onClick={() => onTogglePOI(poi)}
                    aria-pressed={isSelected}
                    aria-label={`${
                      isSelected ? "Deselect" : "Select"
                    } ${poi.name}`}
                  />
                </div>

                {poi.image_url && (
                  <div className="poi-attribution">
                    {poi.image_author && (
                      <p>Photo: {poi.image_author}</p>
                    )}

                    {poi.image_license && (
                      <p>License: {poi.image_license}</p>
                    )}

                    {poi.image_source_url && (
                      <a
                        href={poi.image_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View original on Wikimedia Commons
                      </a>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
