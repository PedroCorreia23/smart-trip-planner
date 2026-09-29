import pytest, httpx
from unittest.mock import patch, Mock
from app.services.currency import CurrencyService
from app.exceptions import ExternalServiceError
from app.domain.schemas import CurrencyInfo

@pytest.mark.asyncio
async def test_get_currency_success():
    # 1. ARRANGE (Preparar): Os dados falsos que a API devolveria
    fake_api_response = {"currencies": [{"code":"EUR","name":"Euro","symbol":"€"}]}
    
    # Criamos uma resposta HTTP falsa (AsyncMock) e dizemos-lhe o que devolver quando chamarem .json()
    mock_response = Mock()
    mock_response.json.return_value = fake_api_response
    
    # 2. ACT (Agir): Intercetamos o httpx.AsyncClient.get e forçamos a usar a nossa resposta falsa
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = CurrencyService()
        
        # O nosso código acha que está a ir à Internet, mas o 'patch' prendeu-o dentro do nosso teste!
        resultado = await service.get_currency("FR")
        
    # 3. ASSERT (Validar): Verificamos se o nosso código extraiu e converteu bem os dados falsos
    assert resultado == CurrencyInfo(code="EUR", name="Euro", symbol="€")

@pytest.mark.asyncio
async def test_get_currency_not_found():

        # 1. ARRANGE (Preparar): Os dados falsos que a API devolveria
    fake_api_response = {"currencies": None}
    
    # Criamos uma resposta HTTP falsa (AsyncMock) e dizemos-lhe o que devolver quando chamarem .json()
    mock_response = Mock()
    mock_response.json.return_value = fake_api_response
    
    # 2. ACT (Agir): Intercetamos o httpx.AsyncClient.get e forçamos a usar a nossa resposta falsa
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = CurrencyService()
        
        # O nosso código acha que está a ir à Internet, mas o 'patch' prendeu-o dentro do nosso teste!
        resultado = await service.get_currency("FR")

    assert resultado is None

@pytest.mark.asyncio
async def test_currency_http_error():

    request = httpx.Request("GET", "https://countries.dev/alpha/FR")

    response = httpx.Response(500, request=request)
    
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server error", request=request,response=response)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = CurrencyService()
        with pytest.raises(ExternalServiceError):
            await service.get_currency("fr")