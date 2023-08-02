import pytest
import requests

from api_calls import query_ensemble_api


def test_empty_variants():
    response, error = query_ensemble_api([])
    assert len(response) == 0
    assert error[0].get("error_description") == "No variants were given."


def test_nonexistant_genes():
    """Test the api response with fake genes and check that errors are being caught."""
    fake_genes = ["aaaaa", "bbbbb", "cccc"]
    response, error = query_ensemble_api(fake_genes)
    assert len(response) == 0
    assert len(error) == 3


def test_http_exception():
    with pytest.raises(requests.exceptions.HTTPError) as http_error:
        raise requests.exceptions.HTTPError("Http Error")
    assert http_error.value.args[0] == "Http Error"


def test_connection_exception():
    with pytest.raises(requests.exceptions.ConnectionError) as connection_error:
        raise requests.exceptions.ConnectionError("Connection Error")
    assert connection_error.value.args[0] == "Connection Error"


def test_timeout_exception():
    with pytest.raises(requests.exceptions.Timeout) as timeout_error:
        raise requests.exceptions.Timeout("Timeout Error")
    assert timeout_error.value.args[0] == "Timeout Error"


def test_request_exception():
    with pytest.raises(requests.exceptions.RequestException) as request_error:
        raise requests.exceptions.RequestException("Request Error")
    assert request_error.value.args[0] == "Request Error"
