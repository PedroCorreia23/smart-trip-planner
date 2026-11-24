
function formatItineraryDate(dateString) {
    const date = new Date(`${dateString}T00:00:00Z`)

    return new Intl.DateTimeFormat("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
        timeZone: "UTC",
    }).format(date)
}
export default function ItineraryResults({itinerary, selectedDay, onSelectDay, }) {
    if (!itinerary?.days) {
        return null
    }

    return (
        <section
            className="itinerary-results"
            aria-labelledby="itinerary-title"
        >
            <div className="itinerary-results-header">
                <h2 id="itinerary-title">Your Itinerary</h2>

                <p>
                    {itinerary.days.length} days planned
                </p>
            </div>

            <div className="itinerary-days">
                {itinerary.days.map((day, index) => (
                    <article
                        key={day.day}
                        className="itinerary-day"
                    >
                    <button
                        type="button"
                        className={`itinerary-day-header itinerary-day-select ${
                            selectedDay === index ? "itinerary-day--active" : ""
                        }`}
                        onClick={() => onSelectDay(index)}
                        aria-pressed={selectedDay === index}
                    >
                        <div>
                            <h3>Day {index + 1}</h3>

                            <p className="itinerary-date">
                                {formatItineraryDate(day.day)}
                            </p>
                        </div>

                        <span className="itinerary-day-count">
                            {day.pois.length}{" "}
                            {day.pois.length === 1 ? "place" : "places"}
                        </span>
                    </button>

                        {day.pois.length === 0 ? (
                            <p className="itinerary-empty">
                                No places planned for this day.
                            </p>
                        ) : (
                            <ol className="itinerary-poi-list">
                                {day.pois.map((poi, poiIndex) => (
                                    <li
                                        key={poi.id}
                                        className="itinerary-poi"
                                    >
                                        <span
                                            className="itinerary-poi-number"
                                            aria-hidden="true"
                                        >
                                            {poiIndex + 1}
                                        </span>

                                        <div className="itinerary-poi-info">
                                            <h4>{poi.name}</h4>
                                            <p>{poi.category}</p>
                                        </div>

                                        {poi.image_url && (
                                            <img
                                                className="itinerary-poi-image"
                                                src={poi.image_url}
                                                alt={poi.name}
                                                loading="lazy"
                                            />
                                        )}
                                    </li>
                                ))}
                            </ol>
                        )}
                    </article>
                ))}
            </div>
        </section>
    )
}
