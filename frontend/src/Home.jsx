import { useState } from "react"
import "./App.css"
import TripSearchForm from "./components/TripSearchForm"

export default function Home() {
    const [tripResult, setTripResult] = useState(null)

    return (
        <div className="home-page">
            <TripSearchForm setTripResult={setTripResult} />
        </div>
    )
}