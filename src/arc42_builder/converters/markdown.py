import subprocess
from pathlib import Path
import logging
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class MarkdownConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("markdown", priority=1)

    def check_dependencies(self) -> bool:
        # Depends on both Asciidoctor and Pandoc
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Markdown conversion requires both Asciidoctor and Pandoc.")
            return False

    def convert(self, context: BuildContext) -> Path:
        # For now, this implements the single-file conversion.
        # Multi-page logic can be added here later based on config.
        multi_page = context.config.get("multi_page", False)
        if multi_page:
            logger.warning("Multi-page Markdown output is not yet implemented. Generating a single file.")
        
        return self._convert_single_file(context)

    def _convert_single_file(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.md"
        main_adoc_file = context.source_dir / "arc42-template.adoc"
        variant = context.config.get("variant", "gfm") # GitHub-Flavored Markdown

        # Create a temporary HTML file via Asciidoctor
        temp_html_file = context.output_dir / f"temp-{context.language}-{context.flavor}.html"

        asciidoctor_cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"flavor={context.flavor}",
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]
        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")
        
        logger.debug(f"Executing Asciidoctor for intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        # Convert the intermediate HTML to Markdown using Pandoc
        pandoc_cmd = [
            "pandoc",
            str(temp_html_file),
            "-f", "html",
            "-t", variant,
            "-o", str(output_file)
        ]
        
        logger.debug(f"Executing Pandoc for Markdown conversion: {' '.join(pandoc_cmd)}")
        subprocess.run(pandoc_cmd, check=True)

        # Clean up the temporary HTML file
        temp_html_file.unlink()

        logger.info(f"Successfully created Markdown file: {output_file}")
        return output_file
