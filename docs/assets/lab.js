(function () {
  "use strict";
  function init() {
    const arm = document.querySelector("#kinematics-lab");
    if (arm && !arm.dataset.ready) {
      arm.dataset.ready = "true";
      const update = () => {
        const a = Number(arm.querySelector("#joint-a").value);
        const b = Number(arm.querySelector("#joint-b").value);
        const q1 = a * Math.PI / 180, q2 = b * Math.PI / 180;
        const elbow = [0.18 * Math.cos(q1), 0.18 * Math.sin(q1)];
        const tip = [elbow[0] + 0.14 * Math.cos(q1 + q2), elbow[1] + 0.14 * Math.sin(q1 + q2)];
        const screen = p => [240 + p[0] * 600, 245 - p[1] * 600];
        const e = screen(elbow), t = screen(tip);
        arm.querySelector("#arm-links").setAttribute("points", `240,245 ${e[0]},${e[1]} ${t[0]},${t[1]}`);
        arm.querySelector("#elbow-dot").setAttribute("cx", e[0]);
        arm.querySelector("#elbow-dot").setAttribute("cy", e[1]);
        arm.querySelector("#tip-dot").setAttribute("cx", t[0]);
        arm.querySelector("#tip-dot").setAttribute("cy", t[1]);
        arm.querySelector("#arm-result").textContent = `q₁ = ${a}° (${q1.toFixed(3)} rad) · q₂ = ${b}° (${q2.toFixed(3)} rad) | Uç: x = ${(tip[0]*100).toFixed(1)} cm, y = ${(tip[1]*100).toFixed(1)} cm`;
      };
      arm.querySelectorAll("input").forEach(el => el.addEventListener("input", update));
      update();
    }
    const planner = document.querySelector("#dataset-planner");
    if (planner && !planner.dataset.ready) {
      planner.dataset.ready = "true";
      const update = () => {
        const values = ["episodes", "seconds", "fps", "cameras"].map(id => Number(planner.querySelector(`#${id}`).value));
        const out = planner.querySelector("#dataset-result");
        if (values.some(n => !Number.isFinite(n) || n <= 0) || values[0] % 1 || values[3] % 1) {
          out.textContent = "Pozitif değerler gir; episode ve kamera sayısı tam sayı olmalı."; return;
        }
        const [episodes, seconds, fps, cameras] = values;
        const frames = episodes * seconds * fps;
        const bytes = frames * cameras * 640 * 480 * 3;
        out.textContent = `${Math.round(frames).toLocaleString("tr-TR")} zaman adımı · ${Math.round(frames*cameras).toLocaleString("tr-TR")} kamera karesi · ${(episodes*seconds/60).toFixed(1)} dk net gösterim · sıkıştırılmamış RGB ≈ ${(bytes/1e9).toFixed(2)} GB. MP4 boyutu codec ve sahneye bağlıdır; reset süreleri dahil değildir.`;
      };
      planner.querySelectorAll("input").forEach(el => el.addEventListener("input", update));
      update();
    }
    const chunk = document.querySelector("#chunk-lab");
    if (chunk && !chunk.dataset.ready) {
      chunk.dataset.ready = "true";
      const update = () => {
        const hz = Number(chunk.querySelector("#control-hz").value);
        const steps = Number(chunk.querySelector("#chunk-steps").value);
        const latency = Number(chunk.querySelector("#latency-ms").value);
        chunk.querySelector("#chunk-result").textContent = `Kontrol periyodu: ${(1000/hz).toFixed(1)} ms · yürütülen ${steps} eylem: ${(steps/hz).toFixed(2)} s · inference: ${latency} ms · ${latency > steps/hz*1000 ? "Inference bu yürütme penceresinden uzun; kuyruk boşalabilir." : "Pencere gecikmeden uzun; bu gerekli bir bütçe kontrolüdür, kesintisiz kontrol garantisi değildir."} Kamera, ağ ve işlem süreleri bu basit hesaba dahil değil.`;
      };
      chunk.querySelectorAll("input").forEach(el => el.addEventListener("input", update));
      update();
    }
    const progress = document.querySelector("#learning-progress");
    if (progress && !progress.dataset.ready) {
      progress.dataset.ready = "true";
      const key = "so101-atolye-progress-v1";
      let saved = {};
      try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (_) { /* local-only optional storage */ }
      if (!saved || typeof saved !== "object") saved = {};
      const boxes = [...progress.querySelectorAll("input[type=checkbox]")];
      const update = () => {
        const count = boxes.filter(b => b.checked).length;
        progress.querySelector("progress").value = count;
        progress.querySelector("#progress-summary").textContent = `${count} / ${boxes.length} durak tamamlandı`;
      };
      boxes.forEach(box => {
        box.checked = saved[box.id] === true;
        box.addEventListener("change", () => {
          saved[box.id] = box.checked;
          try { localStorage.setItem(key, JSON.stringify(saved)); } catch (_) { /* reading still works */ }
          update();
        });
      });
      progress.querySelector("button").addEventListener("click", () => {
        boxes.forEach(b => { b.checked = false; }); saved = {};
        try { localStorage.removeItem(key); } catch (_) { /* optional */ }
        update();
      });
      update();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
