import subprocess
from pathlib import Path
import logging
import re
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
        # We only need Python's file I/O for this converter
        return True

    def convert(self, context: BuildContext) -> Path:
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.adoc").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

        logger.debug(f"Processing AsciiDoc includes from {main_adoc_file}")

        try:
            # Process the main file and all includes
            content = self._process_includes(
                main_adoc_file,
                context.source_dir,
                context.flavor
            )

            # Write the bundled content
            output_file.write_text(content, encoding='utf-8')

            logger.info(f"Successfully created bundled AsciiDoc file: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"AsciiDoc bundling failed for {context.language}-{context.flavor}")
            logger.error(f"Error: {e}")
            raise

    def _process_includes(self, adoc_file: Path, base_dir: Path, flavor: str, depth: int = 0) -> str:
        """
        Recursively process include directives in AsciiDoc files.

        Args:
            adoc_file: The AsciiDoc file to process
            base_dir: Base directory for resolving relative includes
            flavor: The flavor (plain or withHelp) for conditional processing
            depth: Current recursion depth (for preventing infinite loops)

        Returns:
            The processed content as a string
        """
        if depth > 10:
            logger.warning(f"Maximum include depth reached at {adoc_file}")
            return f"// ERROR: Maximum include depth exceeded for {adoc_file}\n"

        if not adoc_file.exists():
            logger.warning(f"Include file not found: {adoc_file}")
            return f"// WARNING: File not found: {adoc_file}\n"

        logger.debug(f"Processing file: {adoc_file} (depth={depth})")

        content = adoc_file.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        result = []

        # Track if we're inside a conditional block
        in_conditional = False
        conditional_matches = True
        conditional_stack = []

        for line in lines:
            # Handle include directives
            include_match = re.match(r'^\s*include::([^\[]+)\[(.*)\]\s*$', line)
            if include_match:
                include_path = include_match.group(1)
                include_attrs = include_match.group(2)

                # Resolve include path relative to current file's directory
                if adoc_file.parent != base_dir:
                    include_file = adoc_file.parent / include_path
                else:
                    include_file = base_dir / include_path

                # Add a comment showing the original include
                result.append(f"// BEGIN INCLUDE: {include_path}\n")

                # Recursively process the included file
                included_content = self._process_includes(include_file, base_dir, flavor, depth + 1)
                result.append(included_content)

                result.append(f"// END INCLUDE: {include_path}\n")
                continue

            # Handle conditional directives for flavor filtering
            # ifdef::show-help[] or ifndef::show-help[]
            ifdef_match = re.match(r'^\s*ifdef::([^\[]+)\[\]\s*$', line)
            ifndef_match = re.match(r'^\s*ifndef::([^\[]+)\[\]\s*$', line)
            endif_match = re.match(r'^\s*endif::\[\]\s*$', line)

            if ifdef_match:
                attr = ifdef_match.group(1)
                # Check if this attribute should be defined based on flavor
                matches = (flavor == "withHelp" and attr == "show-help")
                conditional_stack.append((True, matches))
                # Keep the conditional in output for clarity
                result.append(line)
                continue

            if ifndef_match:
                attr = ifndef_match.group(1)
                # Check if this attribute should NOT be defined
                matches = not (flavor == "withHelp" and attr == "show-help")
                conditional_stack.append((False, matches))
                # Keep the conditional in output
                result.append(line)
                continue

            if endif_match:
                if conditional_stack:
                    conditional_stack.pop()
                result.append(line)
                continue

            # Add the line to result
            result.append(line)

        return ''.join(result)

    def get_output_extension(self) -> str:
        return ".adoc"
