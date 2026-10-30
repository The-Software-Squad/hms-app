"""Export HMS's workflow manifest to Markdown, printable HTML and an optional offline bundle."""

import argparse
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "hms/public/docs"
OUTPUT = ROOT / "docs/user-guide"
E = html.escape


def review_text(book, guide=None):
	if guide and guide.get("verified_on"):
		return "Workflow verified " + guide["verified_on"] + "."
	if guide:
		return (
			"Written instructions source reviewed " + guide["reviewed_on"] + ". " + guide["verification_note"]
		)
	return book["review_notice"]


def chapter_markdown(book, guide, entries):
	lines = [
		"# " + guide["title"],
		"",
		guide["summary"],
		"",
		"**Who can do this:** " + guide["audience"],
		"",
		"[All workflows](README.md)",
		"",
		"## What this workflow does",
		"",
		guide["description"],
		"",
		"## Before you start",
		"",
	]
	lines += ["- " + item for item in guide["prerequisites"]]
	for number, step in enumerate(guide["steps"], 1):
		lines += ["", f'## {number}. {step["title"]}', "", step["detail"]]
	lines += [
		"",
		"## What success looks like",
		"",
		guide["check"],
		"",
		"## Common problems and recovery",
		"",
		guide["note"],
		"",
		"## Screenshots and walkthrough",
		"",
		guide["media_note"],
		"",
	]
	for screen in guide["screenshots"]:
		lines += [
			f'![{screen["caption"]}](../../hms/public/docs/screenshots/{screen["file"]})',
			"",
			screen["caption"],
			"",
		]
	motion = guide.get("walkthrough")
	if motion:
		lines += [
			f'[Open / download the GIF example](../../hms/public/docs/walkthroughs/{motion["file"]})',
			"",
			motion["caption"],
			"",
		]
	lines += ["## Related workflows", ""]
	lines += [f'- [{entries[id]["title"]}]({id}.md)' for id in guide["related"]]
	lines += ["", review_text(book, guide), "", book["screenshot_notice"], ""]
	return "\n".join(lines)


def chapter_html(book, guide, entries):
	parts = [
		f'<article id="{E(guide["id"])}"><a class="back" href="#contents">All workflows</a><p class="category">{E(guide["category"])}</p><h2>{E(guide["title"])}</h2><p>{E(guide["summary"])}</p><p><strong>Who can do this:</strong> {E(guide["audience"])}</p><h3>What this workflow does</h3><p>{E(guide["description"])}</p><aside><h3>Before you start</h3><ul>'
	]
	parts += ["<li>" + E(item) + "</li>" for item in guide["prerequisites"]]
	parts += ['</ul></aside><ol class="steps">']
	parts += [f'<li><h3>{E(step["title"])}</h3><p>{E(step["detail"])}</p></li>' for step in guide["steps"]]
	parts += [
		f'</ol><aside><h3>What success looks like</h3><p>{E(guide["check"])}</p></aside><aside class="note"><h3>Common problems and recovery</h3><p>{E(guide["note"])}</p></aside><h3>Screenshots and walkthrough</h3><p>{E(guide["media_note"])}</p>'
	]
	for screen in guide["screenshots"]:
		url = "screenshots/" + E(screen["file"])
		parts += [
			f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{E(screen["caption"])}"></a><figcaption>{E(screen["caption"])}</figcaption></figure>'
		]
	motion = guide.get("walkthrough")
	if motion:
		parts += [
			f'<p class="gif-link"><a href="walkthroughs/{E(motion["file"])}">Open / download GIF example</a> — {E(motion["caption"])}</p>'
		]
	parts += ["<h3>Related workflows</h3><ul>"]
	parts += [f'<li><a href="#{E(id)}">{E(entries[id]["title"])}</a></li>' for id in guide["related"]]
	parts += [f'</ul><p class="review">{E(review_text(book, guide))}</p></article>']
	return "".join(parts)


