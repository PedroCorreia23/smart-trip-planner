import pytest
from unittest.mock import patch, Mock
from app.services.geocoding import GeocodingService

# O decorador avisa o Pytest que esta função usa "await"
@pytest.mark.asyncio
async def test_get_coordinates_success():
    # 1. ARRANGE (Preparar): Os dados falsos que a API devolveria
    fake_api_response = [{"lat": "48.8566", "lon": "2.3522", "display_name": "Paris"}]
    
    # Criamos uma resposta HTTP falsa (AsyncMock) e dizemos-lhe o que devolver quando chamarem .json()
    mock_response = Mock()
    mock_response.json.return_value = fake_api_response
    
    # 2. ACT (Agir): Intercetamos o httpx.AsyncClient.get e forçamos a usar a nossa resposta falsa
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = GeocodingService()
        
        # O nosso código acha que está a ir à Internet, mas o 'patch' prendeu-o dentro do nosso teste!
        resultado = await service.get_coordinates("Paris")
        
    # 3. ASSERT (Validar): Verificamos se o nosso código extraiu e converteu bem os dados falsos
    assert resultado == {"lat": 48.8566, "lon": 2.3522}