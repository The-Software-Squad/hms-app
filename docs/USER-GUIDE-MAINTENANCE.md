# Maintaining the HMS user guide

Updated 22 October 2026.

## Source and generated files

`hms/public/docs/user-guide.json` owns all 22 chapters. It contains the purpose, audience, prerequisites, steps, success criteria, recovery, related chapters, Desk route and available media for each workflow. HMS owns the reader and assets and does not depend on WhatsApp Messaging or ERPNext.

| File | Purpose |
|---|---|
| `hms/public/js/user_guide.js` | Search, filters, chapter navigation, form help and manual GIF playback |
| `hms/public/css/user_guide.css` | Reader, small-screen and chapter-print styles |
| `hms/hms/page/hms_guide/` | Standard Frappe Page restricted to HMS staff roles |
| `hms/hms/workspace/*/*.json` | User guide shortcuts in HMS workspaces |
| `docs/user-guide/*.md` | Generated chapter text and index; edit the manifest instead |
| `hms/public/docs/user-guide-print.html` | Generated offline-capable printable edition |
| `docs/USER-GUIDE-QUICK-REFERENCE.md` | Hand-maintained role, state and task reference |
| `docs/USER-GUIDE-MEDIA-STATUS.md` | Generated chapter-by-chapter coverage checklist |
| `scripts/build_guide_walkthroughs.py` | Retired selected-frame builder; explains the recording requirement |
| `hms/public/docs/media-provenance.json` | Continuous recording checksum, device verification, cursor/click evidence, GIF hashes and scope |

Use `/desk/hms-guide` for the reader and `/desk/hms-guide/<chapter-id>` for a chapter. Frappe may add the app prefix to the visible URL. The printable edition is served at `/assets/hms/docs/user-guide-print.html`.

## Make a documentation change

1. Read the actual DocType fields, button definitions, server validators and permissions for the changed task. Use exact labels. For a shared workflow, state who performs each restricted step.
2. Edit the manifest. Keep IDs stable so bookmarks and Help links continue to work. Update `reviewed_on` after checking the written instructions against source.
3. Keep `verified_on` null until that full workflow has been exercised under the appropriate staff roles. When verifying, also add `verification_evidence` with `revision`, `roles` and `notes`. A passing integration test or a screenshot of one state is not a complete browser verification.
4. List only screenshot files that exist and have been reviewed. Set `walkthrough` to null where no usable GIF exists. Keep `media_note` accurate about omitted steps, previews and failed saves.
5. Regenerate the exports, run the checks below and inspect changed media locally. Update the quick reference if roles or state meanings changed.
6. For a release, use the normal HMS installation/migration and asset/cache process. This documentation task does not deploy to production. New Page/workspace metadata needs normal Frappe synchronization; source assets alone do not guarantee the metadata is installed on another site.

```bash
# Run from the HMS app directory. These commands require only Python's standard library.
python3 scripts/export_user_guides.py
python3 scripts/validate_user_guides.py
```

To create a portable folder and a sibling ZIP, choose a destination:

```bash
python3 scripts/export_user_guides.py --bundle /path/to/outputs/HMS-user-guide
python3 scripts/validate_user_guides.py --bundle /path/to/outputs/HMS-user-guide
```

Open the bundle's `index.html` manually to read the guide offline. Keep all folders together. The HTML edition offers Print / save PDF; no separate PDF artifact is currently supplied. GIFs are linked instead of automatically animated in the printable edition.

## Capture and convert workflow recordings

The local MacBook Air and its Chrome window were verified for capture on 19 October. Browser connectors can route to another computer, so recheck the intended computer and window before starting a new recording session. Native control of Codex's own window is blocked; do not bypass that block.

Use the disposable `hms-workflow-test.localhost` site with coherent examples such as Maya Patel, Dr Alex Morgan and Paracetamol 500 mg. Use reserved example contact destinations; leave the scheduler disabled and mock email/provider calls. Include no credentials, private operational files or patient data from the main site in published media.

Record the actual browser workflow continuously with the cursor and click indicators visible. Crop out tabs, the address bar and other applications. Verify the actual clicks and pointer are present in the source recording, then convert that recording into a GIF. A sequence of selected screenshots does not satisfy this requirement.

The previous selected-frame GIFs and stills are superseded and archived in task working files. They are not referenced by the current guide. `scripts/build_guide_walkthroughs.py` is retired from the publishing workflow; do not run it to create replacement media. The old frame-selection inventory is archived in task working files; it is not part of the current guide.

Keep the original recording, its checksum, capture date, workflow scope, verified cursor/click visibility and the resulting GIF checksum in the release evidence. Update `user-guide.json` only after visual review. The validator requires continuous-screen-recording provenance, a verified device, positive duration, source/GIF checksums and confirmed cursor/click visibility. Published media remains pending until the actual recordings pass visual review.

Do not label Not Saved as saved, Queued as Sent, Draft as Posted, a preview as a completed action, or a validation failure as success. Do not send a real reminder merely to record a demonstration.

## Before marking a chapter verified

Exercise its positive path and relevant failure/recovery paths using its actual roles. Check direct links, Help/workspace navigation, search and role/category filters, no-results behavior, media loading and fallback, manual GIF play/stop, small-screen overflow and print layout. Compare the final screen labels and stored outcome with each instruction. Record the date and application revision in the release notes and then set `verified_on`. Browser-host verification is a prerequisite to all new capture work.

The validator checks content structure, route targets, related links, real referenced files, provenance hashes, generated-file freshness and local links in the offline bundle. It does not certify application workflows, role enforcement or visual browser behavior.
