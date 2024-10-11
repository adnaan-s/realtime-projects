import unittest
from unittest.mock import patch, MagicMock
from ..scraper import yahoo_search, continuous_scraping, news_cache  # Adjusted import

class TestYahooSearch(unittest.TestCase):

    @patch('scraper.requests.get')
    def test_yahoo_search_success(self, mock_get):
        # Mocking a successful response from Yahoo search
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <body>
            <h3 class="title">Forex Market Hits New Highs</h3>
            <h3 class="title">Euro Gains Against Dollar</h3>
            <h3 class="title">Forex Trends to Watch</h3>
            <h3 class="title">Impact of Inflation on Forex</h3>
            <h3 class="title">Central Banks and Forex Trading</h3>
        </body>
        </html>
        '''
        mock_get.return_value = mock_response

        results = yahoo_search('EURUSD')
        self.assertEqual(len(results), 5)
        self.assertIn('Forex Market Hits New Highs', results)
        self.assertIn('Euro Gains Against Dollar', results)

    @patch('scraper.requests.get')
    def test_yahoo_search_no_results(self, mock_get):
        # Mocking a response with no results
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <body></body>
        </html>
        '''
        mock_get.return_value = mock_response

        results = yahoo_search('EURUSD')
        self.assertEqual(results, [])

    @patch('scraper.requests.get')
    def test_yahoo_search_request_exception(self, mock_get):
        # Mocking a request exception
        mock_get.side_effect = Exception("Network Error")

        results = yahoo_search('EURUSD')
        self.assertEqual(results, [])

class TestContinuousScraping(unittest.TestCase):

    @patch('scraper.yahoo_search')
    def test_continuous_scraping(self, mock_yahoo_search):
        # Mocking the yahoo_search function
        mock_yahoo_search.return_value = ['News 1', 'News 2']
        
        continuous_scraping()
        
        self.assertIn('EURUSD', news_cache)
        self.assertEqual(len(news_cache['EURUSD']), 2)

if __name__ == '__main__':
    unittest.main()
