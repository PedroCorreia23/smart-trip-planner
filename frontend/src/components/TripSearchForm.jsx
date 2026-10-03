import { useState } from "react";
import { FaLocationDot } from "react-icons/fa6";
import { FaCalendarDays } from "react-icons/fa6";

export default function TripSearchForm() {
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
                    <input
                        id="departure-date"
                        type="date"
                        className="date-input"
                    />
                </div>
            </div>
            <div className="input-group">
                <label htmlFor="arrival-date"> Arrival Date</label>
                <div className="input-with-icon">
                    <FaCalendarDays className="date-icon" />
                    <input
                        id="arrival-date"
                        type="date"
                        className="date-input"
                    />
                </div>
            </div>
        </div>
    </main>
  );
}

