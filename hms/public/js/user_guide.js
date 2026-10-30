/* HMS owns this reader and its content; no other application is required. */
/* global hms */
frappe.provide("hms");
(() => {
	if (hms.UserGuide) return;
	const element = (tag, text, cls) => {
		const node = document.createElement(tag);
		if (text !== undefined) node.textContent = text;
		if (cls) node.className = cls;
		return node;
	};
	const chapterLink = (title, id = "", cls = "") => {
		const link = element("a", title, cls);
		link.href = "/desk/hms-guide" + (id ? "/" + encodeURIComponent(id) : "");
		return link;
	};
	const mediaPath = (folder, file) =>
		"/assets/hms/docs/" + folder + "/" + encodeURIComponent(file) + "?v=7";
	hms.UserGuide = class {
		constructor(wrapper) {
			this.page = frappe.ui.make_app_page({
				parent: wrapper,
				title: __("HMS User Guide"),
				single_column: true,
			});
			this.root = element("div", undefined, "hms-guide-root");
			this.page.main[0].append(this.root);
			this.show();
		}
		async show() {
			const generation = (this.generation = (this.generation || 0) + 1);
			this.root.replaceChildren(element("p", __("Loading user guide…"), "hg-footnote"));
			try {
				if (!this.book) {
					this.loading ||= fetch("/assets/hms/docs/user-guide.json?v=7", {
						credentials: "same-origin",
					})
						.then((response) => {
							if (!response.ok) throw new Error("Guide request failed");
							return response.json();
						})
						.catch((error) => {
							this.loading = null;
							throw error;
						});
					this.book = await this.loading;
				}
				if (generation !== this.generation) return;
				this.root.replaceChildren();
				const id = frappe.get_route()[1];
				const guide = this.book.guides.find((entry) => entry.id === id);
				this.page.set_secondary_action(__("Print all chapters"), () =>
					window.open("/assets/hms/docs/user-guide-print.html", "_blank", "noopener")
				);
				if (id && !guide) {
					this.page.set_title(__("HMS User Guide"));
					this.root.append(
						element("h2", __("Guide not found")),
						element("p", __("Choose a chapter from the user guide.")),
						chapterLink(__("All workflows"))
					);
				} else if (guide) this.article(guide);
				else this.home();
			} catch (error) {
				if (generation !== this.generation) return;
				const retry = element("button", __("Try again"), "btn btn-default");
				retry.onclick = () => this.show();
				this.root.replaceChildren(
					element("h2", __("User guide could not load")),
					element(
						"p",
						__("Check your connection, then try again. Your records have not changed.")
					),
					retry
				);
			}
		}
		groups() {
			return [...new Set(this.book.guides.map((guide) => guide.category))];
		}
		home() {
			this.page.set_title(__("HMS User Guide"));
			this.page.clear_primary_action();
			const hero = element("section", undefined, "hg-hero");
			hero.append(
				element("div", "HMS · Staff workflows", "hg-eyebrow"),
				element("h2", "What would you like to do?"),
				element(
					"p",
					"Find the steps for reception, clinical care, inpatient care, pharmacy and billing. Each chapter includes prerequisites, expected results and recovery advice. Available screenshots and screen recordings illustrate the steps.",
					"hg-intro"
				),
				element("p", this.book.media_notice, "hg-footnote")
			);
			const filters = element("div", undefined, "hg-filters");
			const search = element("input", undefined, "form-control");
			search.type = "search";
			search.placeholder = "Search a task, button or status";
			search.setAttribute("aria-label", "Search user guide");
			const category = element("select", undefined, "form-control");
			category.setAttribute("aria-label", "Workflow category");
			const role = element("select", undefined, "form-control");
			role.setAttribute("aria-label", "Workflow role");
			for (const name of ["All categories", ...this.groups()]) {
				const option = element("option", name);
				option.value = name;
				category.append(option);
			}
			for (const name of [
				"All roles",
				"My roles",
				"Receptionist",
				"Doctor",
				"Pharmacist",
				"System Manager",
			]) {
				const option = element("option", name);
				option.value = name;
				role.append(option);
			}
			filters.append(search, category, role);
			hero.append(filters);
			const count = element("p", undefined, "hg-footnote");
			count.setAttribute("role", "status");
			count.setAttribute("aria-live", "polite");
			hero.append(count);
			const results = element("div");
			this.root.append(hero, results);
			const render = () => {
				const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
				const matches = this.book.guides.filter(
					(guide) =>
						(category.value === "All categories" ||
							category.value === guide.category) &&
						(role.value === "All roles" ||
							(role.value === "My roles"
								? guide.roles.some((name) => frappe.user_roles.includes(name))
								: guide.roles.includes(role.value))) &&
						words.every((word) => JSON.stringify(guide).toLowerCase().includes(word))
				);
				count.textContent = `${matches.length} of ${this.book.guides.length} workflows · Role labels describe who can perform the task`;
				results.replaceChildren();
				for (const group of this.groups()) {
					const entries = matches.filter((guide) => guide.category === group);
					if (!entries.length) continue;
					const section = element("section", undefined, "hg-group");
					section.append(element("h3", group));
					const cards = element("div", undefined, "hg-cards");
					for (const guide of entries) {
						const card = chapterLink("", guide.id, "hg-card");
						card.append(
							element("h4", guide.title),
							element("p", guide.summary),
							element("span", guide.audience, "hg-badge")
						);
						cards.append(card);
					}
					section.append(cards);
					results.append(section);
				}
				if (!matches.length)
					results.append(
						element(
							"p",
							"No workflows match. Try a shorter search or reset the category and role filters.",
							"hg-empty"
						)
					);
			};
			search.oninput = render;
			category.onchange = render;
			role.onchange = render;
			render();
			this.footnote(this.root);
		}
		footnote(parent, guide) {
			const review = guide?.verified_on
				? "Workflow verified " + guide.verified_on + "."
				: guide
				? "Written instructions source reviewed " +
				  guide.reviewed_on +
				  ". " +
				  guide.verification_note
				: this.book.review_notice;
			parent.append(element("p", this.book.screenshot_notice + " " + review, "hg-footnote"));
		}
		screenshot(screen) {
			const figure = element("figure", undefined, "hg-figure");
			const link = element("a");
			link.href = mediaPath("screenshots", screen.file);
			link.target = "_blank";
			link.rel = "noopener noreferrer";
			link.setAttribute("aria-label", "Enlarge screenshot: " + screen.caption);
			const image = element("img");
			image.src = link.href;
			image.alt = screen.caption;
			image.loading = "lazy";
			image.decoding = "async";
			image.onerror = () =>
				link.replaceChildren(
					element(
						"p",
						"Screenshot could not load. The written steps remain available.",
						"hg-footnote"
					)
				);
			link.append(image);
			figure.append(
				link,
				element("figcaption", screen.caption + " Select the image to enlarge.")
			);
			return figure;
		}
		walkthrough(guide) {
			const section = element("details", undefined, "hg-walkthrough");
			section.append(element("summary", "Watch walkthrough (GIF)"));
			const box = element("div", undefined, "hg-motion");
			const image = element("img");
			image.alt = guide.walkthrough.caption;
			image.src = mediaPath("screenshots", guide.screenshots[0].file);
			image.loading = "lazy";
			const controls = element("div", undefined, "hg-motion-controls");
			const play = element("button", "Play walkthrough", "btn btn-default btn-sm");
			play.type = "button";
			const download = element("a", "Open / download GIF", "btn btn-default btn-sm");
			download.href = mediaPath("walkthroughs", guide.walkthrough.file);
			download.target = "_blank";
			download.rel = "noopener noreferrer";
			let playing = false;
			const stop = () => {
				playing = false;
				image.src = mediaPath("screenshots", guide.screenshots[0].file);
				play.textContent = "Play walkthrough";
				play.setAttribute("aria-pressed", "false");
			};
			play.setAttribute("aria-pressed", "false");
			play.onclick = () => {
				if (playing) stop();
				else {
					playing = true;
					image.src = download.href;
					play.textContent = "Stop walkthrough";
					play.setAttribute("aria-pressed", "true");
				}
			};
			section.ontoggle = () => {
				if (!section.open) stop();
			};
			image.onerror = () => {
				image.onerror = null;
				playing = false;
				image.remove();
				play.disabled = true;
				play.textContent = "Walkthrough unavailable";
				play.setAttribute("aria-pressed", "false");
				box.append(
					element(
						"p",
						"Walkthrough could not load. Use the written steps and screenshots.",
						"hg-footnote"
					)
				);
			};
			controls.append(play, download);
			box.append(image, controls, element("p", guide.walkthrough.caption, "hg-footnote"));
			section.append(box);
			return section;
		}
		article(guide) {
			this.page.set_title(__(guide.title));
			this.page.set_primary_action(__("Print / save PDF"), () => window.print());
			this.root.append(chapterLink("← All workflows", "", "hg-back"));
			const layout = element("div", undefined, "hg-layout"),
				nav = element("nav", undefined, "hg-nav");
			nav.setAttribute("aria-label", "Workflow chapters");
			for (const group of this.groups()) {
				nav.append(element("h3", group));
				for (const item of this.book.guides.filter((entry) => entry.category === group)) {
					const link = chapterLink(item.title, item.id);
					if (item.id === guide.id) link.setAttribute("aria-current", "page");
					nav.append(link);
				}
			}
			const article = element("article", undefined, "hg-article");
			article.append(
				element("div", guide.category, "hg-eyebrow"),
				element("h2", guide.title),
				element("p", guide.summary, "hg-intro"),
				element("span", "Who can do this: " + guide.audience, "hg-badge"),
				element("h3", "What this workflow does"),
				element("p", guide.description)
			);
			const prerequisites = element("section", undefined, "hg-callout");
			prerequisites.append(element("strong", "Before you start"));
			const list = element("ul");
			for (const item of guide.prerequisites) list.append(element("li", item));
			prerequisites.append(list);
			article.append(prerequisites);
			const open = element("button", "Open this workflow", "btn btn-default btn-sm hg-open");
			open.type = "button";
			open.onclick = () => frappe.set_route(...guide.route);
			article.append(open);
			article.append(element("p", guide.media_note, "hg-footnote"));
			if (guide.screenshots.length) article.append(this.screenshot(guide.screenshots[0]));
			if (guide.walkthrough && guide.screenshots.length)
				article.append(this.walkthrough(guide));
			const steps = element("ol", undefined, "hg-steps");
			for (const step of guide.steps) {
				const li = element("li");
				li.append(element("h3", step.title), element("p", step.detail));
				steps.append(li);
			}
			article.append(steps);
			if (guide.screenshots.length > 1) {
				const more = element("details", undefined, "hg-more");
				more.append(element("summary", "More screenshots"));
				for (const screen of guide.screenshots.slice(1))
					more.append(this.screenshot(screen));
				article.append(more);
			}
			for (const [title, text, cls] of [
				["What success looks like", guide.check, "hg-callout"],
				["Common problems and recovery", guide.note, "hg-callout hg-note"],
			]) {
				const box = element("aside", undefined, cls);
				box.append(element("strong", title), element("p", text));
				article.append(box);
			}
			const related = element("section", undefined, "hg-related");
			related.append(element("h3", "Related workflows"));
			for (const id of guide.related) {
				const item = this.book.guides.find((entry) => entry.id === id);
				if (item) related.append(chapterLink(item.title, id));
			}
			article.append(related);
			this.footnote(article, guide);
			layout.append(nav, article);
			this.root.append(layout);
		}
	};
	const formGuides = {
		Patient: "registration",
		"Patient Appointment": "booking",
		"Patient Visit": "consultation",
		"Lab Report": "labs",
		"Lab Report Type": "labs",
		"Healthcare Practitioner": "staff",
		"Practitioner Schedule": "staff",
		Employee: "staff",
		"Hospital Settings": "eligibility",
		"Fee Validity": "eligibility",
		"IP Record": "admission",
		Bed: "admission",
		Ward: "admission",
		"In Patient Treatment": "care",
		"Discharge Summary": "discharge",
		Medicine: "reminders",
		"Medicine Timing": "reminders",
		"Meds Provider": "intake",
		"Med Item": "intake",
		"Meds In take": "intake",
		"HMS Stock Lot": "intake",
		"Meds Out": "dispense",
		"HMS Pharmacy Collection": "dispense",
		"HMS Patient Departure": "departures",
		"HMS Stock Movement": "stock-adjustments",
		"HMS Stock Adjustment": "stock-adjustments",
		"HMS Invoice": "billing",
		"Payment Recipit": "billing",
		"HMS Medication Delivery": "reminders",
		"HMS Patient Merge": "duplicates",
	};
	for (const [doctype, id] of Object.entries(formGuides))
		frappe.ui.form.on(doctype, {
			refresh(frm) {
				frm.add_custom_button(
					__("User guide"),
					() => frappe.set_route("hms-guide", id),
					__("Help")
				);
			},
		});
})();
