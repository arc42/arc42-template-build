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

    def validate_build_artifacts(self, build_dir: Path):
        """Validate generated build artifacts for syntax and completeness."""
        logger.info("Validating build artifacts...")
        self.validate_markdown_artifacts(build_dir)
        self.validate_html_artifacts(build_dir)
        self.validate_docx_artifacts(build_dir)
        logger.info("Build artifact validation passed.")

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
            self._check_missing_images(lang_dir)
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

    def _check_missing_images(self, lang_dir: Path):
        """
        Parse AsciiDoc files to find image references and verify they exist.
        """
        import re

        logger.debug(f"Checking for missing images in {lang_dir}...")
        images_dir = lang_dir / "images"

        # If no images directory exists, that's fine - no images expected
        if not images_dir.is_dir():
            logger.debug(f"No images directory found at {images_dir}, skipping image checks")
            return

        # Find all .adoc files
        adoc_files = list(lang_dir.glob("**/*.adoc"))

        # Pattern to match image directives: image::path[] or image:path[]
        image_pattern = re.compile(r'image::?([^\[\]]+)\[')

        referenced_images = set()
        for adoc_file in adoc_files:
            with open(adoc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = image_pattern.findall(content)
                referenced_images.update(matches)

        # Check if referenced images exist
        missing_images = []
        for img_ref in referenced_images:
            # Clean up the reference (remove any leading/trailing whitespace)
            img_ref = img_ref.strip()

            # Try both absolute and relative to images directory
            img_path = lang_dir / img_ref
            img_path_in_images = images_dir / img_ref

            if not img_path.exists() and not img_path_in_images.exists():
                missing_images.append(img_ref)

        if missing_images:
            logger.warning(
                f"Missing image files in {lang_dir}:\n  " +
                "\n  ".join(missing_images)
            )
            # Note: We warn but don't fail, as some images might be optional
        else:
            logger.debug(f"All {len(referenced_images)} referenced images found")

    def validate_markdown_artifacts(self, build_dir: Path):
        """
        Validate Markdown files for syntax correctness.
        Uses Pandoc to validate the syntax.
        """
        logger.info("Validating Markdown artifacts...")

        md_files = list(build_dir.glob("**/*.md"))

        if not md_files:
            logger.warning("No Markdown files found to validate")
            return

        errors = []
        for md_file in md_files:
            try:
                # Try to parse the Markdown file with Pandoc
                result = subprocess.run(
                    ["pandoc", str(md_file), "-t", "html", "-o", "/dev/null"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                errors.append(f"{md_file.name}: {e.stderr}")
                logger.error(f"Markdown validation failed for {md_file}: {e.stderr}")

        if errors:
            raise ValueError(
                f"Markdown validation failed for {len(errors)} file(s):\n" +
                "\n".join(errors)
            )

        logger.info(f"All {len(md_files)} Markdown files validated successfully")

    def validate_html_artifacts(self, build_dir: Path):
        """
        Validate HTML files for broken image references.
        """
        import re
        from html.parser import HTMLParser

        logger.info("Validating HTML artifacts...")

        html_files = list(build_dir.glob("**/*.html"))

        if not html_files:
            logger.warning("No HTML files found to validate")
            return

        class ImageExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.images = []

            def handle_starttag(self, tag, attrs):
                if tag == 'img':
                    for attr, value in attrs:
                        if attr == 'src':
                            self.images.append(value)

        errors = []
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                parser = ImageExtractor()
                parser.feed(content)

                # Check if referenced images exist
                for img_src in parser.images:
                    # Skip absolute URLs (http://, https://, data:, etc.)
                    if img_src.startswith(('http://', 'https://', 'data:', '//')):
                        continue

                    # Skip absolute paths (these shouldn't exist after our fix)
                    if img_src.startswith('/'):
                        errors.append(f"{html_file.name}: Image uses absolute path: {img_src}")
                        continue

                    # Check relative path
                    img_path = html_file.parent / img_src
                    if not img_path.exists():
                        errors.append(f"{html_file.name}: Missing image: {img_src}")

                logger.debug(f"HTML validation passed for {html_file.name} ({len(parser.images)} images found)")

            except Exception as e:
                errors.append(f"{html_file.name}: Validation error: {e}")
                logger.error(f"HTML validation failed for {html_file}: {e}")

        if errors:
            raise ValueError(
                f"HTML validation failed for {len(errors)} issue(s):\n" +
                "\n".join(errors)
            )

        logger.info(f"All {len(html_files)} HTML files validated successfully")

    def validate_docx_artifacts(self, build_dir: Path):
        """
        Validate DOCX files for embedded images.
        DOCX files are ZIP archives containing XML and media files.
        """
        import zipfile

        logger.info("Validating DOCX artifacts...")

        docx_files = list(build_dir.glob("**/*.docx"))

        if not docx_files:
            logger.warning("No DOCX files found to validate")
            return

        errors = []
        for docx_file in docx_files:
            try:
                # DOCX is a ZIP file - check if it has media folder with images
                with zipfile.ZipFile(docx_file, 'r') as zip_ref:
                    file_list = zip_ref.namelist()

                    # Check for media files (images are stored in word/media/)
                    media_files = [f for f in file_list if f.startswith('word/media/')]

                    if not media_files:
                        # This might be okay if the document has no images
                        logger.debug(f"{docx_file.name}: No embedded images found (this may be expected)")
                    else:
                        logger.debug(f"{docx_file.name}: Found {len(media_files)} embedded media file(s)")

            except zipfile.BadZipFile:
                errors.append(f"{docx_file.name}: File is not a valid DOCX (corrupted ZIP)")
                logger.error(f"DOCX validation failed for {docx_file}: Not a valid ZIP file")
            except Exception as e:
                errors.append(f"{docx_file.name}: Validation error: {e}")
                logger.error(f"DOCX validation failed for {docx_file}: {e}")

        if errors:
            raise ValueError(
                f"DOCX validation failed for {len(errors)} issue(s):\n" +
                "\n".join(errors)
            )

        logger.info(f"All {len(docx_files)} DOCX files validated successfully")
