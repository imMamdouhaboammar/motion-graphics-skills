const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const text = button.dataset.copy;
    const state = button.querySelector(".copy-state");
    const originalText = button.textContent;

    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }

    if (state) {
      state.textContent = "Copied";
      window.setTimeout(() => {
        state.textContent = button.classList.contains("install-command") ? "Copy command" : "Copy";
      }, 1800);
    } else {
      button.textContent = "Copied ✓";
      window.setTimeout(() => {
        button.textContent = originalText;
      }, 1800);
    }
  });
});

document.querySelectorAll(".video-load").forEach((button) => {
  button.addEventListener("click", () => {
    const shell = button.closest(".video-shell");
    const video = shell.querySelector("video");

    shell.classList.add("is-playing");

    if (!video.src) {
      video.src = video.dataset.src;
      video.load();
    }

    button.style.display = "none";
    video.play().catch(() => {});
  });
});

if (!reducedMotion && window.gsap) {
  gsap.registerPlugin(ScrollTrigger);

  const intro = gsap.timeline({ defaults: { ease: "power4.out" } });
  intro
    .from(".hero-eyebrow", { y: 20, opacity: 0, duration: 0.7 })
    .from(".hero h1", { y: 54, opacity: 0, duration: 1.05 }, "-=0.45")
    .from(".hero-lede", { y: 24, opacity: 0, duration: 0.78 }, "-=0.62")
    .from(".hero-actions", { y: 18, opacity: 0, duration: 0.68 }, "-=0.48")
    .from(".hero-stage", { y: 44, rotate: -1.4, opacity: 0, duration: 1.05 }, "-=0.82")
    .from(".director-cameo", { y: 14, opacity: 0, duration: 0.5 }, "-=0.38");

  const playheadTween = gsap.to(".playhead", {
    x: () => {
      const timeline = document.querySelector(".timeline");
      return timeline ? timeline.clientWidth * 0.72 : 0;
    },
    duration: 5.4,
    ease: "none",
    repeat: -1,
    yoyo: true,
    invalidateOnRefresh: true
  });

  const words = [".word-a", ".word-b", ".word-c", ".word-d"];
  const wordLoop = gsap.timeline({ repeat: -1, repeatDelay: 0.35 });

  words.forEach((selector, index) => {
    if (index === 0) {
      wordLoop.to(selector, { yPercent: -112, duration: 0.7, ease: "power3.inOut" }, 1.2);
    } else {
      const start = index * 1.65 - 0.45;
      wordLoop.fromTo(
        selector,
        { yPercent: 112 },
        { yPercent: 0, duration: 0.7, ease: "power3.inOut" },
        start
      );
      if (index < words.length - 1) {
        wordLoop.to(
          selector,
          { yPercent: -112, duration: 0.7, ease: "power3.inOut" },
          start + 1.2
        );
      }
    }
  });

  wordLoop.to(".word-d", { yPercent: -112, duration: 0.7, ease: "power3.inOut" }, 5.7);
  wordLoop.set(".word-a", { yPercent: 112 }, 5.75);
  wordLoop.to(".word-a", { yPercent: 0, duration: 0.7, ease: "power3.inOut" }, 5.78);

  gsap.to(".flow-line span", {
    scaleY: 1,
    ease: "none",
    scrollTrigger: {
      trigger: "#storyFlow",
      start: "top 72%",
      end: "bottom 42%",
      scrub: 0.45
    }
  });

  gsap.utils.toArray(".flow-step").forEach((step) => {
    gsap.from(step, {
      y: 22,
      opacity: 0.34,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: {
        trigger: step,
        start: "top 83%",
        once: true
      }
    });
  });

  const orbitTween = gsap.to(".core-orbit", {
    rotate: 360,
    duration: 14,
    ease: "none",
    repeat: -1
  });

  gsap.from(".proof-wide", {
    y: 38,
    opacity: 0.3,
    rotate: -1.2,
    duration: 0.9,
    ease: "power4.out",
    scrollTrigger: {
      trigger: ".proof-layout",
      start: "top 76%",
      once: true
    }
  });

  gsap.from(".proof-tall", {
    y: 64,
    opacity: 0.25,
    rotate: 1.6,
    duration: 1.0,
    delay: 0.1,
    ease: "power4.out",
    scrollTrigger: {
      trigger: ".proof-layout",
      start: "top 76%",
      once: true
    }
  });

  const antiTween = gsap.to(".anti-lines span", {
    y: (index) => (index % 2 === 0 ? -5 : 5),
    duration: 2.6,
    repeat: -1,
    yoyo: true,
    stagger: 0.12,
    ease: "sine.inOut"
  });

  const ambientGroups = [
    { element: document.querySelector(".hero"), animations: [playheadTween, wordLoop] },
    { element: document.querySelector(".system"), animations: [orbitTween] },
    { element: document.querySelector(".anti"), animations: [antiTween] }
  ];

  const ambientObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const group = ambientGroups.find((item) => item.element === entry.target);
      if (!group) return;
      group.animations.forEach((animation) => entry.isIntersecting ? animation.play() : animation.pause());
    });
  }, { threshold: 0.05 });

  ambientGroups.forEach((group) => {
    if (group.element) ambientObserver.observe(group.element);
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      ambientGroups.forEach((group) => group.animations.forEach((animation) => animation.pause()));
    } else {
      ambientGroups.forEach((group) => {
        if (!group.element) return;
        const rect = group.element.getBoundingClientRect();
        const visible = rect.bottom > 0 && rect.top < window.innerHeight;
        if (visible) group.animations.forEach((animation) => animation.play());
      });
    }
  });
}

