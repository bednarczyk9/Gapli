import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the pipeline module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline.repair_missing_descriptions import fetch_products_missing_descriptions, repair_missing_description

class TestRepairMissingDescriptions(unittest.TestCase):

    @patch('pipeline.repair_missing_descriptions.requests.get')
    def test_fetch_products_missing_descriptions_filtering(self, mock_get):
        # We need to mock responses for two statuses: ACTIVE and PENDING
        # We will configure side_effect to return different mocks per call
        
        mock_response_active = MagicMock()
        mock_response_active.status_code = 200
        mock_response_active.json.return_value = {
            "products": [
                # 1. Has both zero stock and missing desc -> SKIP
                {"id": 1, "sku": "ZERO_STOCK", "gapli_product_stock_quantity": 0, "allegro_offer_description": None, "allegro_catalog_description": None},
                
                # 2. Has stock, but ALREADY has offer description -> SKIP
                {"id": 2, "sku": "HAS_OFFER_DESC", "gapli_product_stock_quantity": 5, "allegro_offer_description": {"sections": []}, "allegro_catalog_description": None},
                
                # 3. Has stock, but ALREADY has catalog description -> SKIP
                {"id": 3, "sku": "HAS_CATALOG_DESC", "gapli_product_stock_quantity": 5, "allegro_offer_description": None, "allegro_catalog_description": {"sections": []}},
                
                # 4. Has stock, missing both descriptions -> KEEP
                {"id": 4, "sku": "NEEDS_REPAIR", "gapli_product_stock_quantity": 10, "allegro_offer_description": None, "allegro_catalog_description": None}
            ],
            "totalPages": 1
        }
        
        mock_response_empty = MagicMock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = {"products": [], "totalPages": 1}

        # First call is for ACTIVE, second is for PENDING
        mock_get.side_effect = [mock_response_active, mock_response_empty]

        result = fetch_products_missing_descriptions(61)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sku"], "NEEDS_REPAIR")

    @patch('pipeline.repair_missing_descriptions.time.sleep')
    @patch('pipeline.repair_missing_descriptions.send_to_allegro')
    @patch('pipeline.repair_missing_descriptions.update_customization')
    @patch('pipeline.repair_missing_descriptions.rewrite_with_gemini')
    @patch('pipeline.repair_missing_descriptions.get_mandatory_params')
    def test_repair_missing_description_success_flow(self, mock_get_params, mock_gemini, mock_update_cust, mock_send, mock_sleep):
        mock_get_params.return_value = [{"name": "Stan", "type": "dictionary", "dictionary": ["Nowy"]}]
        mock_gemini.return_value = {
            "name": "Fixed Name",
            "description": "<p>Fixed desc</p>",
            "short_description": "Short",
            "tags": ["a", "b"],
            "meta_title": "Title",
            "meta_description": "Desc",
            "parameters": {"Stan": "Nowy"}
        }
        mock_update_cust.return_value = True
        mock_send.return_value = True

        dummy_product = {
            "sku": "NEEDS_REPAIR",
            "id": 999,
            "konto_allegro_id": 61,
            "allegro_catalog_category_id": "123",
            "gapli_product_name": "Test Product",
            "gapli_product_description": "Raw Base Desc"
        }

        # Execute
        result = repair_missing_description(dummy_product, "dummy_token")

        # Assert
        self.assertTrue(result)
        mock_get_params.assert_called_once_with("123", "dummy_token")
        mock_gemini.assert_called_once()
        mock_update_cust.assert_called_once_with("NEEDS_REPAIR", mock_gemini.return_value)
        mock_send.assert_called_once_with("NEEDS_REPAIR", 61)
        mock_sleep.assert_called_once_with(2)

if __name__ == '__main__':
    unittest.main()
