"""Unit tests for docker_validator module."""
import unittest
import mock
from ibis.utilities.docker_validator import DockerValidator


class TestDockerValidator(unittest.TestCase):
    """Test cases for DockerValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cfg_mgr = mock.MagicMock()
        self.validator = DockerValidator(self.mock_cfg_mgr)

    def test_parse_image_name_simple(self):
        """Test parsing simple image name."""
        registry, repository, tag = self.validator._parse_image_name('nginx')
        self.assertEqual(registry, 'docker.io')
        self.assertEqual(repository, 'nginx')
        self.assertEqual(tag, 'latest')

    def test_parse_image_name_with_tag(self):
        """Test parsing image name with tag."""
        registry, repository, tag = self.validator._parse_image_name('nginx:1.20')
        self.assertEqual(registry, 'docker.io')
        self.assertEqual(repository, 'nginx')
        self.assertEqual(tag, '1.20')

    def test_parse_image_name_with_registry(self):
        """Test parsing image name with custom registry."""
        registry, repository, tag = self.validator._parse_image_name('gcr.io/project/image:v1')
        self.assertEqual(registry, 'gcr.io')
        self.assertEqual(repository, 'project/image')
        self.assertEqual(tag, 'v1')

    def test_parse_image_name_user_repo(self):
        """Test parsing user/organization repository."""
        registry, repository, tag = self.validator._parse_image_name('ads-rnr/apt-ads-airflow-prod')
        self.assertEqual(registry, 'docker.io')
        self.assertEqual(repository, 'ads-rnr/apt-ads-airflow-prod')
        self.assertEqual(tag, 'latest')

    @mock.patch('ibis.utilities.docker_validator.requests.get')
    def test_get_dockerhub_metadata_success(self, mock_get):
        """Test successful Docker Hub metadata retrieval."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'latest',
            'full_size': 12345,
            'last_updated': '2023-01-01T00:00:00Z'
        }
        mock_get.return_value = mock_response

        result = self.validator._get_dockerhub_metadata('nginx', 'latest')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'latest')
        self.assertEqual(result['full_size'], 12345)
        self.assertEqual(result['repository'], 'nginx')

    @mock.patch('ibis.utilities.docker_validator.requests.get')
    def test_get_dockerhub_metadata_not_found(self, mock_get):
        """Test Docker Hub metadata retrieval for non-existent image."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.validator._get_dockerhub_metadata('nonexistent', 'latest')
        
        self.assertIsNone(result)

    @mock.patch('ibis.utilities.docker_validator.requests.get')
    def test_get_registry_metadata_success(self, mock_get):
        """Test successful registry metadata retrieval."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.validator._get_registry_metadata('gcr.io', 'project/image', 'v1')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['registry'], 'gcr.io')
        self.assertEqual(result['repository'], 'project/image')
        self.assertEqual(result['tag'], 'v1')

    @mock.patch.object(DockerValidator, '_validate_single_image')
    def test_validate_images_all_success(self, mock_validate):
        """Test validation when all images are valid."""
        mock_validate.return_value = {'status': 'success', 'image': 'test', 'metadata': {}}
        
        result = self.validator.validate_images(['image1', 'image2'])
        
        self.assertTrue(result)
        self.assertEqual(mock_validate.call_count, 2)

    @mock.patch.object(DockerValidator, '_validate_single_image')
    def test_validate_images_some_fail(self, mock_validate):
        """Test validation when some images fail."""
        mock_validate.side_effect = [
            {'status': 'success', 'image': 'image1', 'metadata': {}},
            {'status': 'failed', 'image': 'image2', 'error': 'Not found'}
        ]
        
        result = self.validator.validate_images(['image1', 'image2'])
        
        self.assertFalse(result)
        self.assertEqual(mock_validate.call_count, 2)

    def test_validate_single_image_exception(self):
        """Test single image validation with exception."""
        with mock.patch.object(self.validator, '_parse_image_name', side_effect=Exception('Test error')):
            result = self.validator._validate_single_image('test-image')
            
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['image'], 'test-image')
            self.assertIn('Test error', result['error'])


if __name__ == '__main__':
    unittest.main()
