import pytest
from unittest.mock import patch
from server import get_weather_tool, format_weather_data


@pytest.fixture
def mock_weather_response():
    """Mock weather API response."""
    return {
        "name": "London",
        "weather": [{"description": "scattered clouds"}],
        "main": {
            "temp": 15.5,
            "humidity": 75
        },
        "wind": {
            "speed": 3.2
        }
    }


class TestWeatherFunctions:
    
    def test_format_weather_data(self, mock_weather_response):
        """Test weather data formatting."""
        formatted = format_weather_data(mock_weather_response)
        
        assert "London" in formatted
        assert "scattered clouds" in formatted
        assert "15.5°C" in formatted
        assert "75%" in formatted
        assert "3.20 m/s" in formatted
    
    def test_format_weather_data_missing_fields(self):
        """Test weather data formatting with missing fields."""
        incomplete_data = {"name": "TestCity"}
        formatted = format_weather_data(incomplete_data)
        
        assert "TestCity" in formatted
        assert "Unknown" in formatted  # For missing weather description
        assert "0°C" in formatted      # For missing temperature
    
    @pytest.mark.asyncio
    @patch('server.get_weather_from_openweathermap')
    async def test_get_weather_tool_success(self, mock_get_weather, mock_weather_response):
        """Test successful get_weather_tool call."""
        mock_get_weather.return_value = mock_weather_response
        
        result = await get_weather_tool("London")
        
        assert "London" in result
        assert "scattered clouds" in result
        assert "15.5°C" in result
        mock_get_weather.assert_called_once_with("London")
    
    @pytest.mark.asyncio
    @patch('server.get_weather_from_openweathermap')
    async def test_get_weather_tool_error(self, mock_get_weather):
        """Test get_weather_tool with API error."""
        mock_get_weather.return_value = {"error": "API Error occurred"}
        
        result = await get_weather_tool("InvalidCity")
        
        assert "error" in result.lower()
        assert "api error occurred" in result.lower()
        mock_get_weather.assert_called_once_with("InvalidCity")
    
    @pytest.mark.asyncio
    @patch('server.get_weather_from_openweathermap')
    async def test_get_weather_tool_no_api_key(self, mock_get_weather):
        """Test get_weather_tool without API key."""
        mock_get_weather.return_value = {"error": "OpenWeatherMap API key not set. Please set the OPENWEATHER_API_KEY environment variable."}
        
        result = await get_weather_tool("London")
        
        assert "api key not set" in result.lower()
        mock_get_weather.assert_called_once_with("London")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 