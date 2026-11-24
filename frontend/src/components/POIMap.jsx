
import "leaflet/dist/leaflet.css"
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import L from "leaflet"

const defaultIcon = L.divIcon({
    className: "poi-map-marker",
    html: '<span class="poi-map-marker-dot"></span>',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
})

const selectedIcon = L.divIcon({
    className: "poi-map-marker poi-map-marker--selected",
    html: '<span class="poi-map-marker-dot"></span>',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
})

const activeDayIcon = L.divIcon({
    className: "poi-map-marker poi-map-marker--active-day",
    html: '<span class="poi-map-marker-dot"></span>',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
})

export default function POIMap({
    lat,
    lon,
    pois,
    selectedPOIs,
    onTogglePOI,
    activeDayPOIs = [],
}) {
    // Include itinerary POIs even when another category is displayed
    const visiblePOIs = [...pois]

    for (const poi of activeDayPOIs) {
        if (!visiblePOIs.some((item) => item.id === poi.id)) {
            visiblePOIs.push(poi)
        }
    }

    return (
        <MapContainer
            center={[lat, lon]}
            zoom={13}
            className="poi-map"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {visiblePOIs.map((poi) => {
                const isSelected = selectedPOIs.some(
                    (selected) => selected.id === poi.id
                )

                const isActiveDay = activeDayPOIs.some(
                    (active) => active.id === poi.id
                )

                const icon = isActiveDay
                    ? activeDayIcon
                    : isSelected
                      ? selectedIcon
                      : defaultIcon

                return (
                    <Marker
                        key={poi.id}
                        position={[poi.lat, poi.lon]}
                        icon={icon}
                    >
                        <Popup>
                            <strong>{poi.name}</strong>
                            <p>{poi.category}</p>

                            <button
                                type="button"
                                onClick={() => onTogglePOI(poi)}
                            >
                                {isSelected
                                    ? "Remove from trip"
                                    : "Add to trip"}
                            </button>
                        </Popup>
                    </Marker>
                )
            })}
        </MapContainer>
    )
}
