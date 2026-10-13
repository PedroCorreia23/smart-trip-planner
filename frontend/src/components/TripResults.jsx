import WeatherIcon from "./WeatherIcon";
import moment from "moment";

export default function TripResults({ tripResult }) {
  return (
        <div className="results">
          <h2>Weather Forecast</h2>
          <div className="weather">
            {tripResult.weather.time.map((date, index) => (
              <div className="weather-card" key={date}>
                <p>{moment(date, "YYYY-MM-DD").format("DD MMM")}</p>

                <WeatherIcon code={tripResult.weather.weather_code[index]} />

                <p>Max: {tripResult.weather.temperature_2m_max[index]} ºC</p>
                <p>Min: {tripResult.weather.temperature_2m_min[index]} ºC</p>
                <p>Precipitation: {tripResult.weather.precipitation_sum[index] }  mm</p>
              </div>
            ))}
          </div>
          <div className="currency">
            <p>1 {tripResult.origin_currency.code} = {tripResult.exchange_rate.rate} {tripResult.destination_currency.code}</p>
          </div>
      </div>
  );
}


