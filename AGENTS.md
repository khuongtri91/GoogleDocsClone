# React Best Practices (Vercel-Aligned)

## Goal

Write React code that is fast, scalable, and avoids common performance pitfalls such as request waterfalls, large bundles, and unnecessary client-side work.

---

## Priority Rules (Always Follow)

1. Avoid request waterfalls (use parallel fetching)
2. Minimize client-side JavaScript
3. Keep components small and simple
4. Use Material UI for components, Tailwind for layout

## Data Fetching & Performance

- Avoid request waterfalls — always parallelize independent async operations using `Promise.all`
- Fetch data as early as possible (prefer server over client)
- Do not fetch data inside deeply nested components if it can be lifted
- Co-locate data fetching with the component that needs it, but avoid duplication
- Cache and reuse data when possible

---

## Rendering Strategy

- Prefer **Server Components** over Client Components when possible
- Only use `"use client"` when interactivity is required
- Avoid unnecessary client-side state
- Keep components pure and predictable

---

## Bundle Size Optimization

- Minimize JavaScript sent to the client
- Use dynamic imports (`import()`) for heavy components
- Lazy load non-critical UI
- Avoid large third-party libraries unless necessary
- Tree-shake unused code

---

## State Management

- Keep state as local as possible
- Avoid global state unless truly needed
- Derive state instead of duplicating it
- Avoid unnecessary re-renders by structuring state properly

---

## Avoid Re-renders

- Do not recreate objects/functions unnecessarily inside components
- Use memoization (`useMemo`, `useCallback`) only when needed
- Avoid passing unstable props to child components
- Keep component trees shallow where possible

---

## Network & API

- Reduce number of network requests
- Batch requests when possible
- Use streaming or partial rendering if supported
- Handle loading and error states properly

---

## Component Design

- Keep components small and focused
- Separate UI from business logic when possible
- Reuse components instead of duplicating logic
- Prefer composition over inheritance

---

## Loading & UX

- Show meaningful loading states (not blank screens)
- Use skeletons instead of spinners when possible
- Avoid blocking the main thread
- Prioritize above-the-fold content

---

## Code Quality

- Write predictable and deterministic components
- Avoid side effects during render
- Keep logic testable and modular
- Use clear naming and structure

---

## Common Anti-Patterns to Avoid

- Fetching data sequentially when it can be parallel
- Overusing client components
- Putting everything in global state
- Large monolithic components
- Unnecessary abstraction
- Premature optimization without measuring

---

## Agent Instructions (Important)

When generating or refactoring code:

1. Always check for opportunities to:
   - reduce bundle size
   - eliminate request waterfalls
   - move logic to server components

2. Prefer performance and simplicity over cleverness

3. If unsure:
   - choose the approach with less client-side JavaScript
   - favor readability and maintainability

4. Explain trade-offs when making non-obvious decisions

---

## Summary

- Fetch early, in parallel
- Keep logic on the server when possible
- Send less JavaScript
- Keep components simple
- Avoid unnecessary re-renders

---

This document defines the default standard for all React code in this project.

## Styling & UI Framework Rules

### UI Components (Material UI)

- Use Material UI components for:
  - buttons, inputs, dialogs, modals
  - forms and complex UI elements

- Prefer MUI components over building custom ones
- Use MUI props (`sx`, `variant`, etc.) for component-level styling when appropriate

---

### Styling (Tailwind CSS)

- Use Tailwind CSS for:
  - layout (flex, grid)
  - spacing (margin, padding)
  - positioning
  - responsive design

- Prefer Tailwind over custom CSS files

- Avoid writing raw CSS unless absolutely necessary

---

### Rule of Separation (VERY IMPORTANT)

- Do NOT mix Tailwind and MUI styling on the same element unnecessarily
- Choose one primary styling method per element:
  - MUI component → use `sx` or theme
  - Plain HTML / layout → use Tailwind

---

### Avoid

- Inline styles unless dynamic and necessary
- Overriding MUI styles heavily with Tailwind
- Creating duplicate components that MUI already provides

---

### Preferred Pattern

Example:

- Use MUI:
  - `<Button />`, `<TextField />`, `<Dialog />`

- Use Tailwind:
  - layout containers
  - page structure
  - spacing and alignment

Example: Parallel Data Fetching
await Promise.all([fetchA(), fetchB()])

---

### Agent Instructions

When generating UI code:

1. Default to Material UI for components
2. Use Tailwind for layout and spacing
3. Keep styling consistent and minimal
4. Avoid conflicts between Tailwind and MUI styling systems

- DO NOT jump directly to implementation for non-trivial tasks
- MUST follow the workflow defined in WORKFLOW.md

## Development Workflow

Follow the workflow defined in:

→ ./WORKFLOW.md

This workflow is mandatory for all non-trivial tasks.

## Final Instruction

If a solution violates these rules, rewrite it to comply.
