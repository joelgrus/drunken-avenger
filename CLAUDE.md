# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pelican-based static site generator for Joel Grus's blog (joelgrus.com). The project structure follows standard Pelican conventions with content in Markdown format, custom themes, and build automation via Makefile.

## Architecture

- **Static Site Generator**: Uses Pelican (Python-based) to convert Markdown content to HTML
- **Content Management**: Blog posts and pages stored as Markdown files in `content/` directory
- **Theme System**: Custom theme located in `themes/pelican-svbhack-joel/`
- **Build System**: Makefile-based automation for development and deployment workflows
- **Deployment**: Configured for S3 (AWS) deployment to joelgrus.com

## Key Directories

- `content/`: Blog posts, pages, and static assets (images, experiments)
- `output/`: Generated HTML site (created during build)
- `themes/pelican-svbhack-joel/`: Custom Pelican theme
- `old_content/`, `old_posts/`: Archive of older content

## Development Commands

### Building the Site
```bash
make html          # Generate static HTML files
make local         # Generate with localhost URLs for development
make clean         # Remove generated files
make regenerate    # Auto-regenerate on file changes
```

### Development Server
```bash
make serve         # Serve site at http://localhost:8000
make devserver     # Start development server with auto-reload
make stopserver    # Stop development server
```

### Deployment
```bash
make publish       # Build with production settings
make s3_upload     # Deploy to S3 bucket (joelgrus.com)
```

## Configuration Files

- `pelicanconf.py`: Main Pelican configuration (development settings)
- `publishconf.py`: Production-specific settings
- `pyproject.toml`: Python dependencies (Pelican, Markdown)
- `requirements.txt`: Legacy requirements file

## Content Structure

Blog posts use standard Pelican article format with metadata headers. The site includes:
- Technical blog posts (data science, programming)
- Experiments and interactive content
- Static pages (about, books, speaking)
- Legacy WordPress content migration

## Theme Customization

The custom theme `pelican-svbhack-joel` includes:
- Responsive design
- Social media integration
- Custom styling for code blocks
- Analytics integration