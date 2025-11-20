import subprocess
from pathlib import Path
import logging
import re
import shutil
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class MarkdownMpConverter(ConverterPlugin):
    """Multi-page Markdown converter - splits template into one file per chapter"""

    def __init__(self):
        super().__init__("markdown_mp", priority=1)

    def check_dependencies(self) -> bool:
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Multi-page Markdown conversion requires both Asciidoctor and Pandoc.")
            return False

    def convert(self, context: BuildContext) -> Path:
        """Convert to multi-page Markdown structure"""
        output_dir = context.output_dir / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)

        variant = context.config.get("variant", "gfm")

        # First, generate a single HTML file
        temp_html = self._generate_intermediate_html(context)

        # Split HTML into chapters and convert each to Markdown
        self._split_and_convert(temp_html, output_dir, variant, context)

        # Create an index file
        index_file = self._create_index(output_dir, context)

        # Clean up temporary files
        temp_html.unlink()

        logger.info(f"Successfully created multi-page Markdown in: {output_dir}")
        return index_file

    def _generate_intermediate_html(self, context: BuildContext) -> Path:
        """Generate intermediate HTML file using Asciidoctor"""
        temp_html_file = (context.output_dir / f"temp-{context.language}-{context.flavor}.html").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

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
            "-a", f"revnumber={context.version_props.get('revnumber', '')}",
            "-a", f"revdate={context.version_props.get('revdate', '')}",
            "-a", f"revremark={context.version_props.get('revremark', '')}",
            "-a", f"flavor={context.flavor}",
            # Use relative path to images directory
            "-a", "imagesdir=images",
            "-a", "sectids",  # Generate section IDs for splitting
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]

        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")

        logger.debug(f"Generating intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        return temp_html_file

    def _split_and_convert(self, html_file: Path, output_dir: Path, variant: str, context: BuildContext):
        """Split HTML by h2 headers and convert each to Markdown"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by h2 sections (main arc42 chapters)
        pattern = r'<h2[^>]*>(.*?)</h2>'
        parts = re.split(pattern, content, flags=re.DOTALL)

        # Extract header and footer (everything before first h2 and after last section)
        header = parts[0]

        # Process chapter pairs (title, content)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                chapter_title = re.sub(r'<[^>]+>', '', parts[i])  # Strip HTML tags
                chapter_content = parts[i - 1] + '<h2>' + parts[i] + '</h2>' + parts[i + 1]

                # Sanitize filename
                safe_title = re.sub(r'[^\w\s-]', '', chapter_title).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()
                chapter_num = (i + 1) // 2

                # Write chapter HTML to temp file
                temp_chapter_html = output_dir / f"temp-{chapter_num:02d}.html"
                with open(temp_chapter_html, 'w', encoding='utf-8') as f:
                    f.write(chapter_content)

                # Convert to Markdown
                output_md = output_dir / f"{chapter_num:02d}-{safe_title}.md"
                pandoc_cmd = [
                    "pandoc",
                    str(temp_chapter_html),
                    "-f", "html",
                    "-t", variant,
                    "-o", str(output_md)
                ]

                subprocess.run(pandoc_cmd, check=True)
                temp_chapter_html.unlink()

                logger.debug(f"Created chapter: {output_md.name}")

    def _create_index(self, output_dir: Path, context: BuildContext) -> Path:
        """Create index.md with links to all chapters"""
        index_file = context.output_dir / "index.md"

        chapter_files = sorted(output_dir.glob("*.md"))

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"# arc42 Template - {context.language} ({context.flavor})\n\n")
            f.write("## Chapters\n\n")

            for chapter_file in chapter_files:
                # Extract title from filename
                title = chapter_file.stem.split('-', 1)[1].replace('-', ' ').title()
                relative_path = f"chapters/{chapter_file.name}"
                f.write(f"- [{title}]({relative_path})\n")

        logger.info(f"Created index file: {index_file}")
        return index_file

    def get_output_extension(self) -> str:
        return ".md"
