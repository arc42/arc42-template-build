import subprocess
from pathlib import Path
import logging
import re
import shutil
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class GithubMarkdownConverter(ConverterPlugin):
    """GitHub Flavored Markdown converter with GitHub-specific optimizations"""

    def __init__(self):
        super().__init__("github_markdown", priority=2)

    def check_dependencies(self) -> bool:
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("GitHub Markdown conversion requires both Asciidoctor and Pandoc.")
            return False

    def convert(self, context: BuildContext) -> Path:
        """Convert to single-file GitHub Flavored Markdown"""
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.md").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

        # Copy images directory to output directory for relative referencing
        source_images_dir = context.source_dir / "images"
        output_images_dir = context.output_dir / "images"

        if source_images_dir.exists():
            if output_images_dir.exists():
                shutil.rmtree(output_images_dir)
            shutil.copytree(source_images_dir, output_images_dir)
            logger.debug(f"Copied images from {source_images_dir} to {output_images_dir}")

        # Create a temporary HTML file via Asciidoctor
        temp_html_file = (context.output_dir / f"temp-{context.language}-{context.flavor}.html").absolute()

        asciidoctor_cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"revnumber={context.version_props.get('revnumber', '')}",
            "-a", f"revdate={context.version_props.get('revdate', '')}",
            "-a", f"revremark={context.version_props.get('revremark', '')}",
            "-a", f"flavor={context.flavor}",
            # Use relative path to images directory
            "-a", "imagesdir=images",
            "-a", "sectids",  # Generate section IDs for better anchors
            "-a", "toc=left",  # Table of contents
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]

        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")

        logger.debug(f"Executing Asciidoctor for intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        # Convert the intermediate HTML to GitHub Flavored Markdown using Pandoc
        # Use --resource-path to tell Pandoc where to find images
        pandoc_cmd = [
            "pandoc",
            str(temp_html_file),
            "-f", "html",
            "-t", "gfm",  # GitHub Flavored Markdown
            "--wrap=preserve",  # Preserve line wrapping
            "--atx-headers",  # Use ATX-style headers (# ## ###)
            "--resource-path", str(context.output_dir),
            "-o", str(output_file)
        ]

        logger.debug(f"Executing Pandoc for GitHub Markdown conversion: {' '.join(pandoc_cmd)}")
        subprocess.run(pandoc_cmd, check=True)

        # Post-process for GitHub-specific optimizations
        if context.config.get("optimize_for_github", True):
            self._optimize_for_github(output_file)

        # Clean up the temporary HTML file
        temp_html_file.unlink()

        logger.info(f"Successfully created GitHub Markdown file: {output_file}")
        return output_file

    def _optimize_for_github(self, md_file: Path):
        """Apply GitHub-specific optimizations to the Markdown file"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix anchor links to work with GitHub's auto-generated anchors
        # GitHub auto-generates anchors from headers in lowercase with hyphens
        def fix_anchor(match):
            anchor = match.group(1)
            # Convert to lowercase and replace spaces with hyphens
            github_anchor = anchor.lower().replace(' ', '-')
            # Remove special characters that GitHub strips
            github_anchor = re.sub(r'[^\w\s-]', '', github_anchor)
            github_anchor = re.sub(r'[-\s]+', '-', github_anchor)
            return f'(#{github_anchor})'

        # Fix internal anchor references
        content = re.sub(r'\(#([^)]+)\)', fix_anchor, content)

        # Ensure code blocks have language hints when possible
        # (Pandoc usually handles this, but we can add fallbacks)

        # Add alert/admonition support using GitHub's alert syntax
        # Convert common admonition patterns to GitHub alerts
        content = re.sub(
            r'^\*\*Note:\*\*',
            '> [!NOTE]',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^\*\*Warning:\*\*',
            '> [!WARNING]',
            content,
            flags=re.MULTILINE
        )
        content = re.sub(
            r'^\*\*Important:\*\*',
            '> [!IMPORTANT]',
            content,
            flags=re.MULTILINE
        )

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Applied GitHub-specific optimizations to {md_file}")

    def get_output_extension(self) -> str:
        return ".md"
