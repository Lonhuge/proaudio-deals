#!/usr/bin/env python3
"""Wrap the artifact body into a standalone page for GitHub Pages."""
import pathlib, re, sys

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "report.src.html").read_text()
title = (re.search(r"<title>(.*?)</title>", src, re.S) or [None, "Pro-audio deal scan"])[1].strip()

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Used pro-audio gear on Kleinanzeigen priced below its reference price, with seller-trust filtering.">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='14' font-size='14'>&#127899;</text></svg>">
<style>*{{margin:0;padding:0;box-sizing:border-box}}</style>
{src}
</html>
"""
pathlib.Path("index.html").write_text(html)
print(f"built index.html  ({len(html):,} bytes)  title={title!r}")