const pageVisible = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) {
      const video = entry.target;
      if (!video.paused) video.pause();
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll("video").forEach((video) => pageVisible.observe(video));

/* Director Cameo Wisdom Tips */
const directorTips = [
  "Geometry is measured, taste is reviewed.",
  "Arabic dots are part of the letter — never clip the dot zone.",
  "Never crossfade two saturated fields: cut or carry an object.",
  "The first frame waits for everything it paints.",
  "No card soup. One dominant visual subject per beat.",
  "Plan the end hold in the beat map before rendering."
];

let currentTipIndex = 0;
const tipText = document.getElementById("cameoTipText");
const tipCounter = document.getElementById("cameoTipCounter");
const nextBtn = document.getElementById("cameoNextBtn");

function showTip(index) {
  if (!tipText) return;
  currentTipIndex = (index + directorTips.length) % directorTips.length;
  tipText.textContent = `"${directorTips[currentTipIndex]}"`;
  if (tipCounter) {
    tipCounter.textContent = `${currentTipIndex + 1} / ${directorTips.length}`;
  }
}

if (nextBtn) {
  nextBtn.addEventListener("click", (e) => {
    e.preventDefault();
    showTip(currentTipIndex + 1);
  });
}

if (!reducedMotion) {
  window.setInterval(() => {
    showTip(currentTipIndex + 1);
  }, 7500);
}

/* Guide Tab Switching */
const guideTabs = document.querySelectorAll(".guide-tab");
const guidePanels = document.querySelectorAll(".guide-panel");

function activateGuideTab(targetId) {
  guideTabs.forEach((tab) => {
    const isTarget = tab.getAttribute("aria-controls") === targetId;
    tab.classList.toggle("is-active", isTarget);
    tab.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  guidePanels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === targetId);
  });
}

guideTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const targetId = tab.getAttribute("aria-controls");
    activateGuideTab(targetId);
  });
});

const cameoRobotLink = document.getElementById("cameoRobotLink");
if (cameoRobotLink) {
  cameoRobotLink.addEventListener("click", (e) => {
    e.preventDefault();
    activateGuideTab("tab-fleet");
    const guideSection = document.getElementById("guide");
    if (guideSection) {
      guideSection.scrollIntoView({ behavior: "smooth" });
    }
  });
}
