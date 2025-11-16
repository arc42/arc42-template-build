import click
from pathlib import Path
import yaml
import subprocess
import shutil

@click.command()
@click.option('--language', '-l', type=click.Choice(['EN', 'DE']), 
              multiple=True, default=['EN', 'DE'])
@click.option('--format', '-f', 'formats', 
              type=click.Choice(['html', 'pdf', 'docx']), 
              multiple=True, default=['html', 'pdf', 'docx'])
def main(language, formats):
    """PoC: Build arc42 templates for EN/DE in HTML/PDF/DOCX"""
    
    template_dir = Path("/workspace/arc42-template")
    build_dir = Path("/workspace/build")
    
    for lang in language:
        for fmt in formats:
            click.echo(f"Building {lang} - {fmt}...")
            
            source_dir = template_dir / lang / "asciidoc"
            output_dir = build_dir / lang / "withHelp" / fmt
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load version properties
            version_file = template_dir / lang / "version.properties"
            version_props = {}
            if version_file.exists():
                with open(version_file) as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            version_props[key] = value
            
            # Build based on format
            if fmt == 'html':
                build_html(source_dir, output_dir, lang, version_props)
            elif fmt == 'pdf':
                build_pdf(source_dir, output_dir, lang, version_props)
            elif fmt == 'docx':
                build_docx(source_dir, output_dir, lang, version_props)
            
            click.echo(f"✓ Built {lang} - {fmt}")

def build_html(source_dir, output_dir, lang, version_props):
    """Build HTML output"""
    output_file = output_dir / f"arc42-template-{lang}-withHelp.html"
    cmd = [
        "asciidoctor",
        "-b", "html5",
        "-a", "imagesdir=/workspace/arc42-template/images",
        "-a", f"revnumber={version_props.get('revnumber', '')}",
        "-a", f"revdate={version_props.get('revdate', '')}",
        "-o", str(output_file),
        str(source_dir / "arc42-template.adoc")
    ]
    subprocess.run(cmd, check=True)

def build_pdf(source_dir, output_dir, lang, version_props):
    """Build PDF output"""
    output_file = output_dir / f"arc42-template-{lang}-withHelp.pdf"
    cmd = [
        "asciidoctor-pdf",
        "-a", "imagesdir=/workspace/arc42-template/images",
        "-a", f"revnumber={version_props.get('revnumber', '')}",
        "-a", f"revdate={version_props.get('revdate', '')}",
        "-o", str(output_file),
        str(source_dir / "arc42-template.adoc")
    ]
    subprocess.run(cmd, check=True)

def build_docx(source_dir, output_dir, lang, version_props):
    """Build DOCX via HTML + Pandoc"""
    # First create HTML
    temp_html = output_dir / "temp.html"
    cmd_html = [
        "asciidoctor",
        "-b", "html5",
        "-a", "imagesdir=/workspace/arc42-template/images",
        "-a", f"revnumber={version_props.get('revnumber', '')}",
        "-a", f"revdate={version_props.get('revdate', '')}",
        "-o", str(temp_html),
        str(source_dir / "arc42-template.adoc")
    ]
    subprocess.run(cmd_html, check=True)
    
    # Then convert to DOCX
    output_file = output_dir / f"arc42-template-{lang}-withHelp.docx"
    cmd_docx = [
        "pandoc",
        "-f", "html",
        "-t", "docx",
        "-o", str(output_file),
        str(temp_html)
    ]
    subprocess.run(cmd_docx, check=True)
    
    # Clean up temp file
    temp_html.unlink()

if __name__ == "__main__":
    main()