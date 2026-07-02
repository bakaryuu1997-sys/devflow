# Browser Visual Validation Checklist

## Goal

Validate the UI visually in a real browser without adding a heavy browser automation dependency yet.

## Desktop checklist

Open:

```text
http://localhost:8000
```

Check:

- sidebar is visible and readable
- hero title does not overlap
- account card aligns correctly
- wizard steps are in order
- upload cards fit in the page
- result panels do not overflow horizontally
- traceability cards are readable
- readiness PASS/FAIL card is readable
- evidence cards are readable
- toast messages appear at bottom-right

## Mobile checklist

Use browser dev tools and test widths:

```text
390px
430px
768px
```

Check:

- sidebar stacks above content
- buttons do not overflow
- upload cards stack vertically
- result cards remain readable
- evidence toolbar stacks vertically
- mini metric grid does not break layout

## Suggested screenshots

Take screenshots for:

```text
01-home.png
02-artifact-scan.png
03-traceability.png
04-readiness.png
05-evidence.png
06-mobile-home.png
```

## Pass criteria

The UI is acceptable when:

```text
No horizontal scrolling
No overlapping text
All primary buttons visible
Flow order is understandable
Result cards readable on mobile and desktop
```
