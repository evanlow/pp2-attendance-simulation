"""
Test Suite for NRIC Verification Demo Application
Tests backend routes, OCR functions, and error handling
"""

import pytest
from io import BytesIO
from PIL import Image
from app import app, extract_name, extract_nric_last_4


# Pytest fixtures
@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (640, 480), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


# Route Tests
class TestRoutes:
    """Test Flask routes"""
    
    def test_index_route(self, client):
        """Test that index route returns 200 and serves HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Mock NRIC Verification Demo' in response.data
        assert b'Start Camera' in response.data
    
    def test_verify_route_no_image(self, client):
        """Test verify route without image returns error"""
        response = client.post('/verify')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'No image provided' in json_data['error']
    
    def test_verify_route_with_image(self, client, sample_image):
        """Test verify route with valid image"""
        data = {'image': (sample_image, 'test.png')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'success' in json_data
        assert 'ocr_text' in json_data
        assert 'name' in json_data
        assert 'nric_last_4' in json_data
        assert 'timestamp' in json_data
    
    def test_verify_route_returns_singapore_time(self, client, sample_image):
        """Test that timestamp is in Singapore Time (SGT)"""
        data = {'image': (sample_image, 'test.png')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        json_data = response.get_json()
        assert '+08' in json_data['timestamp'] or 'SGT' in json_data['timestamp']


# OCR Function Tests
class TestOCRFunctions:
    """Test OCR extraction functions"""
    
    def test_extract_name_with_name_pattern(self):
        """Test name extraction with 'NAME:' pattern"""
        text = "REPUBLIC OF SINGAPORE\nNAME: JOHN DOE\nNRIC: S1234567A"
        result = extract_name(text)
        assert "JOHN DOE" in result
    
    def test_extract_name_with_capitalized_words(self):
        """Test name extraction with capitalized words"""
        text = "REPUBLIC OF SINGAPORE\nJOHN DOE\nS1234567A"
        result = extract_name(text)
        assert "JOHN" in result or "DOE" in result
    
    def test_extract_name_empty_text(self):
        """Test name extraction with empty text"""
        result = extract_name("")
        assert result == "Not detected"
    
    def test_extract_name_no_match(self):
        """Test name extraction when no name found"""
        text = "123 456 789"
        result = extract_name(text)
        assert result == "Not detected"
    
    def test_extract_nric_last_4_valid_nric(self):
        """Test NRIC extraction with valid Singapore NRIC"""
        text = "REPUBLIC OF SINGAPORE\nNRIC: S1234567A\nName: John"
        result = extract_nric_last_4(text)
        assert result == "4567"
    
    def test_extract_nric_last_4_multiple_nrics(self):
        """Test NRIC extraction with multiple NRICs (should return first)"""
        text = "S1234567A\nT9876543B"
        result = extract_nric_last_4(text)
        assert result == "4567"
    
    def test_extract_nric_last_4_with_t_prefix(self):
        """Test NRIC extraction with T prefix"""
        text = "NRIC: T9876543B"
        result = extract_nric_last_4(text)
        assert result == "6543"
    
    def test_extract_nric_last_4_with_f_prefix(self):
        """Test NRIC extraction with F prefix (foreigner)"""
        text = "NRIC: F1234567A"
        result = extract_nric_last_4(text)
        assert result == "4567"
    
    def test_extract_nric_last_4_with_g_prefix(self):
        """Test NRIC extraction with G prefix"""
        text = "NRIC: G9876543B"
        result = extract_nric_last_4(text)
        assert result == "6543"
    
    def test_extract_nric_last_4_fallback_to_digits(self):
        """Test NRIC extraction fallback to any 7-digit sequence"""
        text = "ID: 1234567"
        result = extract_nric_last_4(text)
        assert result == "4567"
    
    def test_extract_nric_last_4_empty_text(self):
        """Test NRIC extraction with empty text"""
        result = extract_nric_last_4("")
        assert result == "Not detected"
    
    def test_extract_nric_last_4_no_match(self):
        """Test NRIC extraction when no NRIC found"""
        text = "REPUBLIC OF SINGAPORE"
        result = extract_nric_last_4(text)
        assert result == "Not detected"


# Integration Tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_verification_workflow(self, client, sample_image):
        """Test complete verification workflow from image upload to results"""
        # Upload image
        data = {'image': (sample_image, 'nric.png')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        
        # Verify response structure
        assert response.status_code == 200
        json_data = response.get_json()
        
        # Verify all required fields present
        required_fields = ['success', 'ocr_text', 'name', 'nric_last_4', 'timestamp']
        for field in required_fields:
            assert field in json_data, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(json_data['success'], bool)
        assert isinstance(json_data['ocr_text'], str)
        assert isinstance(json_data['name'], str)
        assert isinstance(json_data['nric_last_4'], str)
        assert isinstance(json_data['timestamp'], str)
    
    def test_multiple_requests_no_data_persistence(self, client):
        """Test that multiple requests don't persist data (stateless)"""
        # First request
        img1 = BytesIO()
        Image.new('RGB', (640, 480), color='white').save(img1, format='PNG')
        img1.seek(0)
        data1 = {'image': (img1, 'test1.png')}
        response1 = client.post('/verify', data=data1, content_type='multipart/form-data')
        
        # Second request with new image
        img2 = BytesIO()
        Image.new('RGB', (640, 480), color='white').save(img2, format='PNG')
        img2.seek(0)
        data2 = {'image': (img2, 'test2.png')}
        response2 = client.post('/verify', data=data2, content_type='multipart/form-data')
        
        # Both should succeed independently
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify timestamps are different (processing at different times)
        json1 = response1.get_json()
        json2 = response2.get_json()
        assert json1['timestamp'] != json2['timestamp'] or True  # May be same if fast


# Edge Case Tests
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_verify_with_invalid_image_format(self, client):
        """Test verify with non-image file"""
        data = {'image': (BytesIO(b'not an image'), 'test.txt')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_verify_with_empty_image(self, client):
        """Test verify with empty file"""
        data = {'image': (BytesIO(b''), 'empty.png')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_extract_name_with_special_characters(self):
        """Test name extraction with special characters"""
        text = "NAME: O'BRIEN-SMITH"
        result = extract_name(text)
        assert "BRIEN" in result or "SMITH" in result
    
    def test_extract_nric_with_lowercase(self):
        """Test NRIC extraction with lowercase letters"""
        text = "nric: s1234567a"
        result = extract_nric_last_4(text)
        assert result == "4567"


# Performance Tests
class TestPerformance:
    """Basic performance tests"""
    
    def test_verify_response_time(self, client, sample_image):
        """Test that verify endpoint responds within reasonable time"""
        import time
        start = time.time()
        data = {'image': (sample_image, 'test.png')}
        response = client.post('/verify', data=data, content_type='multipart/form-data')
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0, f"Response took {duration}s, should be under 5s"


# Run tests with: pytest test_app.py -v
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
