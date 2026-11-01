# GSAP Recipes for Canonical Moves

Executable JavaScript snippets using GSAP 3 syntax.

## 01. Rise

```javascript
gsap.fromTo(".card", 
  { y: 40, opacity: 0 }, 
  { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }
);
```

## 02. Pop

```javascript
gsap.fromTo(".badge", 
  { scale: 0.6, opacity: 0 }, 
  { scale: 1, opacity: 1, duration: 0.45, ease: "back.out(2.5)" }
);
```

## 03. Count-up

```javascript
const counter = { val: 0 };
gsap.to(counter, {
  val: 500,
  duration: 1.8,
  ease: "power2.out",
  onUpdate: () => {
    document.querySelector(".stat-number").textContent = Math.round(counter.val).toLocaleString();
  }
});
```

## 04. Checklist Tick Stagger

```javascript
gsap.fromTo(".list-item", 
  { opacity: 0, x: -20 }, 
  { opacity: 1, x: 0, stagger: 0.35, duration: 0.4, ease: "power2.out" }
);
```
