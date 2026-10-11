import { useState } from "react"
import "./App.css"
import TripSearchForm from "./components/TripSearchForm"
import TripResults  from "./components/TripResults"

export default function Home() {
    const [tripResult, setTripResult] = useState(null)
    const [loadingState, setLoadingState] = useState(false)

    return (
        <div className="home-page">
            <TripSearchForm setTripResult={setTripResult}
                            loadingState={loadingState}
                            setLoadingState={setLoadingState} />
            {tripResult && (
              <TripResults tripResult={tripResult}/>
            )}
        </div>
    )
}