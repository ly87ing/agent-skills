# Sources — Visuals Rules

Provenance for the **Sizing And Verifying Visuals** rules (and the tables-vs-diagrams
choice in Workflow step 3) of `SKILL.md`. W3C and Wikipedia quotes below were retrieved
via `web_fetch` on 2026-06-17; the Tufte items are book citations.

## Rule → source

### "Make content legibility the bar … use color only when it encodes meaning, not as ornament."

- **WCAG 2.2, SC 1.4.1 Use of Color (Level A).** Success Criterion: *"Color is not used
  as the only visual means of conveying information, indicating an action, prompting a
  response, or distinguishing a visual element."* Note: *"This should not in any way
  discourage the use of color … if it is complemented by other visual indication."*
  → Color is legitimate when it **encodes meaning and is not the sole channel**; it is
  not mere decoration.
  <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>
- **WCAG 2.2, SC 1.4.3 Contrast (Minimum) (Level AA).** Text needs a contrast ratio of
  ≥ 4.5:1 (≥ 3:1 for large-scale text). *Pure decoration* — defined as *"serving only an
  aesthetic purpose, providing no information, and having no functionality"* — is exempt.
  → Legibility/contrast is the bar; decorative styling is what gets relaxed, not content.
  <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>
- **Tufte, data-ink / chartjunk** (below): decoration is "non-data-ink," secondary to the data.

### "Match the visual to its information density — never spend a large diagram on a few facts."

- **Edward R. Tufte, _The Visual Display of Quantitative Information_ (Graphics Press, 1983)** —
  origin of **chartjunk** and the **data-ink ratio**. The canonical chartjunk example is a
  chart that *"uses a large area and much 'ink' (many symbols and lines) to show only five
  hard-to-read numbers."* That is exactly the failure this rule guards against.
  Tufte: *"The interior decoration of graphics generates a lot of ink that does not tell the
  viewer anything new … it is all non-data-ink or redundant data-ink, and it is often chartjunk."*
- Tufte's **data-ink ratio** principle — maximize the share of ink devoted to data, erase
  redundant non-data ink — backs "pick the most compact form that stays legible."
- Secondary (quotes/example verified here): Wikipedia, *Chartjunk* (redirected from
  *Data-ink ratio*). <https://en.wikipedia.org/wiki/Chartjunk>

### Workflow step 3 — "tables for dense or relational data; reserve diagrams for genuine process flows."

- **Tufte, _The Visual Display of Quantitative Information_.** Tufte advises that **tables
  serve small / precise datasets** well, while the special power of **graphics is in larger
  data and pattern**. → Use a table for a short, dense inventory; reserve a diagram for a
  real sequence or branching. (Principle from VDQI; specific page not re-verified online here.)

### "Auto-layout diagrams (e.g. Mermaid) render differently per tool … long or CJK-heavy labels can clip — prefer a table … render once to confirm."

- **Not from Tufte/WCAG — this is a tooling/engineering practice**, partly learned firsthand
  (a Mermaid dependency diagram whose CJK labels clipped under one rendering setup). Keep it
  attributed honestly as practice, not as a cited principle.
- Tangential support: WCAG 1.4.3 notes that "large scale" thresholds differ for **CJK fonts**
  ("font size that would yield equivalent size for Chinese, Japanese and Korean (CJK) fonts"),
  i.e. CJK text metrics are not interchangeable with Latin — consistent with CJK labels
  needing more width than Latin-based auto-layout may reserve.
  <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>

## Bibliography

- Edward R. Tufte. *The Visual Display of Quantitative Information.* Graphics Press,
  Cheshire, CT, 1983 (2nd ed. 2001). — chartjunk, data-ink ratio, tables vs graphics.
- Edward R. Tufte. *Envisioning Information.* Graphics Press, 1990. ISBN 978-1-930824-14-0.
- W3C. *Understanding WCAG 2.2 — SC 1.4.1 Use of Color.*
  <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>
- W3C. *Understanding WCAG 2.2 — SC 1.4.3 Contrast (Minimum).*
  <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>
- Wikipedia. *Chartjunk* (secondary source for the Tufte quotes/example above).
  <https://en.wikipedia.org/wiki/Chartjunk>
