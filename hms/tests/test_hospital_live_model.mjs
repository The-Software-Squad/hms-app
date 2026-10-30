import { test } from "node:test";
import assert from "node:assert/strict";
import {
  derive,
  transitions,
  stageFor,
} from "../public/js/hospital_live_model.mjs";
const room = {
  id: "DR-01",
  doctor: "Dr Alex Morgan",
  room_name: "Consultation 01",
  department: "General Medicine",
  seats: 2,
  availability: "Available",
};
const visit = (name, status = "Checked In", patient = "PAT-01") => ({
  name,
  patient,
  patient_label: "Maya Patel",
  doctor: room.id,
  status,
  visit_date: "2026-10-29",
  creation: `2026-10-29 09:${name.endsWith("2") ? "02" : "01"}:00`,
  modified: "2026-10-29 09:05:00",
});
const snapshot = (values = {}) => ({
  date: "2026-10-29",
  rooms: [room],
  visits: [],
  appointments: [],
  pharmacy: [],
  admissions: [],
  beds: [],
  ...values,
});
test("a booked appointment never invents a patient on a seat", () => {
  const m = derive(
    snapshot({ appointments: [{ name: "APT-01", practitioner: room.id }] })
  );
  assert.equal(m.actors.length, 0);
  assert.equal(m.rooms[0].scheduled, 1);
  assert.equal(m.stats.waiting, 0);
});
test("check-in places a patient in their doctor's queue; consultation changes their location", () => {
  const a = derive(snapshot({ visits: [visit("VIS-01")] })),
    b = derive(snapshot({ visits: [visit("VIS-01", "Under Consultation")] }));
  assert.equal(a.actors[0].stage, "waiting");
  assert.equal(b.actors[0].stage, "consultation");
  assert.notDeepEqual(a.actors[0].position, b.actors[0].position);
  assert.equal(transitions(null, a).length, 0);
  assert.equal(transitions(a, b).length, 1);
  assert.equal(transitions(b, b).length, 0);
});
test("closed or departed visits leave the active scene", () => {
  const a = derive(snapshot({ visits: [visit("VIS-01")] }));
  for (const status of ["Completed", "Closed Early", "Cancelled / No Show"]) {
    const b = derive(snapshot({ visits: [visit("VIS-01", status)] }));
    assert.equal(b.actors.length, 0);
    assert.equal(transitions(a, b)[0].leaving, true);
  }
});
test("diagnostics is driven by the visit stage, not an unrelated report", () => {
  const m = derive(
    snapshot({
      visits: [visit("VIS-01", "Lab/Diagnostics Pending")],
      labs: [{ name: "LAB-01", status: "Received" }],
    })
  );
  assert.equal(m.actors[0].stage, "diagnostics");
  assert.equal(stageFor("Lab/Diagnostics Completed"), "waiting");
});
test("prescription and posted uncollected sale project one patient to pharmacy", () => {
  const m = derive(
    snapshot({
      visits: [visit("VIS-01", "Prescription Given")],
      pharmacy: [
        {
          name: "DSP-01",
          patient: "PAT-01",
          patient_visit: "VIS-01",
          patient_label: "Maya Patel",
          collection_status: "Partly Collected",
        },
      ],
    })
  );
  assert.equal(m.actors.length, 1);
  assert.equal(m.actors[0].stage, "pharmacy");
});
test("admission takes precedence over an older OP record, and no random movement is generated", () => {
  const s = snapshot({
    visits: [visit("VIS-01")],
    beds: [{ name: "BED-01", ward: "East Ward", current_admission: "IP-01" }],
    admissions: [
      {
        name: "IP-01",
        patient: "PAT-01",
        patient_label: "Maya Patel",
        bed: "BED-01",
        status: "Admitted",
      },
    ],
  });
  const a = derive(s),
    b = derive(s);
  assert.equal(a.actors.length, 1);
  assert.equal(a.actors[0].stage, "inpatient");
  assert.equal(a.actors[0].lying, true);
  assert.deepEqual(transitions(a, b), []);
});
test("consultation takes priority when one patient has multiple active visit records", () => {
  const m = derive(
    snapshot({
      visits: [visit("VIS-01"), visit("VIS-02", "Under Consultation")],
    })
  );
  assert.equal(m.actors.length, 1);
  assert.equal(m.actors[0].stage, "consultation");
  assert.equal(m.activities.length, 2);
});
test("seat overflow is explicit, with all waiting records retained", () => {
  const m = derive(
    snapshot({
      visits: [
        visit("VIS-01", "Checked In", "PAT-01"),
        visit("VIS-02", "Checked In", "PAT-02"),
        visit("VIS-03", "Checked In", "PAT-03"),
      ],
    })
  );
  assert.equal(m.stats.waiting, 3);
  assert.equal(m.overflow, 1);
  assert.equal(m.actors.length, 3);
});
test("room pagination retains activity and counts outside the current floor view", () => {
  const rooms = Array.from({ length: 7 }, (_, i) => ({
    ...room,
    id: `DR-${i}`,
  }));
  const m = derive(
    snapshot({ rooms, visits: [{ ...visit("VIS-01"), doctor: "DR-6" }] }),
    0
  );
  assert.equal(m.rooms.length, 6);
  assert.equal(m.pages, 2);
  assert.equal(m.unmapped, 1);
  assert.equal(m.activities.length, 1);
  assert.equal(
    derive(
      snapshot({ rooms, visits: [{ ...visit("VIS-01"), doctor: "DR-6" }] }),
      1
    ).actors.length,
    1
  );
});

test("waiting people sit only within their doctor's configured seat count", () => {
  const m = derive(
    snapshot({
      visits: [
        visit("VIS-01", "Checked In", "PAT-01"),
        visit("VIS-02", "Checked In", "PAT-02"),
        visit("VIS-03", "Checked In", "PAT-03"),
      ],
    })
  );
  assert.equal(m.actors.filter((a) => a.seated).length, 2);
  assert.equal(m.actors.filter((a) => !a.seated).length, 1);
});
test("earlier unclosed visits stay in the review list without appearing on today's seats", () => {
  const m = derive(
    snapshot({
      older_visits: [{ ...visit("VIS-OLD"), visit_date: "2026-10-22" }],
    })
  );
  assert.equal(m.stats.waiting, 0);
  assert.equal(m.actors.length, 0);
  assert.equal(m.activities[0].stage, "earlier");
});

test("hidden-name labels keep their readable patient identity as other visits leave", () => {
  const a = { ...visit("VIS-01"), patient: "HMS-PAT-2026-00028" },
    b = { ...visit("VIS-02"), patient: "HMS-PAT-2026-00029" };
  assert.equal(
    derive(snapshot({ visits: [a, b] })).activities[1].label,
    derive(snapshot({ visits: [b] })).activities[0].label
  );
});
