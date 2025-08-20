"""Docker image validation utility module."""
import json
import requests
import traceback
from ibis.custom_logging import get_logger


class DockerValidator(object):
    """Docker image validator for checking image existence and metadata."""

    def __init__(self, cfg_mgr):
        """Initialize the docker validator.
        Args:
            cfg_mgr: ConfigManager object
        """
        self.cfg_mgr = cfg_mgr
        self.logger = get_logger(cfg_mgr)

    def validate_images(self, image_list):
        """Validate a list of docker images.
        Args:
            image_list: List of docker image names to validate
        Returns:
            bool: True if all validations pass, False otherwise
        """
        self.logger.info("Starting docker image validation...")
        validation_results = []
        
        for image in image_list:
            self.logger.info("Validating image: {0}".format(image))
            result = self._validate_single_image(image)
            validation_results.append(result)
            
            if result['status'] == 'success':
                self.logger.info("Image {0} validation: SUCCESS".format(image))
                if result.get('metadata'):
                    self._log_image_metadata(image, result['metadata'])
            else:
                self.logger.error("Image {0} validation: FAILED - {1}".format(
                    image, result.get('error', 'Unknown error')))

        success_count = sum(1 for r in validation_results if r['status'] == 'success')
        total_count = len(validation_results)
        
        self.logger.info("Docker image validation completed: {0}/{1} images validated successfully".format(
            success_count, total_count))
        
        if success_count == total_count:
            self.logger.info("All docker images validated successfully!")
            return True
        else:
            self.logger.error("Docker image validation failed for {0} images".format(
                total_count - success_count))
            return False

    def _validate_single_image(self, image_name):
        """Validate a single docker image.
        Args:
            image_name: Docker image name (e.g., 'ads-rnr/apt-ads-airflow-prod')
        Returns:
            dict: Validation result with status and metadata
        """
        try:
            registry, repository, tag = self._parse_image_name(image_name)
            
            metadata = self._get_image_metadata(registry, repository, tag)
            
            if metadata:
                return {
                    'status': 'success',
                    'image': image_name,
                    'metadata': metadata
                }
            else:
                return {
                    'status': 'failed',
                    'image': image_name,
                    'error': 'Image not found or inaccessible'
                }
                
        except Exception as e:
            self.logger.error("Error validating image {0}: {1}".format(
                image_name, str(e)))
            return {
                'status': 'failed',
                'image': image_name,
                'error': str(e)
            }

    def _parse_image_name(self, image_name):
        """Parse docker image name into components.
        Args:
            image_name: Full image name
        Returns:
            tuple: (registry, repository, tag)
        """
        registry = 'docker.io'
        tag = 'latest'
        
        if '/' in image_name and '.' in image_name.split('/')[0]:
            parts = image_name.split('/', 1)
            registry = parts[0]
            repository = parts[1]
        else:
            repository = image_name
        
        if ':' in repository:
            repository, tag = repository.rsplit(':', 1)
            
        return registry, repository, tag

    def _get_image_metadata(self, registry, repository, tag):
        """Get image metadata from registry API.
        Args:
            registry: Registry hostname
            repository: Repository name
            tag: Image tag
        Returns:
            dict: Image metadata or None if not found
        """
        try:
            if registry == 'docker.io':
                return self._get_dockerhub_metadata(repository, tag)
            else:
                return self._get_registry_metadata(registry, repository, tag)
        except Exception as e:
            self.logger.warning("Failed to get metadata for {0}/{1}:{2} - {3}".format(
                registry, repository, tag, str(e)))
            return None

    def _get_dockerhub_metadata(self, repository, tag):
        """Get metadata from Docker Hub API.
        Args:
            repository: Repository name
            tag: Image tag
        Returns:
            dict: Metadata or None
        """
        try:
            if '/' not in repository:
                url = "https://hub.docker.com/v2/repositories/library/{0}/tags/{1}".format(
                    repository, tag)
            else:
                url = "https://hub.docker.com/v2/repositories/{0}/tags/{1}".format(
                    repository, tag)
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', tag),
                    'full_size': data.get('full_size'),
                    'last_updated': data.get('last_updated'),
                    'repository': repository,
                    'registry': 'docker.io'
                }
            else:
                self.logger.warning("Docker Hub API returned status {0} for {1}:{2}".format(
                    response.status_code, repository, tag))
                return None
                
        except requests.RequestException as e:
            self.logger.warning("Request failed for Docker Hub API: {0}".format(str(e)))
            return None
        except Exception as e:
            self.logger.warning("Error parsing Docker Hub response: {0}".format(str(e)))
            return None

    def _get_registry_metadata(self, registry, repository, tag):
        """Get metadata from generic registry API.
        Args:
            registry: Registry hostname
            repository: Repository name  
            tag: Image tag
        Returns:
            dict: Metadata or None
        """
        try:
            url = "https://{0}/v2/{1}/manifests/{2}".format(registry, repository, tag)
            headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return {
                    'repository': repository,
                    'tag': tag,
                    'registry': registry,
                    'manifest_available': True
                }
            else:
                self.logger.warning("Registry API returned status {0} for {1}/{2}:{3}".format(
                    response.status_code, registry, repository, tag))
                return None
                
        except requests.RequestException as e:
            self.logger.warning("Request failed for registry API: {0}".format(str(e)))
            return None
        except Exception as e:
            self.logger.warning("Error with registry API: {0}".format(str(e)))
            return None

    def _log_image_metadata(self, image_name, metadata):
        """Log image metadata in a readable format.
        Args:
            image_name: Image name
            metadata: Metadata dictionary
        """
        self.logger.info("Metadata for {0}:".format(image_name))
        for key, value in metadata.items():
            if value is not None:
                self.logger.info("  {0}: {1}".format(key, value))
