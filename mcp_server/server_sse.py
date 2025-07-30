import os
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Any
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="weather-sse"
)

async def get_weather_from_openweathermap(city: str) -> dict[str, Any]:
    """Get the weather forecast for a city using OpenWeatherMap API."""
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not OPENWEATHER_API_KEY:
        return {"error": "OpenWeatherMap API key not set. Please set the OPENWEATHER_API_KEY environment variable."}
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": f"Failed to get weather for {city}: {e}"}

def format_weather_data(weather_data: dict[str, Any]) -> str:
    """Format the weather data into a more readable string."""
    return f"""
        City: {weather_data.get('name', 'Unknown')}
        Weather: {weather_data.get('weather', [{}])[0].get('description', 'Unknown')}
        Temperature: {weather_data.get('main', {}).get('temp', 0)}°C
        Humidity: {weather_data.get('main', {}).get('humidity', 0)}%
        Wind Speed: {weather_data.get('wind', {}).get('speed', 0):.2f} m/s
        """

@mcp.tool()
async def get_weather_tool(city: str) -> str:
    """Get the weather forecast for a city using OpenWeatherMap API."""
    try:
        weather_data = await get_weather_from_openweathermap(city)
        if "error" in weather_data:
            return f"Error: {weather_data['error']}"
        return format_weather_data(weather_data)
    except Exception as e:
        return f"Error: Failed to get weather for {city}: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse") 