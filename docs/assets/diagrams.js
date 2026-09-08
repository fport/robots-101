/* Local Mermaid bundle; render only diagram pages and follow the site's palette. */
(function () {
  "use strict";
  const libraryURL = new URL("vendor/mermaid-11.17.2.min.js", document.currentScript.src);

  function init() {
    const sources = [...document.querySelectorAll("pre.workshop-diagram")];
    if (!sources.length) return;
    const en = document.documentElement.lang.startsWith("en");
    const diagrams = sources.map(source => {
      const figure = document.createElement("figure");
      figure.className = "diagram";
      source.replaceWith(figure);
      figure.append(source); // Keep readable source until rendering succeeds.
      return {figure, source: source.textContent};
    });
    const library = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = libraryURL.href;
      script.onload = resolve;
      script.onerror = () => reject(new Error("Unable to load local Mermaid bundle"));
      document.head.append(script);
    });
    let requested = 0, running = false, nextId = 0;

    async function render() {
      requested++;
      if (running) return;
      running = true;
      try {
        await library;
        let generation;
        do {
          generation = requested;
          const dark = document.body.dataset.mdColorScheme === "slate";
          window.mermaid.initialize({
            startOnLoad: false,
            securityLevel: "strict",
            theme: "base",
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            flowchart: {htmlLabels: false, curve: "basis", useMaxWidth: false},
            themeVariables: {
              darkMode: dark,
              fontSize: "16px",
              primaryColor: dark ? "#202d10" : "#edffc2",
              primaryTextColor: dark ? "#edf4e4" : "#202817",
              primaryBorderColor: dark ? "#b6ff00" : "#426b00",
              secondaryColor: dark ? "#18210d" : "#f1f7e6",
              tertiaryColor: dark ? "#151d0d" : "#f5f9ed",
              lineColor: dark ? "#b6ff00" : "#426b00",
              textColor: dark ? "#edf4e4" : "#202817",
              edgeLabelBackground: dark ? "#10130c" : "#fafcf5",
              clusterBkg: dark ? "#151d0d" : "#f5f9ed",
              clusterBorder: dark ? "#6b853e" : "#849769",
            },
          });
          for (const {figure, source} of diagrams) {
            const {svg} = await window.mermaid.render(`workshop-flow-${nextId++}`, source);
            if (generation !== requested) break;
            const canvas = document.createElement("div");
            canvas.className = "diagram-canvas";
            canvas.tabIndex = 0;
            canvas.setAttribute("role", "region");
            canvas.setAttribute("aria-label", en ? "Diagram; scroll horizontally if needed" : "Şema; gerekirse yatay kaydır");
            canvas.innerHTML = svg;
            const drawing = canvas.querySelector("svg");
            drawing.setAttribute("role", "img");
            // Keep text at its designed size; wide diagrams scroll inside the page.
            drawing.style.width = `${drawing.viewBox.baseVal.width}px`;
            drawing.style.maxWidth = "none";
            drawing.style.height = "auto";
            const caption = document.createElement("figcaption");
            caption.className = "diagram-hint";
            caption.textContent = en
              ? "Follow the arrows. Wide diagrams can be scrolled horizontally."
              : "Okları izleyerek ilerle. Geniş şemaları yatay kaydırabilirsin.";
            figure.replaceChildren(canvas, caption);
            figure.dataset.diagramReady = "true";
            figure.dataset.diagramTheme = dark ? "slate" : "default";
          }
        } while (generation !== requested);
      } catch (error) {
        console.error("Diagram rendering failed", error);
        for (const {figure} of diagrams) {
          const note = document.createElement("p");
          note.className = "diagram-error";
          note.textContent = en ? "The diagram could not be rendered; its source is shown below."
            : "Şema çizilemedi; kaynak metni aşağıda gösteriliyor.";
          figure.prepend(note);
          figure.dataset.diagramReady = "error";
        }
      } finally {
        running = false;
      }
    }
    new MutationObserver(render).observe(document.body, {
      attributes: true, attributeFilter: ["data-md-color-scheme"],
    });
    render();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
