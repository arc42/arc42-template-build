import subprocess
from pathlib import Path
import logging

from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class HtmlConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("html", priority=1)
    
    def check_dependencies(self) -> bool:
        try:
            result = subprocess.run(
                ["asciidoctor", "--version"],
                capture_output=True,
                check=True,
                text=True
            )
            logger.info(f"Found Asciidoctor: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Asciidoctor not found. Please ensure it is installed and in the system's PATH.")
            return False
    
    def convert(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.html"

        # Set absolute path to images directory
        images_dir = context.source_dir / "images"

        # Build asciidoctor command
        cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"revnumber={context.version_props.get('revnumber', '')}",
            "-a", f"revdate={context.version_props.get('revdate', '')}",
            "-a", f"revremark={context.version_props.get('revremark', '')}",
            # Pass flavor as an attribute for AsciiDoc's conditional processing
            "-a", f"flavor={context.flavor}",
            # Set absolute path to images so they can be found regardless of output location
            "-a", f"imagesdir={images_dir.absolute()}",
            "-D", str(context.output_dir),
            "-o", str(output_file),
            str(context.source_dir / "arc42-template.adoc")
        ]

        # If flavor is 'withHelp', define the 'show-help' attribute.
        # The AsciiDoc source should use ifdef::show-help[] or ifeval::["{flavor}" == "withHelp"]
        if context.flavor == "withHelp":
            cmd.append("-a show-help")
        
        logger.debug(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        logger.info(f"Successfully created HTML file: {output_file}")
        return output_file
