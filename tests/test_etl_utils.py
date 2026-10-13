import unittest
from unittest.mock import Mock, patch

import pandas as pd

from etl_utils import importar_datos, transformar


class ImportarDatosTests(unittest.TestCase):
    @patch("etl_utils.requests.get")
    def test_importar_datos_uses_timeout_and_returns_records(self, mock_get):
        response = Mock()
        response.json.return_value = [{"date": 20210102}]
        mock_get.return_value = response

        result = importar_datos("https://example.test/data", timeout=12)

        mock_get.assert_called_once_with("https://example.test/data", timeout=12)
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(result, [{"date": 20210102}])

    @patch("etl_utils.requests.get")
    def test_importar_datos_rejects_non_list_payload(self, mock_get):
        response = Mock()
        response.json.return_value = {"data": []}
        mock_get.return_value = response

        with self.assertRaisesRegex(ValueError, "lista de registros"):
            importar_datos("https://example.test/data")


class TransformarTests(unittest.TestCase):
    def test_transformar_sorts_dates_and_maps_daily_metrics(self):
        records = [
            {"date": 20210102, "positiveIncrease": 20, "deathIncrease": 2},
            {"date": 20210101, "positiveIncrease": 10, "deathIncrease": 1},
        ]

        result = transformar(records)

        expected_dates = list(pd.to_datetime(["2021-01-01", "2021-01-02"]))
        self.assertEqual(result["date"].tolist(), expected_dates)
        self.assertEqual(result["daily_cases"].tolist(), [10, 20])
        self.assertEqual(result["daily_deaths"].tolist(), [1, 2])

    def test_transformar_returns_expected_empty_frame(self):
        result = transformar([])

        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns), ["date", "daily_cases", "daily_deaths"]
        )

    def test_transformar_rejects_missing_required_fields(self):
        with self.assertRaisesRegex(ValueError, "positiveIncrease"):
            transformar([{"date": 20210101, "deathIncrease": 1}])


if __name__ == "__main__":
    unittest.main()