def export(bundle=None):
	book = json.loads((ASSETS / "user-guide.json").read_text())
	entries = {guide["id"]: guide for guide in book["guides"]}
	OUTPUT.mkdir(parents=True, exist_ok=True)
	index = [
		"# HMS user guide",
		"",
		"Open **User guide** from an HMS workspace or Help on a supported form, or use `/desk/hms-guide`.",
		"",
		book["review_notice"],
		"",
		book["media_notice"],
		"",
		book["screenshot_notice"],
		"",
		"Where a GIF is available, use Play walkthrough to start it and Stop walkthrough to return to the still image.",
		"",
	]
	for category in dict.fromkeys(g["category"] for g in entries.values()):
		index += ["## " + category, ""]
		index += [
			f'- [{g["title"]}]({g["id"]}.md) — {g["summary"]}'
			for g in entries.values()
			if g["category"] == category
		]
		index += [""]
	index += [
		"## Reference and maintenance",
		"",
		"- [Quick reference](../USER-GUIDE-QUICK-REFERENCE.md)",
		"- [Media and verification checklist](../USER-GUIDE-MEDIA-STATUS.md)",
		"- [Maintaining and exporting the guide](../USER-GUIDE-MAINTENANCE.md)",
		"",
		"Updated " + book["updated"] + ".",
		"",
		"The printable edition is `hms/public/docs/user-guide-print.html`. Use Print / Save as PDF in your browser; a separate PDF has not been generated.",
		"",
	]
	(OUTPUT / "README.md").write_text("\n".join(index))
	for guide in entries.values():
		(OUTPUT / (guide["id"] + ".md")).write_text(chapter_markdown(book, guide, entries))
	contents = "".join(
		f'<li><a href="#{E(g["id"])}">{E(g["title"])}</a><span>{E(g["category"])}</span></li>'
		for g in entries.values()
	)
	css = """body{font:16px/1.65 system-ui,sans-serif;color:#18332b;background:#fafcfb;max-width:980px;margin:38px auto;padding:0 24px}h1{font-size:40px;line-height:1.2}h2{font-size:30px;line-height:1.3}h3{font-size:18px}a{color:#17634c;text-underline-offset:3px}article{border-top:1px solid #ccdcd4;margin-top:48px;padding-top:28px;scroll-margin-top:24px}.category,.review,.back,figcaption{font-size:13px;color:#4e675e}.category{text-transform:uppercase;letter-spacing:.08em}aside{background:#edf5f0;padding:8px 20px;border-radius:10px;margin:20px 0}.note{background:#faf2df}figure{margin:26px 0}img{display:block;max-width:100%;height:auto;border:1px solid #d6e3dc;border-radius:6px}figcaption{margin-top:8px}li{margin:8px 0}#contents ol{padding-left:24px}#contents li span{display:block;font-size:13px;color:#52685f}.print-control{background:#1c674e;color:#fff;border:0;border-radius:8px;padding:12px 20px;font:inherit;cursor:pointer}.notice{border-left:3px solid #bfa261;padding-left:16px}.steps>li{margin-bottom:22px}.review{margin-top:24px}@media(max-width:600px){body{padding:0 16px}h1{font-size:32px}h2{font-size:26px}aside{padding:6px 12px}}@media print{body{background:white;margin:0;padding:0;font-size:11pt;max-width:none}.print-control,.print-hint,.back,.gif-link{display:none}article{break-before:page;border:0;margin:0;padding:0}figure,aside,.steps>li{break-inside:avoid}img{max-height:125mm;width:auto;max-width:100%;margin:auto}h2,h3{break-after:avoid}@page{size:A4;margin:16mm}}"""
	page = (
		'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HMS user guide</title><style>'
		+ css
		+ '</style></head><body><header><p class="category">HMS · Staff workflows · Edition '
		+ E(book["updated"])
		+ '</p><h1>HMS user guide</h1><p>Step-by-step instructions for reception, clinical care, inpatient care, pharmacy and billing on standalone HMS.</p><p class="review">'
		+ E(book["review_notice"])
		+ '</p><p class="notice">'
		+ E(book["media_notice"])
		+ "</p><p>"
		+ E(book["screenshot_notice"])
		+ '</p><button class="print-control" onclick="window.print()">Print / save PDF</button><p class="print-hint">This guide works offline. Select an image to enlarge it. GIF examples open only when selected. To make a PDF, choose Print / save PDF and your browser’s Save as PDF destination.</p><nav id="contents" aria-label="Workflow chapters"><h2>Choose your workflow</h2><ol>'
		+ contents
		+ "</ol></nav></header><main>"
		+ "".join(chapter_html(book, g, entries) for g in entries.values())
		+ "</main></body></html>"
	)
	(ASSETS / "user-guide-print.html").write_text(page)
	checklist = [
		"# Media and verification checklist",
		"",
		"Updated " + book["updated"] + ".",
		"",
		book["review_notice"],
		"",
		book["media_notice"],
		"",
		"GIFs must come from continuous screen recordings with visible cursor movement and click indicators. Media marked Pending is not complete; verify the intended computer and browser before any new recording.",
		"",
		"| Workflow | Stills | GIF | Coverage / remaining work |",
		"|---|---:|---|---|",
	]
	checklist += [
		f'| [{g["title"]}](user-guide/{g["id"]}.md) | {len(g["screenshots"])} | {g["walkthrough"]["coverage"] if g.get("walkthrough") else "Pending"} | {g["media_note"]} |'
		for g in entries.values()
	]
	checklist += [
		"",
		"For every chapter, end-to-end role testing, error recovery, direct links, narrow layout and final media-to-instructions review remain required before setting `verified_on`.",
		"",
	]
	(ROOT / "docs/USER-GUIDE-MEDIA-STATUS.md").write_text("\n".join(checklist))
	if bundle:
		bundle = bundle.resolve()
		bundle.mkdir(parents=True, exist_ok=True)
		shutil.copytree(ROOT / "docs", bundle / "docs", dirs_exist_ok=True)
		shutil.copytree(ASSETS, bundle / "hms/public/docs", dirs_exist_ok=True)
		(bundle / "index.html").write_text(
			page.replace('src="screenshots/', 'src="hms/public/docs/screenshots/')
			.replace('href="screenshots/', 'href="hms/public/docs/screenshots/')
			.replace('href="walkthroughs/', 'href="hms/public/docs/walkthroughs/')
		)
		(bundle / "README.md").write_text(
			"# HMS user guide — offline edition\n\nOpen `index.html` in a browser, or `docs/user-guide/README.md` for Markdown. Keep the folders together so images and GIF links work. Print / Save as PDF is available from the HTML edition.\n\n"
			+ book["review_notice"]
			+ "\n\n"
			+ book["media_notice"]
			+ "\n"
		)
		shutil.make_archive(str(bundle), "zip", bundle)
	print(
		f"Exported {len(entries)} chapters, printable HTML and media checklist"
		+ ("; offline folder and ZIP created" if bundle else "")
	)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"--bundle", type=Path, help="Optional offline output directory (also creates a sibling ZIP)"
	)
	export(parser.parse_args().bundle)
