import subprocess
from pathlib import Path
import logging
import shutil
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class DocxConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("docx", priority=1)

    def check_dependencies(self) -> bool:
        try:
            result = subprocess.run(["pandoc", "--version"], capture_output=True, check=True, text=True)
            logger.info(f"Found Pandoc: {result.stdout.splitlines()[0]}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Pandoc not found. Please ensure it is installed.")
            return False

    def convert(self, context: BuildContext) -> Path:
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.docx").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

        # Pandoc works best converting from a single file. We first let Asciidoctor
        # create a single intermediate HTML file, then convert that to DOCX.

        # Create a temporary HTML file
        temp_html_file = (context.output_dir / f"temp-{context.language}-{context.flavor}.html").absolute()

        # Copy images directory to output directory for relative referencing
        source_images_dir = context.source_dir / "images"
        output_images_dir = context.output_dir / "images"

        if source_images_dir.exists():
            if output_images_dir.exists():
                shutil.rmtree(output_images_dir)
            shutil.copytree(source_images_dir, output_images_dir)
            logger.debug(f"Copied images from {source_images_dir} to {output_images_dir}")

        asciidoctor_cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"flavor={context.flavor}",
            # Use relative path to images directory
            "-a", "imagesdir=images",
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]
        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")

        logger.debug(f"Executing Asciidoctor for intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        # Convert the intermediate HTML to DOCX using Pandoc
        # Use --resource-path to tell Pandoc where to find images
        pandoc_cmd = [
            "pandoc",
            str(temp_html_file),
            "-f", "html",
            "-t", "docx",
            "--resource-path", str(context.output_dir),
            "-o", str(output_file)
        ]

        logger.debug(f"Executing Pandoc for DOCX conversion: {' '.join(pandoc_cmd)}")
        subprocess.run(pandoc_cmd, check=True)

        # Clean up the temporary HTML file
        temp_html_file.unlink()

        logger.info(f"Successfully created DOCX file: {output_file}")
        return output_file
