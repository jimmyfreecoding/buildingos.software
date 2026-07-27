# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VitePress documentation site for BuildingOS smart building software copyright applications (软件著作权). Documents 18 software systems for Chinese software copyright registration, each with three pages: copyright info (软件著作权内容), user/design manual (使用手册), and source code listings (源代码).

## Commands

```bash
npm run docs:dev     # Start dev server
npm run docs:build   # Build static site to docs/.vitepress/dist
npm run docs:serve   # Preview built site
```

## Architecture

- **`docs/`** — VitePress content root. Each software system is a subdirectory containing `copyright.md`, `manual.md`, and `source.md`. Screenshots are stored alongside as `image*.png`.
- **`docs/.vitepress/config.ts`** — Site config: title, language (`zh-CN`), base path (`/software/`), nav, and sidebar. Systems not yet activated are commented out in the sidebar; active ones are: visitor, access, reservation, meetingroom, toilet.
- **`docs/index.md`** — Homepage with navigation links to active systems.
- **`ref/`** — Reference materials including the official copyright application form template, requirements document, and R&D project records (2024-2025).

## Adding or Activating a Software System

1. Create the subdirectory under `docs/` if it doesn't exist (e.g., `docs/workflow/`).
2. Add three files: `copyright.md`, `manual.md`, `source.md`. Follow the format of existing systems like `docs/visitor/`.
3. Uncomment (or add) the sidebar entry in `docs/.vitepress/config.ts`.
4. Update `docs/index.md` with the corresponding nav link.
