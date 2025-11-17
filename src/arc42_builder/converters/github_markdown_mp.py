import subprocess
from pathlib import Path
import logging
import re
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class GithubMarkdownMpConverter(ConverterPlugin):
    """Multi-page GitHub Flavored Markdown converter with GitHub-specific optimizations"""

    def __init__(self):
        super().__init__("github_markdown_mp", priority=2)

    def check_dependencies(self) -> bool:
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Multi-page GitHub Markdown conversion requires both Asciidoctor and Pandoc.")
            return False

    def convert(self, context: BuildContext) -> Path:
        """Convert to multi-page GitHub Flavored Markdown structure"""
        output_dir = context.output_dir / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)

        # First, generate a single HTML file
        temp_html = self._generate_intermediate_html(context)

        # Split HTML into chapters and convert each to Markdown
        chapter_info = self._split_and_convert(temp_html, output_dir, context)

        # Create a README.md as the index file (GitHub convention)
        readme_file = self._create_readme(output_dir, context, chapter_info)

        # Clean up temporary files
        temp_html.unlink()

        logger.info(f"Successfully created multi-page GitHub Markdown in: {output_dir}")
        return readme_file

    def _generate_intermediate_html(self, context: BuildContext) -> Path:
        """Generate intermediate HTML file using Asciidoctor"""
        temp_html_file = (context.output_dir / f"temp-{context.language}-{context.flavor}.html").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"
        images_dir = context.source_dir / "images"

        asciidoctor_cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"flavor={context.flavor}",
            "-a", f"imagesdir={images_dir.absolute()}",
            "-a", "sectids",
            "-a", "toc=left",
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]

        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")

        logger.debug(f"Generating intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        return temp_html_file

    def _split_and_convert(self, html_file: Path, output_dir: Path, context: BuildContext) -> list:
        """Split HTML by h2 headers and convert each to GitHub Markdown"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by h2 sections (main arc42 chapters)
        pattern = r'<h2[^>]*>(.*?)</h2>'
        parts = re.split(pattern, content, flags=re.DOTALL)

        chapter_info = []

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

                # Convert to GitHub Flavored Markdown
                output_md = output_dir / f"{chapter_num:02d}-{safe_title}.md"
                pandoc_cmd = [
                    "pandoc",
                    str(temp_chapter_html),
                    "-f", "html",
                    "-t", "gfm",
                    "--wrap=preserve",
                    "--atx-headers",
                    "-o", str(output_md)
                ]

                subprocess.run(pandoc_cmd, check=True)

                # Apply GitHub-specific optimizations
                self._optimize_for_github(output_md)

                temp_chapter_html.unlink()

                chapter_info.append({
                    'num': chapter_num,
                    'title': chapter_title.strip(),
                    'file': output_md.name
                })

                logger.debug(f"Created chapter: {output_md.name}")

        return chapter_info

    def _optimize_for_github(self, md_file: Path):
        """Apply GitHub-specific optimizations to the Markdown file"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix anchor links for GitHub
        def fix_anchor(match):
            anchor = match.group(1)
            github_anchor = anchor.lower().replace(' ', '-')
            github_anchor = re.sub(r'[^\w\s-]', '', github_anchor)
            github_anchor = re.sub(r'[-\s]+', '-', github_anchor)
            return f'(#{github_anchor})'

        content = re.sub(r'\(#([^)]+)\)', fix_anchor, content)

        # Convert admonitions to GitHub alerts
        content = re.sub(r'^\*\*Note:\*\*', '> [!NOTE]', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Warning:\*\*', '> [!WARNING]', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Important:\*\*', '> [!IMPORTANT]', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Tip:\*\*', '> [!TIP]', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\*Caution:\*\*', '> [!CAUTION]', content, flags=re.MULTILINE)

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_readme(self, output_dir: Path, context: BuildContext, chapter_info: list) -> Path:
        """Create README.md with links to all chapters (GitHub convention)"""
        readme_file = context.output_dir / "README.md"

        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"# arc42 Template - {context.language} ({context.flavor})\n\n")
            f.write("This is the arc42 architecture documentation template in multi-page format.\n\n")
            f.write("## Table of Contents\n\n")

            for chapter in chapter_info:
                relative_path = f"chapters/{chapter['file']}"
                f.write(f"{chapter['num']}. [{chapter['title']}]({relative_path})\n")

            f.write("\n---\n\n")
            f.write("**About arc42**: arc42 is a template for documenting software and system architecture. ")
            f.write("Learn more at [arc42.org](https://arc42.org/)\n")

        logger.info(f"Created README file: {readme_file}")
        return readme_file

    def get_output_extension(self) -> str:
        return ".md"
