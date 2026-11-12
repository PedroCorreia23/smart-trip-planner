import { useState, useEffect, useRef } from "react"
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

    const [poiCategory, setPoiCategory] = useState("museum")

    const poiCache = useRef({})

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
                const response = await fetch(url, {signal: controller.signal})
                
                if (!response.ok) {
                    let errorMessage = "An unexpected error occurred."

                    try {
                        const errorData = await response.json()
                        errorMessage = errorData.detail || errorMessage

                        
                    } catch {
                        // Keep the default error message if JSON parsing fails

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
                
            }finally {
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

                    <POIResults
                        pois={poiResults}
                        category={poiCategory}
                        onCategoryChange={setPoiCategory}
                        loading={poiLoading}
                        error={poiError}
                    />
                </>
            )}
        </div>
    )
}