import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the pipeline module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline.nuke_and_repair_errors import fetch_actionable_errors, nuke_and_repair_product

class TestNukeAndRepair(unittest.TestCase):

    @patch('pipeline.nuke_and_repair_errors.requests.get')
    def test_fetch_actionable_errors_filters_zero_stock(self, mock_get):
        # Mock API response containing one product with stock=0, one with stock=5, and one with no stock field
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [
                {"id": 1, "sku": "SKU_ZERO", "gapli_product_stock_quantity": 0},
                {"id": 2, "sku": "SKU_VALID", "gapli_product_stock_quantity": 5},
                {"id": 3, "sku": "SKU_NONE"} # Should default to 0 and be filtered out
            ]
        }
        mock_get.return_value = mock_response

        # Execute
        result = fetch_actionable_errors(61)

        # Assert
        # The API is called twice (ERROR and VALIDATION_ERROR), returning the same mocked list each time.
        # So it should return 2 valid products (1 per call)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["sku"], "SKU_VALID")
        self.assertEqual(result[1]["sku"], "SKU_VALID")
        self.assertEqual(mock_get.call_count, 2)

    @patch('pipeline.nuke_and_repair_errors.time.sleep') # Prevent test from actually sleeping
    @patch('pipeline.nuke_and_repair_errors.send_to_allegro')
    @patch('pipeline.nuke_and_repair_errors.permanent_delete')
    @patch('pipeline.nuke_and_repair_errors.update_customization')
    @patch('pipeline.nuke_and_repair_errors.rewrite_with_gemini')
    @patch('pipeline.nuke_and_repair_errors.get_mandatory_params')
    def test_nuke_and_repair_product_success_flow(self, mock_get_params, mock_gemini, mock_update_cust, mock_delete, mock_send, mock_sleep):
        # Setup mocks
        mock_get_params.return_value = [{"name": "EAN (GTIN)", "type": "string"}]
        mock_gemini.return_value = {
            "name": "Fixed Name",
            "description": "<p>Fixed desc</p>",
            "short_description": "Short",
            "tags": ["a", "b"],
            "meta_title": "Title",
            "meta_description": "Desc",
            "parameters": {"EAN (GTIN)": "1234567890123"}
        }
        mock_update_cust.return_value = True
        mock_delete.return_value = True
        mock_send.return_value = True

        dummy_product = {
            "sku": "TEST_SKU",
            "id": 999,
            "konto_allegro_id": 61,
            "allegro_catalog_category_id": "123",
            "gapli_product_name": "Test Product",
            "gapli_product_description": "Test Desc"
        }

        # Execute
        result = nuke_and_repair_product(dummy_product, "dummy_token")

        # Assert
        self.assertTrue(result)
        mock_get_params.assert_called_once_with("123", "dummy_token")
        mock_gemini.assert_called_once()
        mock_update_cust.assert_called_once_with("TEST_SKU", mock_gemini.return_value)
        mock_delete.assert_called_once_with(999, 61)
        mock_send.assert_called_once_with("TEST_SKU", 61)
        mock_sleep.assert_called_once_with(2) # Checks if the database sleep delay was called

    @patch('pipeline.nuke_and_repair_errors.time.sleep')
    @patch('pipeline.nuke_and_repair_errors.send_to_allegro')
    @patch('pipeline.nuke_and_repair_errors.permanent_delete')
    @patch('pipeline.nuke_and_repair_errors.update_customization')
    @patch('pipeline.nuke_and_repair_errors.rewrite_with_gemini')
    @patch('pipeline.nuke_and_repair_errors.get_mandatory_params')
    def test_nuke_and_repair_stops_on_ai_failure(self, mock_get_params, mock_gemini, mock_update_cust, mock_delete, mock_send, mock_sleep):
        # Setup AI to return None (failure)
        mock_get_params.return_value = []
        mock_gemini.return_value = None

        dummy_product = {"sku": "TEST_SKU", "id": 999, "konto_allegro_id": 61}

        # Execute
        result = nuke_and_repair_product(dummy_product, "dummy_token")

        # Assert flow stops
        self.assertFalse(result)
        mock_update_cust.assert_not_called()
        mock_delete.assert_not_called()
        mock_send.assert_not_called()

if __name__ == '__main__':
    unittest.main()
