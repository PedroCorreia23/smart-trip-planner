import { useState, useEffect } from "react"
import "./App.css"
import TripSearchForm from "./components/TripSearchForm"
import TripResults  from "./components/TripResults"
import POIResults from "./components/POIResults"

export default function Home() {
    const [tripResult, setTripResult] = useState(null)
    const [loadingState, setLoadingState] = useState(false)
    const [errorState, setErrorState] = useState(null)

    const [poiResults, setPoiResults] = useState([])
    const [poiLoading, setPoiLoading] = useState(false)
    const [poiError, setPoiError] = useState(null)

    useEffect(() => {
        if (!tripResult) {
            return
        }

        const lat = tripResult.destination_coordinates.lat
        const lon = tripResult.destination_coordinates.lon

        const fetchPOIs = async () => {

            try {

                setPoiLoading(true)
                setPoiError(null)
                setPoiResults([])

                const url = `${import.meta.env.VITE_API_BASE_URL}/pois?lat=${lat}&lon=${lon}&radius=5000`
                const response = await fetch(url)

                if (!response.ok) {
                    const poiError = await response.json()
                    throw new Error(poiError.detail || "An unexpected error occurred.")
                }
                if (!tripResult) {
                    setPoiResults([])
                    setPoiError(null)
                    return
                }

                const data = await response.json()
                setPoiResults(data)

            } catch (error) {
                console.error("Failed to fetch POIs:", error)
                setPoiError(error.message)
            }finally {
                setPoiLoading(false) 
        }
        fetchPOIs()
        }
    }, [tripResult])
  
    return (
        <div className="home-page">
            <TripSearchForm setTripResult={setTripResult}
                            loadingState={loadingState}
                            setLoadingState={setLoadingState}
                            setErrorState={setErrorState} />
            
            {errorState && (
                <p className="error-message" role="alert">
                    {errorState}
                </p>
            )}
            {tripResult && (
                <>
                    <TripResults tripResult={tripResult} />

                    {poiLoading && <p role="status">Loading places...</p>}

                    {poiError && <p role="alert">{poiError}</p>}

                    {!poiLoading && !poiError && (
                        <POIResults pois={poiResults} />
                    )}
                </>
            )}
        </div>
    )
}