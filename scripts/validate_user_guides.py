"""Check guide content, generated text, media provenance and portable local links."""

import argparse
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from export_user_guides import chapter_markdown

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "hms/public/docs"
ROLES = {"Doctor", "Receptionist", "Pharmacist", "System Manager"}
EXPECTED = {
	"start",
	"hospital-live",
	"registration",
	"duplicates",
	"staff",
	"booking",
	"check-in",
	"consultation",
	"labs",
	"reminders",
	"follow-ups",
	"eligibility",
	"admission",
	"care",
	"discharge",
	"departures",
	"intake",
	"dispense",
	"stock-adjustments",
	"billing",
	"reporting",
	"legacy",
}


class Links(HTMLParser):
	def __init__(self):
		super().__init__()
		self.links, self.ids = [], []

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if "id" in attrs:
			self.ids.append(attrs["id"])
		for attr in ("href", "src"):
			if attrs.get(attr):
				self.links.append(attrs[attr])


def check(condition, message):
	if not condition:
		raise ValueError(message)


def validate_links(file, boundary):
	text = file.read_text()
	if file.suffix == ".html":
		parser = Links()
		parser.feed(text)
		links, ids = parser.links, parser.ids
		check(len(ids) == len(set(ids)), f"Duplicate anchors in {file}")
	else:
		links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
		ids = []
	for link in links:
		url = urlsplit(link)
		if url.scheme or url.netloc or link.startswith("/"):
			continue
		if not url.path:
			if file.suffix == ".html" and url.fragment:
				check(unquote(url.fragment) in ids, f"Missing anchor {link} in {file}")
			continue
		target = (file.parent / unquote(url.path)).resolve()
		check(target.is_relative_to(boundary.resolve()), f"Link escapes package: {link} in {file}")
		check(target.is_file(), f"Broken local link: {link} in {file}")


def validate(bundle=None):
	book = json.loads((ASSETS / "user-guide.json").read_text())
	entries = {g["id"]: g for g in book["guides"]}
	check(len(entries) == len(book["guides"]) and set(entries) == EXPECTED, "Missing or duplicate chapters")
	definitions = [json.loads(p.read_text()) for p in (ROOT / "hms/hms/doctype").glob("*/*.json")]
	doctypes = {d["name"] for d in definitions if d.get("doctype") == "DocType"}
	pages = {json.loads(p.read_text())["name"] for p in (ROOT / "hms/hms/page").glob("*/*.json")}
	workspaces = {p.stem.replace("_", "-") for p in (ROOT / "hms/hms/workspace").glob("*/*.json")}
	printable = ASSETS / "user-guide-print.html"
	page = printable.read_text()
	check(html.escape(book["media_notice"]) in page, "Regenerate printable notice")
	stills, gifs = set(), set()
	for guide in entries.values():
		id = guide["id"]
		for field in (
			"title",
			"category",
			"audience",
			"summary",
			"description",
			"prerequisites",
			"steps",
			"check",
			"note",
			"route",
			"media_note",
			"reviewed_on",
			"verification_note",
		):
			check(guide.get(field), f"Missing {field} in {id}")
		check(set(guide["roles"]) <= ROLES and guide["roles"], f"Unknown roles in {id}")
		check(len(guide["steps"]) >= 3, f"Too few steps in {id}")
		check(
			set(guide["related"]) <= entries.keys() and id not in guide["related"],
			f"Invalid related chapter in {id}",
		)
		route = guide["route"]
		check(
			(route[0] == "List" and len(route) == 2 and route[1] in doctypes)
			or (len(route) == 1 and route[0] in workspaces | pages),
			f"Unknown workflow route in {id}",
		)
		for step in guide["steps"]:
			check(step.get("title") and step.get("detail"), f"Empty step in {id}")
			check(html.escape(step["detail"]) in page, f"Stale printable steps for {id}")
		for screen in guide["screenshots"]:
			check(
				Path(screen["file"]).name == screen["file"] and screen["caption"],
				f"Unsafe or unlabelled screenshot in {id}",
			)
			check((ASSETS / "screenshots" / screen["file"]).is_file(), f"Missing screenshot in {id}")
			stills.add(screen["file"])
		motion = guide.get("walkthrough")
		if motion:
			check(
				guide["screenshots"] and motion["coverage"] in ("Partial workflow", "Complete workflow"),
				f"Missing poster or coverage in {id}",
			)
			check(Path(motion["file"]).name == motion["file"] and motion["caption"], f"Unsafe GIF in {id}")
			check(
				(ASSETS / "walkthroughs" / motion["file"]).read_bytes()[:6] in (b"GIF87a", b"GIF89a"),
				f"Invalid GIF in {id}",
			)
			gifs.add(motion["file"])
		file = ROOT / "docs/user-guide" / (id + ".md")
		check(file.read_text() == chapter_markdown(book, guide, entries), f"Regenerate Markdown for {id}")
		if guide.get("verified_on"):
			evidence = guide.get("verification_evidence", {})
			check(
				evidence.get("revision") and evidence.get("roles") and evidence.get("notes"),
				f"Record revision, roles and verification notes before marking {id} verified",
			)
	provenance = json.loads((ASSETS / "media-provenance.json").read_text())
	check({w["file"] for w in provenance["workflows"]} == gifs, "GIF provenance does not match manifest")
	for workflow in provenance["workflows"]:
		check(
			workflow.get("capture_method") == "continuous-screen-recording",
			f"GIF is not a continuous screen recording: {workflow['id']}",
		)
		check(
			workflow.get("cursor_visible") is True and workflow.get("click_indicators_visible") is True,
			f"Cursor/click evidence missing in {workflow['id']}",
		)
		check(
			workflow.get("source_recording_sha256")
			and workflow.get("duration_seconds", 0) > 1
			and workflow.get("recorded_on")
			and workflow.get("device_verified"),
			f"Recording provenance incomplete in {workflow['id']}",
		)
		file = ASSETS / "walkthroughs" / workflow["file"]
		check(
			hashlib.sha256(file.read_bytes()).hexdigest() == workflow["sha256"],
			f"GIF changed without provenance: {file.name}",
		)
	for file in [
		printable,
		*sorted((ROOT / "docs/user-guide").glob("*.md")),
		*sorted((ROOT / "docs").glob("USER-GUIDE*.md")),
	]:
		validate_links(file, ROOT)
	if bundle:
		check((bundle / "index.html").is_file(), "Offline index missing")
		for file in [*bundle.rglob("*.html"), *bundle.rglob("*.md")]:
			validate_links(file, bundle)
		for file in ASSETS.rglob("*"):
			if file.is_file():
				check(
					(bundle / "hms/public/docs" / file.relative_to(ASSETS)).read_bytes() == file.read_bytes(),
					f"Stale bundled asset {file.name}",
				)
	print(
		f"PASS: {len(entries)} chapters, source routes, generated text, {len(stills)} referenced stills, {len(gifs)} GIFs, provenance and local links"
		+ ("; offline bundle checked" if bundle else "")
	)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--bundle", type=Path)
	validate(parser.parse_args().bundle)
