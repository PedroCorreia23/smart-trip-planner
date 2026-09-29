import pytest, httpx
from unittest.mock import patch, Mock
from app.services.exchange_rate import ExchangeRateService
from app.exceptions import ExternalServiceError
from app.domain.schemas import ExchangeRateInfo

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
    assert resultado == ExchangeRateInfo(base="EUR", target="USD", rate=1.1398)

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

@pytest.mark.asyncio
async def test_get_rate_http_error():
    request = httpx.Request("GET", "https://api.frankfurter.dev/v2/rate/EUR/USD")

    response = httpx.Response(500, request=request)

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server error", request=request,response=response)

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        service = ExchangeRateService()
        with pytest.raises(ExternalServiceError):
            await service.get_rate("EUR", "USD")

@pytest.mark.asyncio
async def test_get_rate_network_error():

    request = httpx.Request(
        "GET",
        "https://api.frankfurter.dev/v2/rate/EUR/USD"
    )

    with patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.RequestError(
            "Network error",
            request=request
        )
    ):
        service = ExchangeRateService()

        with pytest.raises(ExternalServiceError):
            await service.get_rate("EUR", "USD")