import { useState } from "react";
import { FaLocationDot } from "react-icons/fa6";
import { FaCalendarDays } from "react-icons/fa6";
import { FaSearchengin } from "react-icons/fa6";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import moment from "moment";

export default function TripSearchForm({ setTripResult }) {

    const [departureDate, setDepartureDate] = useState(null);
    const [arrivalDate, setArrivalDate] = useState(null);
    const [originPlace, setOriginPlace] = useState("")
    const [destinationPlace, setDestinationPlace] = useState("")

    const handleSearch = async () => {
        try {
            const trip = {
            origin: originPlace,
            destination: destinationPlace,
            start_date: moment(departureDate).format("YYYY-MM-DD"),
            end_date: moment(arrivalDate).format("YYYY-MM-DD")
            }

            const response = await fetch("http://127.0.0.1:8000/trips/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(trip)
            })

            if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`)
            }
            
            const data = await response.json()
            setTripResult(data)

        } catch (error) {
            console.error("Error searching trip:", error)
        }
    } 

    return (
        <main className="trip-search-form">
            <div className="search-box">

                <div className="input-group">
                    <label htmlFor="origin">Origin</label>
                    <div className="input-with-icon">
                        <FaLocationDot className="location-icon" />
                        <input
                            id="origin"
                            type="text"
                            value={originPlace}
                            onChange={(e) => setOriginPlace(e.target.value) }
                            placeholder="e.g. Porto, PT"
                        />
                    </div>
                </div>

                <div className="input-group">
                    <label htmlFor="destination">Destination</label>
                    <div className="input-with-icon">
                        <FaLocationDot className="location-icon" />
                        <input
                            id="destination"
                            type="text"
                            value={destinationPlace}
                            onChange={(d) => setDestinationPlace(d.target.value) }
                            placeholder="e.g. Paris, FR"
                        />
                    </div>
                </div>
                
                <div className="input-group">
                    <label htmlFor="departure-date"> Departure Date</label>
                    <div className="input-with-icon">
                        <FaCalendarDays className="date-icon" />

                        <DatePicker
                        selected={departureDate}
                        onChange={(date) => setDepartureDate(date)}
                        placeholderText="Select date"
                        dateFormat="dd/MM/yyyy"
                        className="date-input"
                        />
                    </div>
                </div>
                
                <div className="input-group">
                    <label htmlFor="arrival-date"> Arrival Date</label>
                    <div className="input-with-icon">
                        
                        <FaCalendarDays className="date-icon" />

                        <DatePicker
                        selected={arrivalDate}
                        onChange={(date) => setArrivalDate(date)}
                        placeholderText="Select date"
                        dateFormat="dd/MM/yyyy"
                        className="date-input"

                        minDate={departureDate}
                        />
                    </div>
                </div>

                <div className="input-group search-button-group">
                    <div className="input-with-icon">
                        <FaSearchengin className="date-icon" />
                        <button onClick={handleSearch}>Search Trip</button>
                    </div>
                </div>
                
                {tripResult && (
                    <div>
                        <h2>Trip Results</h2>
                        <p>Origin: {tripResult.trip_details.origin}</p>
                        <p>Destination: {tripResult.trip_details.destination}</p>
                    </div>
                )}
            </div>
        </main>
  );
}

