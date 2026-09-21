# NEXT.JS UI AGENT RULES

## Design Language

* Use a professional, minimal **neo-brutalist** visual system. black & white theme .primarily .
* Preserve the core visual identity:

  * `2px solid` dark borders
  * `4px 4px 0` hard offset shadows
  * ~`5px` border radius
  * flat colors
  * bold typography
  * compact spacing
* The offset shadow is a **hard geometric layer**, not a soft elevation shadow.
* Avoid gradients, glassmorphism, excessive rounding, blur, glow, and soft/drop shadows unless explicitly requested.

## Code & Structure

* Stack: **Next.js + React**.
* Follow the existing folder structure strictly.
* Inspect existing components before creating new ones.
* Reuse existing components, utilities, styles, and dependencies.
* Do not create duplicate components or unnecessary abstractions.
* Modify only files relevant to the request.
* Keep the repository clean.
* No unnecessary files, dependencies, refactors, or generated artifacts.
* **No code comments** unless explicitly requested.

## Execution

* Ask for approval before executing modifying commands, installing packages, running scripts, builds, migrations, or destructive operations.
* Read-only inspection is allowed when necessary.
* If architecture or requirements are ambiguous, stop and ask instead of assuming.

## UI Interaction

Every meaningful interaction should have a polished visual response where appropriate:

* Hover
* Active/pressed
* Focus
* Click
* Scroll
* Open/close
* Enter/exit
* Loading
* Success/error states

Animations must feel **smooth, fast, intentional, and responsive**.

Prefer:

```css
transition: transform 160ms ease, opacity 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
```

Use `transform` and `opacity` for movement/visibility whenever possible.

For physical buttons:

```css
:hover {
  transform: translate(-1px, -1px);
}

:active {
  transform: translate(3px, 3px);
  box-shadow: 0 0 0;
}
```

Do not make animations slow, excessive, or distracting.

## Performance

Prioritize rendering performance.

* Prefer GPU-friendly `transform` and `opacity`.
* Avoid animating `width`, `height`, `top`, `left`, `margin`, or other layout-triggering properties when `transform` can achieve the same effect.
* Avoid expensive `filter`, `backdrop-filter`, large blurs, and continuous box-shadow animations.
* Avoid unnecessary re-renders.
* Keep React state localized.
* Use CSS animations/transitions for purely visual interactions instead of JavaScript state.
* Avoid scroll listeners when CSS/Intersection Observer can solve the requirement.
* Use passive event handling where appropriate.
* Do not add animation libraries unless existing project dependencies already provide one or the user explicitly approves it.
* Respect `prefers-reduced-motion`.

## Scroll Animations

* Keep scroll effects subtle and performant.
* Prefer CSS/Intersection Observer over continuously running JavaScript scroll handlers.
* Animate `transform` and `opacity`.
* Avoid layout shifts and heavy effects during scrolling.
* Never sacrifice scrolling responsiveness for visual effects.

## Animation Quality

* Default interaction duration: approximately **120–220ms**.
* Larger entrance/section animations: approximately **250–500ms**.
* Use appropriate easing such as `ease-out` for entrances and responsive interactions.
* Avoid unnecessary bouncing, excessive spring effects, or long delays.
* Animations should enhance hierarchy and feedback, never obstruct interaction.

## Responsive Design

* Mobile-first and responsive.
* Preserve the neo-brutalist identity across breakpoints.
* Prevent overflow and layout shifts.
* Maintain usable touch targets.

## Final Principle

**Inspect → Plan → Ask → Implement → Verify → Report briefly**

Build interfaces that are **clean, tactile, fast, responsive, and visually consistent**.

**Never sacrifice performance for animation. Never sacrifice the design language for convenience.**
