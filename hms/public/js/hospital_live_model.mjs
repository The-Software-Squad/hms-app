// Operational projection only. Coordinates are schematic; no physical tracking is inferred.
export const ROOMS_PER_PAGE = 6;
export const COLORS = {
  waiting: 0xdba34e,
  consultation: 0x369e89,
  diagnostics: 0x669bc7,
  pharmacy: 0x9a85c4,
  prescription: 0x8fac85,
  inpatient: 0xdb8b78,
  departure: 0x91a7a2,
};
export function roomPosition(index) {
  return { x: ((index % 3) - 1) * 11, z: Math.floor(index / 3) * 15 - 9 };
}
export function seatPosition(roomIndex, index, count) {
  const p = roomPosition(roomIndex),
    columns = Math.min(count, 6);
  return {
    x: p.x + ((index % columns) - (columns - 1) / 2) * 1.22,
    y: 0,
    z: p.z + 6 + Math.floor(index / columns) * 1.4,
  };
}
export function stageFor(status) {
  return (
    {
      "Checked In": "waiting",
      "Under Consultation": "consultation",
      "Lab/Diagnostics Pending": "diagnostics",
      "Lab/Diagnostics Completed": "waiting",
      "Prescription Given": "prescription",
    }[status] || null
  );
}
export function anonymousLabel(patient, fallback) {
  const match = String(patient || "").match(/^HMS-PAT-(\d{4}-\d+)$/);
  return match ? `Patient ${match[1]}` : fallback;
}
export function derive(snapshot, page = 0) {
  const allRooms = snapshot.rooms || [],
    rooms = allRooms.slice(page * ROOMS_PER_PAGE, (page + 1) * ROOMS_PER_PAGE);
  const roomIndex = new Map(rooms.map((r, i) => [r.id, i]));
  const models = new Map(
    allRooms.map((r) => [
      r.id,
      { ...r, waiting: [], current: [], other: [], scheduled: 0 },
    ])
  );
  const visits = [...(snapshot.visits || [])].sort(
    (a, b) =>
      String(a.creation).localeCompare(String(b.creation)) ||
      a.name.localeCompare(b.name)
  );
  const pharmacy = snapshot.pharmacy || [],
    salesByVisit = new Map();
  for (const sale of pharmacy) {
    if (!salesByVisit.has(sale.patient_visit))
      salesByVisit.set(sale.patient_visit, []);
    salesByVisit.get(sale.patient_visit).push(sale);
  }
  const admitted = new Map(
    (snapshot.admissions || []).map((a) => [a.patient, a])
  );
  const actors = [],
    activities = [],
    assignedPatients = new Set();
  let unmapped = 0,
    overflow = 0;
  const stats = {
    waiting: 0,
    consultation: 0,
    diagnostics: 0,
    pharmacy: pharmacy.length,
    inpatient: (snapshot.admissions || []).length,
    scheduled: (snapshot.appointments || []).length,
  };
  for (const a of snapshot.appointments || []) {
    const room = models.get(a.practitioner);
    if (room) room.scheduled++;
  }
  const rank = { consultation: 5, diagnostics: 4, waiting: 3, prescription: 2 };
  const primary = new Map();
  for (const v of visits) {
    const old = primary.get(v.patient);
    if (
      !old ||
      (rank[stageFor(v.status)] || 0) > (rank[stageFor(old.status)] || 0) ||
      ((rank[stageFor(v.status)] || 0) === (rank[stageFor(old.status)] || 0) &&
        String(v.modified) > String(old.modified))
    )
      primary.set(v.patient, v);
  }
  const labelByVisit = new Map(
    visits.map((v, i) => [
      v.name,
      anonymousLabel(v.patient, `Patient ${String(i + 1).padStart(2, "0")}`),
    ])
  );
  let diagnosticsIndex = 0,
    prescriptionIndex = 0;
  for (const visit of visits) {
    const stage = stageFor(visit.status);
    if (!stage) continue;
    const room = models.get(visit.doctor);
    if (stage === "waiting") {
      stats.waiting++;
      room?.waiting.push(visit);
    } else if (stage === "consultation") {
      stats.consultation++;
      room?.current.push(visit);
    } else {
      if (stage === "diagnostics") stats.diagnostics++;
      room?.other.push(visit);
    }
    const activity = {
      key: `visit:${visit.name}`,
      source_type: "Patient Visit",
      source_name: visit.name,
      patient: visit.patient,
      patient_label: visit.patient_label || "Patient",
      label: labelByVisit.get(visit.name),
      status: visit.status,
      stage,
      doctor: room?.doctor || "Room not configured",
      previous_day: visit.visit_date !== snapshot.date,
    };
    activities.push(activity);
    if (
      admitted.has(visit.patient) ||
      assignedPatients.has(visit.patient) ||
      primary.get(visit.patient)?.name !== visit.name
    )
      continue;
    let position;
    if (!roomIndex.has(visit.doctor)) {
      unmapped++;
      continue;
    }
    const ri = roomIndex.get(visit.doctor),
      rp = roomPosition(ri);
    if (stage === "waiting") {
      const index = room.waiting.length - 1;
      if (index < room.seats) position = seatPosition(ri, index, room.seats);
      else {
        overflow++;
        position = {
          x: rp.x + 4.4 + ((index - room.seats) % 2) * 0.8,
          y: 0,
          z: rp.z + 6 + Math.floor((index - room.seats) / 2) * 1.1,
        };
      }
    } else if (stage === "consultation")
      position = {
        x: rp.x + 1.1 + (room.current.length - 1) * 0.8,
        y: 0,
        z: rp.z + 0.1,
      };
    else if (stage === "diagnostics") {
      const index = diagnosticsIndex++;
      position = {
        x: -12 + (index % 5) * 1.1,
        y: 0,
        z: 25.4 + Math.floor(index / 5) * 1.1,
      };
    } else if (stage === "prescription" && salesByVisit.has(visit.name))
      continue;
    else {
      const index = prescriptionIndex++;
      position = {
        x: -2 + (index % 4) * 1.1,
        y: 0,
        z: 26 + Math.floor(index / 4) * 1.1,
      };
    }
    assignedPatients.add(visit.patient);
    actors.push({
      ...activity,
      key: `patient:${visit.patient}`,
      position,
      seated: stage === "waiting" && room.waiting.indexOf(visit) < room.seats,
      color: COLORS[stage] || COLORS.waiting,
    });
  }
  pharmacy.forEach((sale, i) => {
    const activity = {
      key: `sale:${sale.name}`,
      source_type: "Meds Out",
      source_name: sale.name,
      patient: sale.patient,
      patient_label: sale.patient_label,
      label: anonymousLabel(sale.patient, `Collection ${i + 1}`),
      status: sale.collection_status,
      stage: "pharmacy",
      doctor: "Pharmacy",
    };
    activities.push(activity);
    if (
      sale.patient &&
      (admitted.has(sale.patient) || assignedPatients.has(sale.patient))
    )
      return;
    if (sale.patient) assignedPatients.add(sale.patient);
    actors.push({
      ...activity,
      key: sale.patient ? `patient:${sale.patient}` : `sale:${sale.name}`,
      position: {
        x: 8 + (i % 5) * 1.05,
        y: 0,
        z: 25.3 + Math.floor(i / 5) * 1.15,
      },
      color: COLORS.pharmacy,
    });
  });
  const visibleBeds = (snapshot.beds || []).slice(0, 24),
    bedByName = new Map(
      visibleBeds.map((b, i) => [b.name, { ...b, index: i }])
    );
  (snapshot.admissions || []).forEach((a, i) => {
    const b = bedByName.get(a.bed);
    const activity = {
      key: `admission:${a.name}`,
      source_type: "IP Record",
      source_name: a.name,
      patient: a.patient,
      patient_label: a.patient_label,
      label: anonymousLabel(a.patient, `Inpatient ${i + 1}`),
      status: a.status,
      stage: "inpatient",
      doctor: b?.ward || "Inpatient care",
    };
    activities.push(activity);
    if (!b) return;
    actors.push({
      ...activity,
      key: `patient:${a.patient}`,
      position: bedPosition(b.index),
      color: COLORS.inpatient,
      lying: true,
    });
  });
  for (const [i, v] of (snapshot.older_visits || []).entries())
    activities.push({
      key: `older:${v.name}`,
      source_type: "Patient Visit",
      source_name: v.name,
      patient: v.patient,
      patient_label: v.patient_label,
      label: anonymousLabel(v.patient, `Earlier visit ${i + 1}`),
      status: `${v.status} · ${v.visit_date}`,
      stage: "earlier",
      doctor: models.get(v.doctor)?.doctor || "Earlier open visit",
      previous_day: true,
    });
  return {
    rooms: rooms.map((r) => models.get(r.id)),
    stats,
    actors,
    activities,
    overflow,
    unmapped,
    visibleBeds,
    hiddenBeds: Math.max(0, (snapshot.beds || []).length - 24),
    pages: Math.max(1, Math.ceil(allRooms.length / ROOMS_PER_PAGE)),
  };
}
export function bedPosition(index) {
  return {
    x: 22 + (index % 3) * 2.5,
    y: 0.6,
    z: -9 + Math.floor(index / 3) * 3.6,
  };
}
export function transitions(previous, next) {
  const before = new Map((previous?.actors || []).map((a) => [a.key, a]));
  const changes = [];
  for (const actor of next.actors) {
    const old = before.get(actor.key);
    if (
      previous &&
      (!old ||
        old.stage !== actor.stage ||
        old.source_name !== actor.source_name)
    )
      changes.push({
        actor,
        from: old?.position || { x: -5, y: 0, z: 31 },
        to: actor.position,
      });
    before.delete(actor.key);
  }
  if (previous)
    for (const actor of before.values())
      changes.push({
        actor,
        from: actor.position,
        to: { x: -5, y: 0, z: 33 },
        leaving: true,
      });
  return changes;
}
