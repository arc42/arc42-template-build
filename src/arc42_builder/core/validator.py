import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class Validator:
    """
    Performs pre-build validation checks on the template repository.
    """
    def __init__(self, config):
        self.config = config
        self.template_path = Path(config.template.path)

    def run_all_validations(self):
        """Runs all validation checks and raises an error if any fail."""
        logger.info("Running all validations...")
        self.validate_template_path()
        self.validate_languages()
        self.verify_fonts_installed()
        logger.info("All validations passed.")

    def validate_template_path(self):
        """Check if the template path exists and seems valid."""
        if not self.template_path.is_dir():
            raise FileNotFoundError(f"Template directory not found at: {self.template_path}")
        logger.info(f"Template path '{self.template_path}' found.")

    def validate_languages(self):
        """
        For each language in the config, check for:
        1. The language directory.
        2. The version.properties file.
        3. Broken includes or image references using `asciidoctor`.
        """
        for lang in self.config.languages:
            logger.info(f"Validating language: {lang}...")
            lang_dir = self.template_path / lang
            if not lang_dir.is_dir():
                raise FileNotFoundError(f"Language directory not found for '{lang}' at: {lang_dir}")

            # 1. Check for version.properties
            version_file = lang_dir / "version.properties"
            if not version_file.is_file():
                raise FileNotFoundError(f"Missing version.properties for '{lang}' at: {version_file}")
            
            # 2. Check for broken references
            main_adoc = lang_dir / "arc42-template.adoc"
            if not main_adoc.is_file():
                raise FileNotFoundError(f"Main AsciiDoc file not found for '{lang}' at: {main_adoc}")
            
            self._check_asciidoctor_references(main_adoc)
            logger.info(f"Language '{lang}' validation passed.")

    def _check_asciidoctor_references(self, adoc_file: Path):
        """
        Runs asciidoctor in a dry-run mode to detect broken references.
        """
        logger.debug(f"Checking references in {adoc_file}...")
        try:
            subprocess.run(
                [
                    "asciidoctor",
                    str(adoc_file),
                    "-o", "/dev/null", # Discard output
                    "--failure-level", "WARN" # Fail on warnings (e.g., missing includes)
                ],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Validation failed for {adoc_file}. Asciidoctor output:\n{e.stderr}")
            raise ValueError(f"Broken references detected in {adoc_file}. See log for details.")

    def verify_fonts_installed(self):
        """
        Verify all required fonts are installed in the container.
        """
        if not self.config.build.verify_fonts:
            logger.warning("Skipping font verification.")
            return

        logger.info("Verifying required fonts are installed in the container...")
        required_fonts = [
            "Noto Sans",
            "Noto Sans CJK SC",
            "Noto Sans Mono",
            "Liberation Sans",
        ]
        
        try:
            result = subprocess.run(
                ["fc-list", ":", "family"], 
                capture_output=True, 
                text=True,
                check=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("`fc-list` command not found. Skipping font verification. This is expected on non-Linux hosts.")
            return

        installed_fonts = result.stdout
        missing = [font for font in required_fonts if font not in installed_fonts]
        
        if missing:
            raise RuntimeError(
                f"Missing required fonts in container: {missing}. "
                f"Please ensure the Docker image was built correctly."
            )
        logger.info("All required fonts are installed.")
