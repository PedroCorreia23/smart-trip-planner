import pytest
from unittest.mock import patch, Mock
from app.services.exchange_rate import ExchangeRateService

# O decorador avisa o Pytest que esta função usa "await"
@pytest.mark.asyncio
async def test_get_rate_success():
    # 1. ARRANGE (Preparar): Os dados falsos que a API devolveria
    fake_api_response = {"date":"2026-09-27","base":"EUR","quote":"USD","rate":1.1398}
    
    # Criamos uma resposta HTTP falsa (AsyncMock) e dizemos-lhe o que devolver quando chamarem .json()
    mock_response = Mock()
    mock_response.json.return_value = fake_api_response
    
    # 2. ACT (Agir): Intercetamos o httpx.AsyncClient.get e forçamos a usar a nossa resposta falsa
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = ExchangeRateService()
        
        # O nosso código acha que está a ir à Internet, mas o 'patch' prendeu-o dentro do nosso teste!
        resultado = await service.get_rate("EUR","USD")
        
    # 3. ASSERT (Validar): Verificamos se o nosso código extraiu e converteu bem os dados falsos
    assert resultado == {"base":"EUR","target":"USD","rate":1.1398}

@pytest.mark.asyncio
async def test_get_rate_not_found():

        # 1. ARRANGE (Preparar): Os dados falsos que a API devolveria
    fake_api_response = {"date":"2026-09-27","base":"EUR","quote":"USD","rate": None} 
    
    # Criamos uma resposta HTTP falsa (AsyncMock) e dizemos-lhe o que devolver quando chamarem .json()
    mock_response = Mock()
    mock_response.json.return_value = fake_api_response
    
    # 2. ACT (Agir): Intercetamos o httpx.AsyncClient.get e forçamos a usar a nossa resposta falsa
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = ExchangeRateService()
        
        # O nosso código acha que está a ir à Internet, mas o 'patch' prendeu-o dentro do nosso teste!
        resultado = await service.get_rate("EUR","USD")

    assert resultado is None