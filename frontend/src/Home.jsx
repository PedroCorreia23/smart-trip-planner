import { useState } from "react"
import "./App.css"
import TripSearchForm from "./components/TripSearchForm"
import TripResults  from "./components/TripResults"

export default function Home() {
    const [tripResult, setTripResult] = useState(null)
    const [loadingState, setLoadingState] = useState(false)
    const [errorState, setErrorState] = useState(null)

    const [poiResults, setPoiResults] = useState([])
    const [poiLoading, setPoiLoading] = useState(false)
    const [poiError, setPoiError] = useState(null)

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
              <TripResults tripResult={tripResult}/>
            )}
        </div>
    )
}