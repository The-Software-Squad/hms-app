/* global hms */
frappe.provide("hms");

hms.HospitalLive = class {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Hospital Live"),
			single_column: true,
		});
		this.names = false;
		this.roomPage = 0;
		this.filter = "all";
		this.active = false;
		this.paused = false;
		this.root = document.createElement("div");
		this.root.className = "hospital-live";
		this.page.body.append(this.root);
		this.page.set_secondary_action(__("User guide"), () =>
			frappe.set_route("hms-guide", "hospital-live")
		);
		this.root.innerHTML = `
   <header class="hl-header"><div><p class="hl-eyebrow"><span class="hl-mark">H<span>+</span></span> THE HOSPITAL, AT A GLANCE</p><h1>Care in motion<span>.</span></h1><p class="hl-subtitle">Every arrival, consultation and handover. One shared picture.</p></div><div class="hl-header-actions"><span class="hl-connection" aria-live="polite"><i></i><span>Connecting to HMS</span></span><button class="hl-button" data-action="refresh">↻ <span>Refresh</span></button><button class="hl-button" data-action="configure" hidden>Configure layout</button></div></header>
   <section class="hl-metrics" aria-label="Recorded hospital activity"></section>
   <div class="hl-workbench"><section class="hl-map-panel"><div class="hl-map-toolbar"><div><span class="hl-section-kicker">LIVE FLOOR</span><span class="hl-schematic">Grouped schematic</span></div><div class="hl-view-controls"><button data-action="pause" aria-pressed="false">Pause updates</button><button data-action="names" aria-pressed="false">Show patient names</button><button data-action="top">Top view</button><button data-action="home">Reset view</button><button data-action="full">Expand</button></div></div><div class="hl-scene" tabindex="0"><div class="hl-loading"><span></span>Preparing the hospital floor…</div></div><div class="hl-map-bottom"><div class="hl-legend"><span class="hl-dot waiting">Waiting</span><span class="hl-dot consultation">In consultation</span><span class="hl-dot diagnostics">Diagnostics</span><span class="hl-dot pharmacy">Pharmacy</span><span class="hl-dot inpatient">Inpatient</span></div><div class="hl-camera-buttons"><button data-action="minus" aria-label="Zoom out">−</button><button data-action="plus" aria-label="Zoom in">+</button></div></div><div class="hl-map-caption"><span>Drag to orbit · Shift + drag to pan · Scroll to zoom · Select a room or person</span><div class="hl-pagination"><button data-action="previous" aria-label="Previous rooms">←</button><span></span><button data-action="next" aria-label="Next rooms">→</button></div></div></section>
   <aside class="hl-inspector" aria-live="polite"><div class="hl-selection"></div><div class="hl-room-list"></div></aside></div>
   <div class="hl-notice" role="status"></div><section class="hl-activity"><div class="hl-activity-header"><div><span class="hl-section-kicker">FROM YOUR HMS RECORDS</span><h2>Activity on the floor</h2></div><div class="hl-filters" role="group" aria-label="Filter hospital activity"><button data-filter="all" class="is-active">All</button><button data-filter="waiting">Waiting</button><button data-filter="consultation">Consultations</button><button data-filter="diagnostics">Diagnostics</button><button data-filter="pharmacy">Pharmacy</button><button data-filter="inpatient">Inpatients</button><button data-filter="earlier">Earlier open visits</button></div></div><div class="hl-activity-list"></div></section>
   <footer class="hl-footer"><span>Characters follow recorded HMS actions. Seats and paths are schematic, not physical tracking.</span><span class="hl-last-updated"></span></footer>`;
		this.root
			.querySelectorAll("[data-action]")
			.forEach((button) =>
				button.addEventListener("click", () => this.action(button.dataset.action))
			);
		this.root.querySelectorAll("[data-filter]").forEach((button) =>
			button.addEventListener("click", () => {
				this.filter = button.dataset.filter;
				this.renderActivity();
			})
		);
		this.page.set_indicator(__("Connecting"), "gray");
		$(wrapper).on("hide", () => this.hide());
		this.visibility = () => {
			if (this.active) {
				this.scene?.setActive(!document.hidden);
				if (!document.hidden && !this.paused) this.refresh();
			}
		};
		document.addEventListener("visibilitychange", this.visibility);
		this.ready = import("/assets/hms/js/hospital_live_model.mjs?v=20261029-2").then((module) => {
			this.modelModule = module;
		});
	}
	el(selector) {
		return this.root.querySelector(selector);
	}
	node(tag, className, text) {
		const e = document.createElement(tag);
		if (className) e.className = className;
		if (text !== undefined) e.textContent = text;
		return e;
	}
	show() {
		if (this.active) return;
		this.active = true;
		this.scene?.setActive(true);
		this.refresh();
		this.timer = setInterval(() => {
			if (!this.paused && !document.hidden) this.refresh();
		}, 15000);
	}
	hide() {
		this.active = false;
		clearInterval(this.timer);
		this.scene?.setActive(false);
	}
	async initScene() {
		if (this.scene || this.sceneFailed) return;
		const host = this.el(".hl-scene");
		try {
			const { HospitalScene } = await import("/assets/hms/js/hospital_live_scene.mjs?v=20261029-2");
			if (!this.active) return;
			host.replaceChildren();
			this.scene = new HospitalScene(host, {
				onSelect: (data) => this.select(data),
				onError: (message) => this.sceneError(message),
			});
		} catch (error) {
			this.sceneError(
				"3D is unavailable in this browser. All permitted activity is available in the list below."
			);
			console.warn("Hospital Live renderer unavailable", error);
		}
	}
	sceneError(message) {
		this.sceneFailed = true;
		this.scene?.setActive(false);
		const host = this.el(".hl-scene");
		const note = this.node("div", "hl-renderer-notice", message);
		host.appendChild(note);
	}
	async refresh() {
		if (this.loading || !this.active) return;
		this.loading = true;
		this.el('[data-action="refresh"]').disabled = true;
		try {
			await this.ready;
			const { message } = await frappe.call({
				method: "hms.api.hospital_live.snapshot",
				type: "GET",
				quiet: true,
			});
			if (!this.active) return;
			this.snapshot = message;
			await this.initScene();
			if (!this.active) return;
			this.render();
			this.lastSuccess = Date.now();
			this.connection(
				this.paused ? "Updates paused" : "Connected · updates every 15s",
				this.paused ? "paused" : "connected"
			);
		} catch (error) {
			const denied =
				error?.httpStatus === 403 ||
				error?.status === 403 ||
				error?.statusCode === 403 ||
				error?.exc_type === "PermissionError";
			if (denied) {
				this.snapshot = null;
				this.selected = null;
				this.scene?.dispose();
				this.scene = null;
				this.root
					.querySelectorAll(".hl-selection,.hl-room-list,.hl-activity-list,.hl-metrics")
					.forEach((e) => e.replaceChildren());
			}
			this.connection(
				denied ? "Access restricted" : "Connection interrupted · showing last update",
				"error"
			);
			this.el(".hl-notice").textContent = denied
				? "Your roles do not permit this view. Contact your System Manager."
				: "The display could not refresh. Data is stale until a successful update; use Refresh to try again.";
		} finally {
			this.loading = false;
			this.el('[data-action="refresh"]').disabled = false;
		}
	}
	connection(text, state) {
		const e = this.el(".hl-connection");
		e.className = `hl-connection ${state}`;
		e.lastElementChild.textContent = text;
		this.page.set_indicator(
			__(state === "connected" ? "Connected" : state === "paused" ? "Paused" : "Stale"),
			state === "connected" ? "green" : state === "paused" ? "orange" : "red"
		);
	}
	render({ animate = true } = {}) {
		if (!this.snapshot || !this.modelModule) return;
		const { derive } = this.modelModule;
		this.roomPage = Math.min(
			this.roomPage,
			Math.max(0, Math.ceil(this.snapshot.rooms.length / 6) - 1)
		);
		this.model = derive(this.snapshot, this.roomPage);
		const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
		this.scene?.setModel(this.model, { animate: animate && !reduced });
		const metrics = [
			["waiting", "Waiting for doctor", "Checked in · ready to be seen"],
			["consultation", "In consultation", "Active consultation records"],
			["diagnostics", "Diagnostics", "Visits awaiting diagnostics"],
			["pharmacy", "Awaiting collection", "Posted sales still to hand over"],
			["inpatient", "Inpatient care", "Open admissions"],
		];
		const target = this.el(".hl-metrics");
		target.replaceChildren();
		for (const [key, label, detail] of metrics) {
			const card = this.node("div", `hl-metric ${key}`);
			card.append(
				this.node("span", "hl-metric-label", label),
				this.node("strong", "", String(this.model.stats[key])),
				this.node("span", "hl-metric-detail", detail)
			);
			target.appendChild(card);
		}
		this.el('[data-action="configure"]').hidden = !this.snapshot.can_configure;
		this.el(".hl-pagination span").textContent = this.snapshot.rooms.length
			? `Rooms ${this.roomPage * 6 + 1}–${Math.min(
					this.snapshot.rooms.length,
					(this.roomPage + 1) * 6
			  )} of ${this.snapshot.rooms.length}`
			: "No doctor rooms";
		this.el('[data-action="previous"]').disabled = this.roomPage === 0;
		this.el('[data-action="next"]').disabled = this.roomPage >= this.model.pages - 1;
		const notes = [];
		if (!this.snapshot.rooms.length)
			notes.push(
				"No doctor rooms are available for your role. A System Manager can configure rooms and waiting seats in Hospital Settings."
			);
		if (this.snapshot.older_visits?.length)
			notes.push(
				`${this.snapshot.older_visits.length} earlier outpatient visits are still open. Review Earlier open visits; they are excluded from today’s waiting seats.`
			);
		if (this.model.overflow)
			notes.push(
				`${this.model.overflow} waiting patients exceed the displayed seat capacity.`
			);
		if (this.model.unmapped)
			notes.push(
				`${this.model.unmapped} patient placements belong to doctors outside this room view. All permitted records remain in the activity list.`
			);
		if (this.model.hiddenBeds)
			notes.push(
				`${this.model.hiddenBeds} additional beds are listed in HMS; the schematic displays the first 24.`
			);
		if (this.scene?.hiddenActors)
			notes.push(
				`${this.scene.hiddenActors} additional people are available in the activity list; the 3D view displays up to 160 at once.`
			);
		if (this.snapshot.truncated.length)
			notes.push(
				`Results are limited to 1,000 per record type: ${this.snapshot.truncated.join(
					", "
				)}. Use the original HMS lists for the full totals.`
			);
		const restricted = Object.entries(this.snapshot.access)
			.filter(([, allowed]) => !allowed)
			.map(([name]) => name);
		if (restricted.length)
			notes.push(
				`Your role does not include: ${restricted.join(
					", "
				)}. Counts cover permitted records only.`
			);
		this.el(".hl-notice").textContent = notes.join(" ");
		this.el(
			".hl-last-updated"
		).textContent = `Last HMS snapshot: ${frappe.datetime.str_to_user(this.snapshot.as_of)}`;
		this.renderRooms();
		this.renderSelection();
		this.renderActivity();
	}
	displayName(row) {
		return this.names ? row.patient_label || row.label || "Patient" : row.label || "Patient";
	}
	renderRooms() {
		const target = this.el(".hl-room-list");
		target.replaceChildren(this.node("h3", "", "Doctor rooms"));
		for (const room of this.model.rooms) {
			const button = this.node("button", "hl-room-card");
			button.type = "button";
			const busy = room.current.length > 0;
			button.append(
				this.node("span", "hl-room-number", room.room_name),
				this.node("strong", "", room.doctor),
				this.node("span", "hl-room-department", room.department)
			);
			const line = this.node(
				"span",
				`hl-room-state ${busy ? "busy" : ""}`,
				busy ? `${room.current.length} in consultation` : room.availability
			);
			button.append(
				line,
				this.node(
					"span",
					"hl-room-count",
					`${room.waiting.length} waiting · ${room.scheduled} booked today`
				)
			);
			button.addEventListener("click", () => this.select({ kind: "room", room }));
			target.appendChild(button);
		}
	}
	select(data) {
		this.selected = data;
		this.renderSelection();
	}
	renderSelection() {
		const target = this.el(".hl-selection");
		target.replaceChildren();
		if (!this.selected) {
			target.append(
				this.node("span", "hl-section-kicker", "EXPLORE THE FLOOR"),
				this.node("h2", "", "A seat for every next step."),
				this.node(
					"p",
					"",
					"Select a doctor’s room or a person to see the HMS activity behind them."
				)
			);
			const note = this.node(
				"div",
				"hl-action-note",
				"Check in → wait → consultation → next care step. Characters move only when the recorded state changes."
			);
			target.append(note);
			return;
		}
		if (this.selected.kind === "room") {
			const room = this.model.rooms.find((r) => r.id === this.selected.room.id);
			if (!room) {
				this.selected = null;
				this.renderSelection();
				return;
			}
			this.selected = { kind: "room", room };
			target.append(
				this.node("span", "hl-section-kicker", room.room_name),
				this.node("h2", "", room.doctor),
				this.node("p", "", room.department)
			);
			target.append(
				this.node(
					"div",
					"hl-detail-status",
					`${room.availability}${
						room.availability_updated_on
							? " · " + frappe.datetime.str_to_user(room.availability_updated_on)
							: " · no availability report today"
					}`
				)
			);
			if (room.current.length > 1)
				target.append(
					this.node(
						"p",
						"hl-warning",
						"Multiple consultations are active for this doctor. Review their visit statuses."
					)
				);
			for (const visit of room.current) {
				const activity = this.model.activities.find((a) => a.source_name === visit.name);
				this.recordButton(target, activity, "Current: " + this.displayName(activity));
			}
			target.append(
				this.node(
					"p",
					"",
					`${room.waiting.length} waiting · ${room.seats} seats · ${room.scheduled} scheduled, not checked in`
				)
			);
			if (room.can_update_availability) {
				const controls = this.node("div", "hl-availability");
				for (const status of ["Available", "Away", "Off Duty"]) {
					const button = this.node("button", "hl-small-button", status);
					button.disabled = room.availability === status;
					button.addEventListener("click", () =>
						this.reportAvailability(room.id, status)
					);
					controls.appendChild(button);
				}
				target.append(controls);
			}
			target.append(
				this.node(
					"p",
					"hl-fine-print",
					"Availability is reported by staff and resets to Not Recorded on a new day. Consultation figures come from visit statuses."
				)
			);
		} else if (this.selected.kind === "zone") {
			target.append(
				this.node("span", "hl-section-kicker", "CARE AREA"),
				this.node(
					"h2",
					"",
					{
						waiting: "Reception & waiting",
						diagnostics: "Diagnostics",
						prescription: "Follow-up & exit",
						pharmacy: "Pharmacy",
						inpatient: "Inpatient care",
					}[this.selected.stage]
				)
			);
			const button = this.node("button", "hl-button", "Show related activity");
			button.addEventListener("click", () => {
				this.filter = this.selected.stage;
				this.renderActivity();
				this.el(".hl-activity").scrollIntoView({ behavior: "smooth", block: "start" });
			});
			target.append(button);
		} else {
			const activity = this.model.activities.find(
				(a) =>
					a.source_type === this.selected.source_type &&
					a.source_name === this.selected.source_name
			);
			if (!activity) {
				target.append(this.node("h2", "", "This activity has left the active view."));
				return;
			}
			this.selected = activity;
			target.append(
				this.node("span", "hl-section-kicker", "RECORDED ACTIVITY"),
				this.node("h2", "", this.displayName(activity)),
				this.node("div", `hl-status ${activity.stage}`, activity.status),
				this.node("p", "", activity.doctor)
			);
			if (activity.previous_day)
				target.append(
					this.node(
						"p",
						"hl-warning",
						"This active visit is from an earlier date. Review its status in HMS."
					)
				);
			this.recordButton(target, activity, "Open HMS record");
			target.append(
				this.node(
					"p",
					"hl-fine-print",
					"The character’s position represents the workflow stage. It does not confirm the person’s physical location."
				)
			);
		}
	}
	recordButton(parent, activity, label) {
		if (!activity) return;
		const button = this.node("button", "hl-record-link", label);
		button.addEventListener("click", () =>
			frappe.set_route("Form", activity.source_type, activity.source_name)
		);
		parent.appendChild(button);
	}
	renderActivity() {
		if (!this.model) return;
		const target = this.el(".hl-activity-list");
		target.replaceChildren();
		this.root
			.querySelectorAll("[data-filter]")
			.forEach((b) => b.classList.toggle("is-active", b.dataset.filter === this.filter));
		const activities = this.model.activities.filter(
			(a) => this.filter === "all" || a.stage === this.filter
		);
		if (!activities.length) {
			target.append(
				this.node(
					"div",
					"hl-empty",
					"No active records in this view. The floor updates when staff check in patients or change HMS workflow status."
				)
			);
			return;
		}
		for (const activity of activities.slice(0, 200)) {
			const row = this.node("button", "hl-activity-row");
			row.type = "button";
			row.append(
				this.node(
					"span",
					`hl-avatar ${activity.stage}`,
					this.displayName(activity).slice(0, 1)
				),
				this.node("strong", "", this.displayName(activity)),
				this.node("span", "hl-activity-doctor", activity.doctor),
				this.node("span", `hl-status ${activity.stage}`, activity.status),
				this.node("span", "hl-row-arrow", "↗")
			);
			row.addEventListener("click", () => {
				this.select(activity);
				this.el(".hl-selection").scrollIntoView({ behavior: "smooth", block: "nearest" });
			});
			target.append(row);
		}
		if (activities.length > 200)
			target.append(
				this.node(
					"p",
					"hl-fine-print",
					`Showing 200 of ${activities.length} permitted activity records. Filter by care area or open the original HMS record list.`
				)
			);
	}
	async reportAvailability(practitioner, status) {
		try {
			await frappe.call({
				method: "hms.api.hospital_live.set_availability",
				type: "POST",
				args: { practitioner, status },
				freeze: true,
			});
			await this.refresh();
		} catch {
			this.connection("Availability could not be saved", "error");
		}
	}
	action(action) {
		if (action === "refresh") return this.refresh();
		if (action === "configure") return frappe.set_route("Form", "Hospital Settings");
		if (action === "pause") {
			this.paused = !this.paused;
			const b = this.el('[data-action="pause"]');
			b.textContent = this.paused ? "Resume updates" : "Pause updates";
			b.setAttribute("aria-pressed", String(this.paused));
			this.connection(
				this.paused ? "Updates paused" : "Refreshing…",
				this.paused ? "paused" : "connected"
			);
			if (!this.paused) this.refresh();
			return;
		}
		if (action === "names") {
			this.names = !this.names;
			const b = this.el('[data-action="names"]');
			b.textContent = this.names ? "Hide patient names" : "Show patient names";
			b.setAttribute("aria-pressed", String(this.names));
			this.renderSelection();
			this.renderActivity();
			return;
		}
		if (action === "previous" || action === "next") {
			this.roomPage += action === "next" ? 1 : -1;
			this.selected = null;
			return this.render({ animate: false });
		}
		if (action === "home") this.scene?.home();
		if (action === "top") this.scene?.top();
		if (action === "plus") this.scene?.zoomBy(1.2);
		if (action === "minus") this.scene?.zoomBy(0.83);
		if (action === "full") {
			this.root.classList.toggle("hl-expanded");
			this.el('[data-action="full"]').textContent = this.root.classList.contains(
				"hl-expanded"
			)
				? "Collapse"
				: "Expand";
			this.scene?.resize();
		}
	}
};
