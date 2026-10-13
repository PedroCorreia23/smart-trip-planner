import {
  WiDaySunny,
  WiDayCloudy,
  WiCloudy,
  WiFog,
  WiRain,
  WiSnow,
  WiThunderstorm,
  WiNa,
} from "react-icons/wi";

import { getWeatherCondition } from "../utils/weatherUtils";

const weatherIcons = {
  sunny: WiDaySunny,
  "partly-cloudy": WiDayCloudy,
  cloudy: WiCloudy,
  foggy: WiFog,
  rainy: WiRain,
  snowy: WiSnow,
  stormy: WiThunderstorm,
  unknown: WiNa,
};

export default function WeatherIcon({ code }) {
  const condition = getWeatherCondition(code);
  const Icon = weatherIcons[condition] ?? WiNa;

  return (
    <Icon
      className="weather-icon"
      role="img"
      aria-label={condition.replaceAll("-", " ")}
    />
  );
}