import subprocess
from pathlib import Path
import logging
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class AsciidocConverter(ConverterPlugin):
    """
    A 'pass-through' converter that produces a single, self-contained AsciiDoc file
    with all includes processed. This is useful for consumers who want a single
    file without having to handle the include structure themselves.
    """
    def __init__(self):
        super().__init__("asciidoc", priority=1)

    def check_dependencies(self) -> bool:
        # Same dependency as HTML converter
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Asciidoctor not found.")
            return False

    def convert(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.adoc"
        
        # We use the 'docbook' backend as a way to get Asciidoctor to process
        # all includes and conditionals, then we capture the output.
        cmd = [
            "asciidoctor",
            "--no-header-footer",
            "-b", "docbook", 
            "-a", f"flavor={context.flavor}",
            str(context.source_dir / "arc42-template.adoc"),
            "-o", "-"  # Output to stdout
        ]
        
        if context.flavor == "withHelp":
            cmd.append("-a show-help")

        logger.debug(f"Executing command to bundle AsciiDoc: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Write the captured stdout to the output file
        output_file.write_text(result.stdout, encoding='utf-8')
        
        logger.info(f"Successfully created bundled AsciiDoc file: {output_file}")
        return output_file
