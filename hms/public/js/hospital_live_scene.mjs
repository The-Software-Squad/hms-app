import * as THREE from "../vendor/three/three.module.min.js";
import {
  roomPosition,
  seatPosition,
  bedPosition,
  transitions,
  COLORS,
} from "./hospital_live_model.mjs?v=20261029-2";

export class HospitalScene {
  constructor(host, { onSelect, onError }) {
    this.host = host;
    this.onSelect = onSelect;
    this.onError = onError;
    this.disposed = false;
    this.labels = [];
    this.actors = new Map();
    this.meshes = [];
    this.geometries = new Map();
    this.materials = new Map();
    this.active = true;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xeaf1ee);
    this.scene.fog = new THREE.Fog(0xeaf1ee, 90, 155);
    this.camera = new THREE.OrthographicCamera(-30, 30, 26, -26, 0.1, 250);
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: "low-power",
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.domElement.setAttribute(
      "aria-label",
      "Interactive 3D hospital schematic. Use the activity list for an accessible view of every record."
    );
    this.renderer.domElement.setAttribute("role", "img");
    this.renderer.domElement.addEventListener(
      "webglcontextlost",
      (this.contextLost = (e) => {
        e.preventDefault();
        this.onError(
          "3D rendering was interrupted. The activity list is still available."
        );
      })
    );
    host.appendChild(this.renderer.domElement);
    this.layer = document.createElement("div");
    this.layer.className = "hl-scene-labels";
    host.appendChild(this.layer);
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xa5bab0, 1.8));
    const sun = new THREE.DirectionalLight(0xffffff, 2.1);
    sun.position.set(-18, 45, 12);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    Object.assign(sun.shadow.camera, {
      left: -40,
      right: 40,
      top: 45,
      bottom: -40,
      near: 1,
      far: 110,
    });
    sun.shadow.bias = -0.001;
    this.scene.add(sun);
    this.world = new THREE.Group();
    this.scene.add(this.world);
    this.people = new THREE.Group();
    this.scene.add(this.people);
    this.target = new THREE.Vector3(5, 0, 8);
    this.yaw = -0.57;
    this.pitch = 0.88;
    this.zoom = 1;
    this.raycaster = new THREE.Raycaster();
    this.bindControls();
    this.observer = new ResizeObserver(() => this.resize());
    this.observer.observe(host);
    this.resize();
  }
  material(color) {
    if (!this.materials.has(color))
      this.materials.set(
        color,
        new THREE.MeshStandardMaterial({ color, roughness: 0.83, metalness: 0 })
      );
    return this.materials.get(color);
  }
  geometry(kind) {
    if (!this.geometries.has(kind))
      this.geometries.set(
        kind,
        kind === "box"
          ? new THREE.BoxGeometry(1, 1, 1)
          : kind === "sphere"
          ? new THREE.SphereGeometry(1, 12, 10)
          : kind === "cylinder"
          ? new THREE.CylinderGeometry(1, 1, 1, 12)
          : new THREE.ConeGeometry(1, 1, 9)
      );
    return this.geometries.get(kind);
  }
  part(parent, kind, color, x, y, z, sx, sy, sz) {
    const mesh = new THREE.Mesh(this.geometry(kind), this.material(color));
    mesh.position.set(x, y, z);
    mesh.scale.set(sx, sy, sz);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    parent.add(mesh);
    return mesh;
  }
  box(g, c, x, y, z, w, h, d) {
    return this.part(g, "box", c, x, y, z, w, h, d);
  }
  label(text, x, z, type = "zone", data = null) {
    const element = document.createElement(data ? "button" : "div");
    element.className = `hl-world-label hl-${type}-label`;
    element.textContent = text;
    const entry = {
      element,
      position: new THREE.Vector3(x, 2.8, z),
      data,
      type,
    };
    if (data) {
      element.type = "button";
      element.addEventListener("click", () => this.onSelect(entry.data));
    }
    this.layer.appendChild(element);
    this.labels.push(entry);
    return element;
  }
  chair(x, z, color = 0x83a9a0, rotation = 0) {
    const g = new THREE.Group();
    g.position.set(x, 0, z);
    g.rotation.y = rotation;
    this.world.add(g);
    this.box(g, color, 0, 0.52, 0, 0.8, 0.17, 0.74);
    this.box(g, color, 0, 0.98, -0.34, 0.8, 0.83, 0.13);
    for (const dx of [-0.29, 0.29])
      for (const dz of [-0.25, 0.25])
        this.box(g, 0x657f78, dx, 0.24, dz, 0.055, 0.47, 0.055);
    return g;
  }
  plant(x, z) {
    const g = new THREE.Group();
    g.position.set(x, 0, z);
    this.world.add(g);
    this.part(g, "cylinder", 0xd6c6a7, 0, 0.32, 0, 0.38, 0.64, 0.38);
    this.part(g, "sphere", 0x43846e, 0, 1.03, 0, 0.7, 0.74, 0.6);
    this.part(g, "sphere", 0x6a9b7f, 0.23, 1.38, 0.08, 0.36, 0.44, 0.36);
  }
  person(actor, color, doctor = false) {
    const group = new THREE.Group();
    group.userData.actor = actor;
    const seated = !!actor.seated;
    const skin = [0xc99472, 0x986b52, 0xd9ac86, 0x744e3b][
      Math.abs([...actor.key].reduce((s, c) => s + c.charCodeAt(0), 0)) % 4
    ];
    this.box(
      group,
      doctor ? 0xfafaf4 : color,
      0,
      seated ? 0.87 : 1.04,
      0,
      0.55,
      seated ? 0.55 : 0.7,
      0.32
    );
    this.part(
      group,
      "sphere",
      skin,
      0,
      seated ? 1.37 : 1.61,
      0,
      0.245,
      0.275,
      0.245
    );
    this.part(
      group,
      "sphere",
      0x3f423e,
      0,
      seated ? 1.53 : 1.77,
      -0.04,
      0.24,
      0.12,
      0.23
    );
    for (const side of [-1, 1]) {
      if (seated) {
        this.box(group, 0x415b61, side * 0.15, 0.58, 0.21, 0.19, 0.17, 0.58);
        this.box(group, 0x415b61, side * 0.15, 0.3, 0.48, 0.18, 0.45, 0.19);
        this.box(group, 0x36494d, side * 0.15, 0.065, 0.57, 0.21, 0.1, 0.36);
      } else {
        const leg = this.box(
          group,
          0x415b61,
          side * 0.15,
          0.34,
          0,
          0.18,
          0.69,
          0.22
        );
        leg.userData.leg = side;
        this.box(group, 0x36494d, side * 0.15, 0.045, 0.08, 0.21, 0.1, 0.4);
      }
      this.box(
        group,
        skin,
        side * 0.37,
        seated ? 0.84 : 1.03,
        0,
        0.16,
        seated ? 0.5 : 0.6,
        0.19
      );
    }
    if (doctor) {
      this.box(
        group,
        0x5b9a96,
        0,
        seated ? 0.94 : 1.12,
        0.17,
        0.13,
        0.36,
        0.025
      );
      this.box(
        group,
        0x2b756a,
        0.19,
        seated ? 1.02 : 1.2,
        0.18,
        0.09,
        0.13,
        0.025
      );
    }
    if (actor.lying) group.rotation.x = -Math.PI / 2;
    group.traverse((o) => {
      if (o.isMesh) o.userData.actor = actor;
    });
    this.people.add(group);
    return group;
  }
  build(model) {
    this.world.clear();
    for (const l of this.labels) l.element.remove();
    this.labels = [];
    const rows = Math.max(1, Math.ceil(model.rooms.length / 3)),
      maxZ = rows === 1 ? 17 : 32;
    this.serviceZ = maxZ - 6;
    this.target.set(5, 0, (maxZ - 11) / 2);
    this.extent = rows === 1 ? 25 : 31;
    this.box(this.world, 0xc4d2cb, 6, -0.55, 8, 53, 0.8, 55);
    this.box(this.world, 0xf6f7ef, 6, -0.1, 8, 52, 0.24, 54);
    // Floor joints, circulation strip and a stepped entry make the schematic legible.
    for (let x = -19; x < 32; x += 2)
      this.box(this.world, 0xe7ede5, x, 0.027, 8, 0.017, 0.012, 52);
    for (let z = -17; z < 35; z += 2)
      this.box(this.world, 0xe7ede5, 6, 0.027, z, 51, 0.012, 0.017);
    this.box(this.world, 0xd9e9df, 0, 0.045, 20, 38, 0.03, 2.8);
    this.box(this.world, 0xcbdad1, -5, -0.28, 35, 8, 0.25, 3);
    this.box(this.world, 0xdbe5dc, -5, -0.43, 36, 9, 0.18, 3);
    model.rooms.forEach((room, i) => {
      const p = roomPosition(i),
        busy = room.current.length > 0;
      this.box(
        this.world,
        busy ? 0xe0efe7 : 0xe5ece8,
        p.x,
        0.055,
        p.z,
        9.8,
        0.07,
        7
      );
      this.box(this.world, 0xffffff, p.x, 1.65, p.z - 3.5, 10, 3.3, 0.18);
      this.box(this.world, 0xf9fbf6, p.x - 5, 1.65, p.z, 0.18, 3.3, 7);
      this.box(this.world, 0x557f76, p.x, 3.36, p.z - 3.5, 10, 0.16, 0.28);
      this.box(
        this.world,
        0xd6e7e3,
        p.x + 2.9,
        1.9,
        p.z - 3.36,
        2.5,
        1.7,
        0.06
      );
      this.box(
        this.world,
        0xf2f9f4,
        p.x + 2.9,
        1.9,
        p.z - 3.28,
        2.25,
        1.48,
        0.05
      );
      this.box(
        this.world,
        0xc3ad88,
        p.x - 0.8,
        0.86,
        p.z + 0.3,
        3.2,
        0.2,
        1.35
      );
      for (const dx of [-2.1, 0.5])
        this.box(
          this.world,
          0xd8d5c4,
          p.x + dx,
          0.42,
          p.z + 0.3,
          0.15,
          0.8,
          1.05
        );
      this.box(
        this.world,
        0x355354,
        p.x - 1.1,
        1.25,
        p.z + 0.14,
        0.8,
        0.62,
        0.09
      );
      this.box(
        this.world,
        0x91b8ad,
        p.x - 1.1,
        1.26,
        p.z + 0.2,
        0.66,
        0.47,
        0.025
      );
      this.chair(p.x - 1, p.z - 1.25, 0x496e6a, 0);
      this.chair(p.x + 1.25, p.z + 1.3, 0xb7c9bf);
      this.box(this.world, 0xd2ded6, p.x - 3.9, 0.7, p.z - 2.65, 1.7, 1.4, 0.8);
      this.plant(p.x + 4, p.z - 2.7);
      this.box(
        this.world,
        0xe9e4d6,
        p.x,
        0.06,
        p.z + 7.5,
        9.8,
        0.05,
        Math.max(4, Math.ceil(room.seats / 6) * 1.4 + 1)
      );
      for (let s = 0; s < room.seats; s++) {
        const sp = seatPosition(i, s, room.seats);
        this.chair(sp.x, sp.z);
      }
      const text = `${room.room_name} · ${room.doctor}`;
      this.label(text, p.x, p.z - 3.7, "room", { kind: "room", room });
      this.label(
        `${room.waiting.length} waiting / ${room.seats} seats`,
        p.x,
        p.z + 10.3,
        "seats",
        { kind: "room", room }
      );
    });
    this.buildServices();
    model.visibleBeds.forEach((b, i) => {
      const p = bedPosition(i);
      this.box(
        this.world,
        b.current_admission ? 0xf4d8cb : 0xe1ebe4,
        p.x,
        0.12,
        p.z,
        2.15,
        0.16,
        3.15
      );
      this.box(this.world, 0x98afa7, p.x, 0.55, p.z, 1.2, 0.64, 2.4);
      this.box(this.world, 0xf9fbf2, p.x, 0.91, p.z, 1.14, 0.18, 2.3);
      this.box(this.world, 0xc0d6c9, p.x, 1.04, p.z + 0.33, 1.16, 0.12, 1.5);
      this.box(this.world, 0xffffff, p.x, 1.05, p.z - 0.77, 0.92, 0.19, 0.5);
      this.box(this.world, 0x8eaaa0, p.x, 1.28, p.z - 1.15, 1.28, 0.8, 0.09);
    });
    this.label(
      `Inpatient care · ${model.stats.inpatient} admitted`,
      24,
      -14,
      "zone",
      { kind: "zone", stage: "inpatient" }
    );
    this.label("RECEPTION / ENTRY", -5, 32, "zone", {
      kind: "zone",
      stage: "waiting",
    });
    this.box(this.world, 0xaebfac, -10, 0.65, 31, 6, 1.3, 1.2);
    this.box(this.world, 0xe0c9a5, -10, 1.4, 31, 6.2, 0.2, 1.4);
    this.plant(-17, 31);
    this.plant(17, 31);
    this.label("HOSPITAL LIVE", 5, -17, "sign");
    this.cameraUpdate();
  }
  buildServices() {
    for (const zone of [
      { x: -11, name: "DIAGNOSTICS", color: 0xaac8d9, stage: "diagnostics" },
      {
        x: 0,
        name: "FOLLOW-UP & EXIT",
        color: 0xb9c8ad,
        stage: "prescription",
      },
      { x: 11, name: "PHARMACY", color: 0xc4b6d5, stage: "pharmacy" },
    ]) {
      this.box(this.world, zone.color, zone.x, 0.07, 25.7, 9, 0.09, 7);
      this.box(this.world, 0xf7faf6, zone.x, 1.2, 22.1, 9, 2.4, 0.15);
      this.box(this.world, zone.color, zone.x, 2.45, 22.1, 9, 0.12, 0.23);
      this.box(this.world, 0xf9f9ed, zone.x, 0.72, 23.4, 5.5, 1.4, 1.1);
      this.box(this.world, zone.color, zone.x, 1.45, 23.4, 5.7, 0.15, 1.2);
      this.label(zone.name, zone.x, 21.4, "zone", {
        kind: "zone",
        stage: zone.stage,
      });
      if (zone.stage === "pharmacy")
        for (let col = -2; col <= 2; col++)
          for (let row = 0; row < 2; row++)
            this.box(
              this.world,
              [0x9dbdaa, 0xd8b474, 0xad9ebd][(col + row + 3) % 3],
              zone.x + col * 0.6,
              0.8 + row * 0.45,
              22.4,
              0.35,
              0.36,
              0.25
            );
    }
  }
  setModel(model, { animate = true, rebuild = false } = {}) {
    const old = this.model,
      changedLayout =
        rebuild ||
        !old ||
        old.rooms.map((r) => `${r.id}:${r.seats}:${r.room_name}`).join() !==
          model.rooms.map((r) => `${r.id}:${r.seats}:${r.room_name}`).join() ||
        JSON.stringify(old.visibleBeds) !== JSON.stringify(model.visibleBeds);
    if (changedLayout) this.build(model);
    const changes = animate && !changedLayout ? transitions(old, model) : [];
    const byKey = new Map(changes.map((c) => [c.actor.key, c]));
    const nextKeys = new Set();
    this.hiddenActors = Math.max(0, model.actors.length - 160);
    for (const actor of model.actors.slice(0, 160)) {
      nextKeys.add(actor.key);
      let entry = this.actors.get(actor.key);
      if (!entry) {
        entry = { mesh: this.person(actor, actor.color), actor };
        this.actors.set(actor.key, entry);
      }
      if (
        entry.actor.stage !== actor.stage ||
        !!entry.actor.lying !== !!actor.lying ||
        !!entry.actor.seated !== !!actor.seated
      ) {
        this.people.remove(entry.mesh);
        entry.mesh = this.person(actor, actor.color);
      }
      entry.actor = actor;
      entry.mesh.traverse((o) => {
        if (o.isMesh) o.userData.actor = actor;
      });
      const change = byKey.get(actor.key);
      entry.path = change ? this.path(change.from, change.to) : null;
      entry.start = performance.now();
      entry.duration = 2200;
      if (entry.path && (actor.seated || actor.lying)) {
        this.people.remove(entry.mesh);
        entry.mesh = this.person(
          { ...actor, seated: false, lying: false },
          actor.color
        );
        entry.mesh.traverse((o) => {
          if (o.isMesh) o.userData.actor = actor;
        });
        entry.restorePose = true;
      }
      if (!entry.path)
        entry.mesh.position.set(
          actor.position.x,
          actor.position.y,
          actor.position.z
        );
    }
    for (const [key, entry] of this.actors)
      if (!nextKeys.has(key)) {
        const change = byKey.get(key);
        if (change?.leaving) {
          entry.path = this.path(change.from, change.to);
          entry.start = performance.now();
          entry.duration = 2000;
          entry.leaving = true;
          if (entry.actor.seated || entry.actor.lying) {
            this.people.remove(entry.mesh);
            entry.mesh = this.person(
              { ...entry.actor, seated: false, lying: false },
              entry.actor.color
            );
          }
        } else {
          this.people.remove(entry.mesh);
          this.actors.delete(key);
        }
      }
    // Doctor avatars are inferred only from active consultation or today's reported availability.
    for (const mesh of [...this.people.children])
      if (mesh.userData.isDoctor) this.people.remove(mesh);
    model.rooms.forEach((r, i) => {
      if (r.current.length || r.availability === "Available") {
        const p = roomPosition(i),
          mesh = this.person(
            { key: `doctor:${r.id}`, kind: "room", room: r, seated: true },
            COLORS.consultation,
            true
          );
        mesh.position.set(p.x - 1, 0, p.z - 1.3);
        mesh.userData.isDoctor = true;
      }
    });
    for (const label of this.labels) {
      if (label.data?.kind === "room") {
        const room = model.rooms.find((r) => r.id === label.data.room.id);
        if (room) {
          label.data = { kind: "room", room };
          label.element.textContent =
            label.type === "seats"
              ? `${room.waiting.length} waiting / ${room.seats} seats`
              : `${room.room_name} · ${room.doctor}`;
        }
      }
      if (label.data?.stage === "inpatient")
        label.element.textContent = `Inpatient care · ${model.stats.inpatient} admitted`;
    }
    this.model = model;
    this.requestDraw();
  }
  path(from, to) {
    return [
      new THREE.Vector3(from.x, from.y, from.z),
      new THREE.Vector3(from.x, 0, from.z + 2),
      new THREE.Vector3(to.x, 0, to.z + 2),
      new THREE.Vector3(to.x, to.y, to.z),
    ];
  }
  draw(time = performance.now()) {
    this.frame = null;
    if (this.disposed || !this.active) return;
    let moving = false;
    for (const [key, e] of this.actors) {
      if (!e.path) continue;
      const raw = Math.min(1, (time - e.start) / e.duration),
        progress = raw * 3,
        seg = Math.min(2, Math.floor(progress)),
        t = progress - seg;
      e.mesh.position.lerpVectors(e.path[seg], e.path[seg + 1], Math.min(1, t));
      e.mesh.rotation.y = Math.atan2(
        e.path[seg + 1].x - e.path[seg].x,
        e.path[seg + 1].z - e.path[seg].z
      );
      e.mesh.traverse((o) => {
        if (o.userData.leg)
          o.rotation.x = Math.sin(raw * 30) * 0.23 * o.userData.leg;
      });
      if (raw === 1) {
        e.path = null;
        e.mesh.rotation.y = 0;
        e.mesh.traverse((o) => {
          if (o.userData.leg) o.rotation.x = 0;
        });
        if (e.restorePose && !e.leaving) {
          this.people.remove(e.mesh);
          e.mesh = this.person(e.actor, e.actor.color);
          e.mesh.position.set(
            e.actor.position.x,
            e.actor.position.y,
            e.actor.position.z
          );
          e.restorePose = false;
        }
        if (e.leaving) {
          this.people.remove(e.mesh);
          this.actors.delete(key);
        }
      } else moving = true;
    }
    this.renderer.render(this.scene, this.camera);
    const width = this.host.clientWidth,
      height = this.host.clientHeight;
    for (const l of this.labels) {
      const p = l.position.clone().project(this.camera);
      l.element.style.transform = `translate(-50%,-50%) translate(${
        ((p.x + 1) * width) / 2
      }px,${((1 - p.y) * height) / 2}px)`;
      l.element.hidden = p.z > 1 || p.z < -1;
    }
    if (moving) this.requestDraw();
  }
  requestDraw() {
    if (!this.frame && this.active && !this.disposed)
      this.frame = requestAnimationFrame((t) => this.draw(t));
  }
  resize() {
    const w = this.host.clientWidth,
      h = this.host.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h);
    this.aspect = w / h;
    this.cameraUpdate();
  }
  cameraUpdate() {
    const span = this.extent || 30;
    this.camera.left = -span * this.aspect;
    this.camera.right = span * this.aspect;
    this.camera.top = span;
    this.camera.bottom = -span;
    this.camera.zoom = this.zoom;
    this.camera.updateProjectionMatrix();
    this.camera.position
      .copy(this.target)
      .add(
        new THREE.Vector3(
          Math.sin(this.yaw) * Math.cos(this.pitch) * 90,
          Math.sin(this.pitch) * 90,
          Math.cos(this.yaw) * Math.cos(this.pitch) * 90
        )
      );
    this.camera.lookAt(this.target);
    this.requestDraw();
  }
  home() {
    this.yaw = -0.57;
    this.pitch = 0.88;
    this.zoom = 1;
    this.cameraUpdate();
  }
  zoomBy(value) {
    this.zoom = Math.max(0.55, Math.min(2.7, this.zoom * value));
    this.cameraUpdate();
  }
  top() {
    this.pitch = 1.48;
    this.yaw = 0;
    this.cameraUpdate();
  }
  bindControls() {
    const canvas = this.renderer.domElement;
    canvas.style.touchAction = "none";
    canvas.addEventListener(
      "pointerdown",
      (this.down = (e) => {
        this.pointer = {
          x: e.clientX,
          y: e.clientY,
          startX: e.clientX,
          startY: e.clientY,
          pan: e.shiftKey || e.button === 2,
        };
        canvas.setPointerCapture(e.pointerId);
      })
    );
    canvas.addEventListener(
      "pointermove",
      (this.move = (e) => {
        if (!this.pointer) return;
        const dx = e.clientX - this.pointer.x,
          dy = e.clientY - this.pointer.y;
        if (this.pointer.pan) {
          this.target.x -= (dx * 0.055) / this.zoom;
          this.target.z -= (dy * 0.055) / this.zoom;
        } else {
          this.yaw -= dx * 0.006;
          this.pitch = Math.max(0.3, Math.min(1.48, this.pitch + dy * 0.004));
        }
        this.pointer.x = e.clientX;
        this.pointer.y = e.clientY;
        this.cameraUpdate();
      })
    );
    canvas.addEventListener(
      "pointerup",
      (this.up = (e) => {
        if (
          this.pointer &&
          Math.hypot(
            e.clientX - this.pointer.startX,
            e.clientY - this.pointer.startY
          ) < 5
        ) {
          const rect = canvas.getBoundingClientRect();
          this.raycaster.setFromCamera(
            new THREE.Vector2(
              ((e.clientX - rect.left) / rect.width) * 2 - 1,
              (-(e.clientY - rect.top) / rect.height) * 2 + 1
            ),
            this.camera
          );
          const hit = this.raycaster
            .intersectObjects(this.people.children, true)
            .find((h) => h.object.userData.actor);
          if (hit) this.onSelect(hit.object.userData.actor);
        }
        this.pointer = null;
      })
    );
    canvas.addEventListener(
      "wheel",
      (this.wheel = (e) => {
        e.preventDefault();
        this.zoomBy(e.deltaY > 0 ? 0.93 : 1.07);
      }),
      { passive: false }
    );
    canvas.addEventListener(
      "contextmenu",
      (this.menu = (e) => e.preventDefault())
    );
  }
  setActive(active) {
    this.active = active;
    if (!active && this.frame) {
      cancelAnimationFrame(this.frame);
      this.frame = null;
    }
    if (active) this.requestDraw();
  }
  dispose() {
    this.disposed = true;
    this.observer.disconnect();
    if (this.frame) cancelAnimationFrame(this.frame);
    for (const geometry of this.geometries.values()) geometry.dispose();
    for (const material of this.materials.values()) material.dispose();
    this.renderer.dispose();
    this.renderer.domElement.remove();
    this.layer.remove();
  }
}
