export function getWeatherCondition(code) {
  if (code === 0) {
    return "sunny";
  }

  if (code === 1 || code === 2) {
    return "partly-cloudy";
  }

  if (code === 3) {
    return "cloudy";
  }

  if (code === 45 || code === 48) {
    return "foggy";
  }

  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
    return "rainy";
  }

  if ((code >= 71 && code <= 77) || code === 85 || code === 86) {
    return "snowy";
  }

  if (code >= 95 && code <= 99) {
    return "stormy";
  }

  return "unknown";
}