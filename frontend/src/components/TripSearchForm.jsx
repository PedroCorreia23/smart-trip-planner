import { useState } from "react";
import { FaLocationDot } from "react-icons/fa6";
import { FaCalendarDays } from "react-icons/fa6";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export default function TripSearchForm() {

    const [departureDate, setDepartureDate] = useState(null);
    const [arrivalDate, setArrivalDate] = useState(null);
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
            </div>
        </main>
  );
}

