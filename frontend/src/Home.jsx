
import { useState, useEffect, useRef } from "react"
import "./App.css"
import TripSearchForm from "./components/TripSearchForm"
import TripResults from "./components/TripResults"
import POIResults from "./components/POIResults"
import POIMap from "./components/POIMap"
import ItineraryResults from "./components/ItineraryResults"

export default function Home() {
    const [tripResult, setTripResult] = useState(null)
    const [loadingState, setLoadingState] = useState(false)
    const [errorState, setErrorState] = useState(null)

    const [poiResults, setPoiResults] = useState([])
    const [poiLoading, setPoiLoading] = useState(false)
    const [poiError, setPoiError] = useState(null)
    const [poiCategory, setPoiCategory] = useState("museum")

    const [selectedPOIs, setSelectedPOIs] = useState([])

    // Itinerary generation states
    const [itinerary, setItinerary] = useState(null)
    const [itineraryLoading, setItineraryLoading] = useState(false)
    const [itineraryError, setItineraryError] = useState("")

    const poiCache = useRef({})
    const itineraryController = useRef(null)

    useEffect(() => {
        if (!tripResult) {
            return
        }

        const lat = tripResult.destination_coordinates.lat
        const lon = tripResult.destination_coordinates.lon
        const controller = new AbortController()
        const cacheKey = `${lat}:${lon}:5000:${poiCategory}`

        const cachedPOIs = poiCache.current[cacheKey]

        if (cachedPOIs !== undefined) {
            setPoiResults(cachedPOIs)
            setPoiLoading(false)
            setPoiError(null)
            return
        }

        const fetchPOIs = async () => {
            try {
                setPoiLoading(true)
                setPoiError(null)
                setPoiResults([])

                const url = `${import.meta.env.VITE_API_BASE_URL}/pois?lat=${lat}&lon=${lon}&radius=5000&category=${poiCategory}`

                const response = await fetch(url, {
                    signal: controller.signal,
                })

                if (!response.ok) {
                    let errorMessage = "An unexpected error occurred."

                    try {
                        const errorData = await response.json()

                        if (typeof errorData.detail === "string") {
                            errorMessage = errorData.detail
                        }
                    } catch {
                        // Keep the default error message
                    }

                    throw new Error(errorMessage)
                }

                const data = await response.json()

                if (!controller.signal.aborted) {
                    poiCache.current[cacheKey] = data
                    setPoiResults(data)
                }
            } catch (error) {
                if (controller.signal.aborted) {
                    return
                }

                console.error("Failed to fetch POIs:", error)
                setPoiError(error.message)
            } finally {
                if (!controller.signal.aborted) {
                    setPoiLoading(false)
                }
            }
        }

        fetchPOIs()

        return () => {
            controller.abort()
        }
    }, [tripResult, poiCategory])

    useEffect(() => {
        return () => {
            itineraryController.current?.abort()
        }
    }, [])

    function clearItinerary() {
        itineraryController.current?.abort()
        itineraryController.current = null

        setItinerary(null)
        setItineraryError("")
        setItineraryLoading(false)
    }

    function handleTripSuccess(data) {
        clearItinerary()
        setTripResult(data)
        setSelectedPOIs([])
    }

    function handleTogglePOI(poi) {
        clearItinerary()

        setSelectedPOIs((current) => {
            const isSelected = current.some(
                (selected) => selected.id === poi.id
            )

            if (isSelected) {
                return current.filter(
                    (selected) => selected.id !== poi.id
                )
            }

            return [...current, poi]
        })
    }

    async function handleGenerateItinerary() {
        if (
            !tripResult ||
            selectedPOIs.length === 0 ||
            itineraryLoading
        ) {
            return
        }

        const controller = new AbortController()
        itineraryController.current = controller

        setItineraryLoading(true)
        setItineraryError("")
        setItinerary(null)

        try {
            const payload = {
                start_date: tripResult.trip_details.start_date,
                end_date: tripResult.trip_details.end_date,
                pois: selectedPOIs,
            }

            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL}/itineraries/generate`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                    signal: controller.signal,
                }
            )

            if (!response.ok) {
                let errorMessage = "Failed to generate itinerary."

                try {
                    const errorData = await response.json()

                    if (typeof errorData.detail === "string") {
                        errorMessage = errorData.detail
                    }
                } catch {
                    // Keep the default error message
                }

                throw new Error(errorMessage)
            }

            const data = await response.json()

            if (!controller.signal.aborted) {
                setItinerary(data)
            }
        } catch (error) {
            if (controller.signal.aborted) {
                return
            }

            console.error("Failed to generate itinerary:", error)
            setItineraryError(error.message)
        } finally {
            if (!controller.signal.aborted) {
                setItineraryLoading(false)
                itineraryController.current = null
            }
        }
    }

    return (
        <div className="home-page">
            <TripSearchForm
                setTripResult={handleTripSuccess}
                loadingState={loadingState}
                setLoadingState={setLoadingState}
                setErrorState={setErrorState}
            />

            {errorState && (
                <p className="error-message" role="alert">
                    {errorState}
                </p>
            )}

            {tripResult && (
                <>
                    <TripResults tripResult={tripResult} />

                    <POIResults
                        pois={poiResults}
                        category={poiCategory}
                        onCategoryChange={setPoiCategory}
                        loading={poiLoading}
                        error={poiError}
                        selectedPOIs={selectedPOIs}
                        onTogglePOI={handleTogglePOI}
                    />

                    <POIMap
                        lat={tripResult.destination_coordinates.lat}
                        lon={tripResult.destination_coordinates.lon}
                        pois={poiResults}
                        selectedPOIs={selectedPOIs}
                        onTogglePOI={handleTogglePOI}
                    />

                    <section className="itinerary-generator">
                        <h2>Generate Your Itinerary</h2>

                        <p>
                            {selectedPOIs.length} places selected
                        </p>

                        <button
                            type="button"
                            onClick={handleGenerateItinerary}
                            disabled={
                                selectedPOIs.length === 0 ||
                                itineraryLoading
                            }
                        >
                            {itineraryLoading
                                ? "Generating..."
                                : "Generate Itinerary"}
                        </button>

                        {itineraryLoading && (
                            <p role="status">
                                Generating your itinerary...
                            </p>
                        )}

                        {itineraryError && (
                            <p className="error-message" role="alert">
                                {itineraryError}
                            </p>
                        )}

                        {itinerary && (
                        <>
                            <p role="status">
                                Itinerary generated successfully!
                                {" "}
                                {itinerary.days.length} days created.
                            </p>

                            <ItineraryResults itinerary={itinerary} />
                        </>
                    )}
                    </section>  
                </>
            )}
        </div>
    )
}