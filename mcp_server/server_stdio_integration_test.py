import pytest
import os
from server_stdio import get_weather_tool


class TestWeatherIntegration:
    """Integration tests for weather API - no mocking, calls real API."""
    
    @pytest.mark.asyncio
    async def test_get_weather_tool_integration_success(self):
        """Integration test: Get weather for a real city using actual API."""
        # Skip if no API key is set
        if not os.getenv("OPENWEATHER_API_KEY"):
            pytest.skip("OPENWEATHER_API_KEY not set, skipping integration test")
        
        result = await get_weather_tool("London")
        
        # Verify the response contains expected weather information
        assert "London" in result
        assert "Temperature:" in result
        assert "Humidity:" in result
        assert "Wind Speed:" in result
        assert "Weather:" in result
        assert "°C" in result
        assert "%" in result
        assert "m/s" in result
    
    @pytest.mark.asyncio
    async def test_get_weather_tool_integration_invalid_city(self):
        """Integration test: Test with invalid city name using actual API."""
        # Skip if no API key is set
        if not os.getenv("OPENWEATHER_API_KEY"):
            pytest.skip("OPENWEATHER_API_KEY not set, skipping integration test")
        
        result = await get_weather_tool("NonExistentCity12345")
        
        # Should return an error message
        assert "error" in result.lower()
        assert "failed" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 