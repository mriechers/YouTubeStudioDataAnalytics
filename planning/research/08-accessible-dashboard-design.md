# Accessibility & Inclusive Dashboard Design — Research Report

## Summary

WCAG 2.2 does not have chart-specific success criteria, but a cluster of existing criteria — covering contrast, text alternatives, keyboard operability, and non-text content — directly govern how data visualizations must behave. The emerging WCAG 3.0 draft introduces outcome-based guidelines that will more explicitly address complex visualizations. Color-blind safe palette work is mature and well-tooled (ColorBrewer, Viz Palette, Oklab-based schemes), but multi-platform comparisons involving YouTube red and TikTok pink/red require deliberate palette design since deuteranopia and protanopia affect roughly 8% of males. Among JavaScript chart libraries, Highcharts remains the gold standard for screen reader support; Recharts and Chart.js require significant manual ARIA work. Dashboard frameworks like Adobe React Spectrum and Radix UI provide accessible primitives that save substantial implementation effort.

---

## Key Findings

1. **No single WCAG criterion covers "charts" — it is a matrix of criteria.** Success criteria 1.1.1 (Non-text Content), 1.4.1 (Use of Color), 1.4.3/1.4.6 (Contrast), 1.4.11 (Non-text Contrast), 2.1.1 (Keyboard), 2.4.3 (Focus Order), and 4.1.2 (Name, Role, Value) all apply to interactive dashboards. A chart that passes only one of these while failing others is still non-compliant.

2. **1.1.1 is the most overlooked criterion for charts.** SVG-based charts must either have a text alternative (`<title>`, `aria-label`, or a linked data table) or be marked `aria-hidden="true"` with an adjacent accessible alternative. Most chart library defaults fail this out of the box.

3. **1.4.1 (Use of Color) is the primary color-blindness criterion.** It requires that color is not the *only* visual means of conveying information. For line charts comparing 4–6 series, this means using both color AND a secondary encoding: differing line dash patterns, data point markers (circle, square, triangle, diamond), or direct labeling.

4. **1.4.11 (Non-text Contrast, Level AA, new in WCAG 2.1) applies to chart elements.** UI components and graphical objects must achieve 3:1 contrast against adjacent colors. This affects axis lines, data point borders, and the boundaries of filled areas in area charts.

5. **YouTube red (#FF0000) and TikTok's brand colors create a specific deuteranopia/protanopia problem.** Red and green are indistinguishable for ~5–6% of users. A YouTube red vs. a Facebook blue is fine; YouTube red vs. an Instagram coral/orange is not. The solution is a palette built from hue-lightness combinations that diverge across the full color-blind simulation spectrum — not just normal vision and deuteranopia.

6. **Recharts (widely used in React apps) has no meaningful built-in ARIA support as of 2024.** Its SVG output has `role="img"` at the root but no `<title>` injection, and individual data series have no accessible names. This must be implemented manually via the `customized` prop system.

7. **Highcharts ships with a dedicated Accessibility Module** that generates a hidden data table, sonification support, keyboard traversal of data points, and configurable `aria-label` templates. It is the only widely-used library where a11y is first-class rather than bolted on.

8. **`prefers-reduced-motion` applies to animated chart entry transitions and sparkline animations.** The CSS media query must be respected; libraries like Framer Motion and CSS animation stacks make this straightforward, but many charting libraries animate by default and require explicit configuration to disable.

9. **Text summaries of charts improve comprehension for all users, not just screen reader users.** The "inverted pyramid" pattern (headline finding → supporting data → chart) is recommended by the UK Government Data Service, the US Data.gov team, and academic visualization research. The chart reinforces the finding; the text carries the core message.

10. **Focus management in filter-heavy dashboards is a distinct challenge.** When a user changes a filter and charts re-render, focus should remain predictable. A common failure is focus jumping to the top of the page or being lost entirely after a React re-render.

---

## Tools & Technologies

### Palette Tools

| Tool | URL | Notes |
|---|---|---|
| ColorBrewer 2.0 | colorbrewer2.org | The classic. Categorical, sequential, diverging schemes; built-in colorblind-safe filter. Max 12 categories but quality drops above 8. |
| Viz Palette | projects.susielu.com/viz-palette | Interactive; simulates deuteranopia, protanopia, tritanopia, achromatopsia simultaneously. Shows palette performance on sample charts. |
| Oklab/Oklch palette generation | oklch.com, bottosson.github.io/posts/oklab | Perceptually uniform color space that produces palettes with consistent perceived lightness across hues — the best foundation for new custom palettes. |
| Coolors color-blind checker | coolors.co | Quick simulation tool. Less rigorous than Viz Palette but fast for gut-checking. |
| Adobe Color | color.adobe.com | Has a color-blind safe mode that evaluates accessibility of a palette and suggests compliant alternatives. |
| Colorgorical | vrl.cs.brown.edu/color | Research tool: generates palettes maximized for perceptual discriminability (including simulated color blindness) for a specified number of categories. |

### Recommended Categorical Palette for 5 Platforms (YouTube, Instagram, TikTok, Facebook, X)

The problem: YouTube red, TikTok (red+cyan brand), and Instagram gradient overlap badly for red-green color blindness. A working strategy:

```
YouTube:   #0077BB  (blue — diverges from all reds)
Instagram: #EE7733  (orange — distinct from blue and teal)
TikTok:    #009988  (teal/cyan — distinct from orange and blue)
Facebook:  #AA3377  (magenta/purple — distinct from teal and orange)
X/Twitter: #BBBBBB  (neutral grey — or #333333 for dark mode)
```

This is based on the Paul Tol "Bright" color scheme, which is designed for color-blind safety across all common forms of CVD. Never use brand colors directly for a multi-platform comparison chart — use them only for single-platform branded elements (a YouTube icon, a "YouTube" label badge).

**Paul Tol's schemes** (personal.sron.nl/~pault/) are among the most rigorously tested color-blind safe palettes in data visualization research and are worth using as the foundation for any multi-category chart.

### JavaScript Chart Libraries — A11y Comparison

| Library | Screen Reader | Keyboard Nav | ARIA Support | A11y Doc Quality | License |
|---|---|---|---|---|---|
| **Highcharts** | Excellent (Accessibility Module) | Yes, per data point | Full | Comprehensive | Commercial (free for non-profit) |
| **Visa Chart Components** | Excellent (built-in) | Yes, per data point | Full | Good | Open source (MIT) |
| **Apache ECharts** | Partial (aria option since v5) | Limited | Basic title/desc | Minimal | Open source (Apache 2.0) |
| **Chart.js** | None by default | None by default | Manual only | Poor | Open source (MIT) |
| **Recharts** | None by default | None by default | Manual only | Poor | Open source (MIT) |
| **Victory** | Partial | Limited | Manual | Fair | Open source (MIT) |
| **Observable Plot** | None | None | Manual | Poor | Open source (ISC) |
| **Visx** (Airbnb) | None | None | Manual | Poor | Open source (MIT) |
| **Nivo** | None | None | Manual | Poor | Open source (MIT) |

**Note for this project**: If migrating from Recharts, **Visa Chart Components** (github.com/visa/visa-chart-components) is the most accessible open-source alternative that does not require a commercial license. It includes keyboard navigation to individual data points and screen reader descriptions by default — the same features Highcharts charges for. Highcharts offers free licensing for non-profit organizations, which PBS Wisconsin may qualify for.

**Highcharts Accessibility Module** features:
- Automatic data table generation (hidden but screen-reader accessible)
- Keyboard navigation between chart series, data points, axis labels
- Sonification (playing data as audio tones — experimental but impressive)
- Configurable description templates with `{point.x}`, `{point.y}` interpolation
- Focus indicator styling hooks

**Chart.js manual ARIA pattern:**
```html
<canvas
  role="img"
  aria-label="Line chart showing monthly views for 5 platforms January through December 2024"
>
  <p>Data table alternative: [hidden table or link to table below]</p>
</canvas>
```

**Recharts manual ARIA pattern:**
```jsx
<ResponsiveContainer>
  <LineChart
    aria-label="Monthly YouTube views, January–December 2024"
    role="img"
  >
    {/* Add hidden <title> via customized component */}
    <Customized
      component={() => <title>Monthly YouTube views, January–December 2024</title>}
    />
    ...
  </LineChart>
</ResponsiveContainer>
```

### Dashboard Frameworks with Strong A11y

| Framework | Key Strength | Notes |
|---|---|---|
| **Adobe React Spectrum** | ARIA patterns for every component, WAI-ARIA spec-compliant, tested with JAWS/NVDA/VoiceOver | The most comprehensive. Developed by Adobe's accessibility team. |
| **Radix UI** | Unstyled primitives with complete ARIA and keyboard patterns | Excellent for custom-styled dashboards. No opinions on visual design. |
| **Reach UI** | Similar to Radix; slightly smaller component set | Ryan Florence's library, solid but less actively developed since Remix matured. |
| **Chakra UI** | Good defaults; uses Radix under the hood for complex components | Easier to get started than raw Radix, slightly less control. |
| **Headless UI** (Tailwind Labs) | Small focused set (Menu, Dialog, Combobox, etc.) — all keyboard and ARIA compliant | Best for Tailwind-based projects. |

For a React dashboard like this project (using Tailwind + custom components), **Radix UI primitives** for interactive elements (dropdowns, date pickers, tabs, tooltips) combined with **Highcharts** for visualization is the highest-confidence accessible stack.

### Screen Reader Testing Tools

- **axe DevTools** (browser extension): Best automated coverage, catches ~30–40% of WCAG issues automatically
- **WAVE** (WebAIM): Visual overlay of accessibility issues; good for spotting missing alt text and contrast
- **Lighthouse** (Chrome DevTools): Accessibility audit built in; runs axe under the hood
- **NVDA** (Windows, free): Most common screen reader; test with Firefox
- **JAWS** (Windows, paid): Most common enterprise screen reader
- **VoiceOver** (macOS/iOS, built-in): Test with Safari on Mac; `Cmd+F5` to toggle
- **TalkBack** (Android, built-in): For mobile considerations

---

## Examples in the Wild

### 1. UK Government Data Service (ONS / data.gov.uk)
The Office for National Statistics produces accessible chart-embedded articles. Key patterns: every chart has a linked data download, chart titles are informative statements ("Inflation rose 4.2% in October 2023, the highest since 1992") not labels ("Figure 1"), and each chart section opens with a prose summary paragraph. Their chart components are open source at `github.com/ONSvisual`.

### 2. USA Facts (usafacts.org)
A nonprofit public data site that has been specifically called out for accessibility in data journalism circles. Uses accessible SVG charts with keyboard navigation, provides CSV downloads alongside every chart, and maintains contrast compliance. Built on D3 with custom ARIA overlays.

### 3. The Pudding
Not a traditional dashboard but consistently cited in data visualization accessibility discussions. Publishes scrollytelling visual essays with text-first narration — the visual is secondary to a prose narrative, which naturally creates the "text alternative" pattern.

### 4. U.S. Census Bureau Data Visualizations
census.gov embeds accessible charts that include title elements, description elements, and linked data tables. Published using accessible chart patterns that comply with Section 508 (the US federal accessibility law, which aligns with WCAG 2.1 AA).

### 5. Highcharts Demo Gallery
The Highcharts demo site itself demonstrates what fully accessible charts look like in practice: highcharts.com/demo. Enable the keyboard and navigate through a chart with Tab/Arrow keys to see the experience a screen reader user gets from a well-configured accessible chart.

---

## Code Patterns & Implementation Notes

### ARIA Pattern: Accessible Chart Wrapper (React/Recharts)

```tsx
// AccessibleChart.tsx
import { useId } from 'react';

interface AccessibleChartProps {
  title: string;
  description: string;
  children: React.ReactNode;
  dataTable?: React.ReactNode; // hidden but accessible table alternative
}

export function AccessibleChart({
  title,
  description,
  children,
  dataTable,
}: AccessibleChartProps) {
  const titleId = useId();
  const descId = useId();
  const tableId = useId();

  return (
    <div>
      <figure
        role="figure"
        aria-labelledby={titleId}
        aria-describedby={descId}
      >
        <figcaption id={titleId} className="sr-only">
          {title}
        </figcaption>
        <p id={descId} className="text-sm text-gray-600 mb-2">
          {description}
        </p>
        {children}
      </figure>

      {/* Visually hidden data table for screen readers */}
      {dataTable && (
        <details>
          <summary className="text-sm text-blue-600 underline cursor-pointer mt-2">
            View data table
          </summary>
          <div id={tableId}>{dataTable}</div>
        </details>
      )}
    </div>
  );
}
```

### Color Palette: Paul Tol Bright — CSS Custom Properties

```css
/* Paul Tol Bright scheme — color-blind safe for up to 7 categories */
:root {
  --color-cat-1: #4477AA;  /* blue */
  --color-cat-2: #EE6677;  /* red */
  --color-cat-3: #228833;  /* green */
  --color-cat-4: #CCBB44;  /* yellow */
  --color-cat-5: #66CCEE;  /* cyan */
  --color-cat-6: #AA3377;  /* purple */
  --color-cat-7: #BBBBBB;  /* grey */
}

/* Platform-specific mapping (bypasses brand colors) */
:root {
  --color-youtube:   var(--color-cat-1);   /* blue */
  --color-instagram: var(--color-cat-2);   /* red-adjacent but lightness-distinct */
  --color-tiktok:    var(--color-cat-5);   /* cyan */
  --color-facebook:  var(--color-cat-6);   /* purple */
  --color-twitter-x: var(--color-cat-7);   /* grey */
}
```

### prefers-reduced-motion: Recharts + Tailwind

```tsx
// In component
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Recharts: disable animations globally
<LineChart isAnimationActive={!prefersReducedMotion}>
  <Line
    isAnimationActive={!prefersReducedMotion}
    animationDuration={prefersReducedMotion ? 0 : 800}
    ...
  />
</LineChart>
```

```tsx
// Or via a React hook
import { useReducedMotion } from '@mantine/hooks'; // or build your own
// Returns boolean: true when user prefers reduced motion

function useReducedMotion() {
  const [prefersReduced, setPrefersReduced] = React.useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
  React.useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return prefersReduced;
}
```

### Automated Chart Alt Text Generation

Generating descriptive alt text for charts manually does not scale. Two approaches exist:

**1. Template-based generation (deterministic, recommended for production)**
Construct alt text from the data at render time. For a bar chart of platform views:
```ts
function generateChartAltText(data: PlatformViewData[]): string {
  const sorted = [...data].sort((a, b) => b.views - a.views);
  const top = sorted[0];
  const total = data.reduce((s, d) => s + d.views, 0);
  const topPct = Math.round((top.views / total) * 100);
  return (
    `Bar chart of video views by platform for ${data[0].period}. ` +
    `${top.platform} led with ${top.views.toLocaleString()} views (${topPct}% of total). ` +
    `Platforms shown: ${data.map(d => d.platform).join(', ')}.`
  );
}
```

**2. LLM-based generation (emerging, not production-ready for privacy-sensitive data)**
Tools like Datawrapper's "Describe your chart" feature and experimental integrations in Flourish use LLMs to generate plain-language chart descriptions. Not suitable for internal analytics dashboards with proprietary data, but worth tracking as the space matures.

**The Chartability standard** (chartability.fizz.studio) requires that alt text follow this structure:
1. Chart type and subject ("Bar chart comparing...")
2. Key finding or trend ("YouTube views grew 40%...")
3. Data range and context ("January through December 2024")
4. Offer to provide more detail ("A data table is available below")

### Keyboard Navigation: Dashboard Tab Order Pattern
  const announcerRef = React.useRef<HTMLDivElement>(null);

  function handleChange(value: string) {
    onChange(value);
    // Announce result to screen readers without moving focus
    if (announcerRef.current) {
      announcerRef.current.textContent = `Dashboard updated for ${value}`;
    }
  }

  return (
    <>
      {/* Live region: announces updates without focus move */}
      <div
        ref={announcerRef}
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />
      <select onChange={(e) => handleChange(e.target.value)}>
        ...
      </select>
    </>
  );
}
```

### Chart Title Pattern: Insight-First

```
Bad:  "Views by Platform, 2024"
Good: "YouTube drove 67% of total video views in Q4 2024"

Bad:  "Subscriber Growth"
Good: "Subscriber growth accelerated after Shorts launch in March"
```

This pattern (called "headline chart titles" or "assertive titles") ensures the key insight survives for users who cannot see or process the chart. It also improves comprehension for sighted users — multiple studies show that people understand and retain chart data better when the chart title states the finding.

### WCAG 2.2 Criterion Quick-Reference for Charts

| Criterion | Level | How it Applies to Charts |
|---|---|---|
| 1.1.1 Non-text Content | A | Every chart needs a text alternative (aria-label, title, linked table, or figcaption) |
| 1.3.1 Info and Relationships | A | Data relationships conveyed by layout must also be in markup (e.g., table headers) |
| 1.3.3 Sensory Characteristics | A | Don't say "see the chart on the left" — always provide context in text |
| 1.4.1 Use of Color | A | Color alone cannot encode data categories — must have secondary encoding |
| 1.4.3 Contrast (Minimum) | AA | Text in chart labels, axes, legends: 4.5:1 (small text) or 3:1 (large text) |
| 1.4.4 Resize Text | AA | Chart labels must remain legible at 200% browser zoom |
| 1.4.10 Reflow | AA | Charts must be usable at 320px viewport width without horizontal scrolling |
| 1.4.11 Non-text Contrast | AA | Chart elements (bars, lines, points) must meet 3:1 against adjacent colors |
| 2.1.1 Keyboard | A | All interactive chart features (tooltips, filters, drill-downs) must be keyboard accessible |
| 2.4.3 Focus Order | A | Tab order through dashboard widgets must be logical |
| 2.4.7 Focus Visible | AA | Focused chart elements must have a visible focus indicator |
| 2.5.3 Label in Name | A | Interactive chart elements' accessible names must contain their visible text |
| 4.1.2 Name, Role, Value | A | Custom chart components must expose correct ARIA role, state, and property |
| 4.1.3 Status Messages | AA | Filter changes, loading states, errors must be communicated to screen readers via aria-live |

### WCAG 3.0 Preview (Working Draft)

WCAG 3.0 moves from binary pass/fail to a scoring model (Bronze/Silver/Gold). For data visualization, the most relevant emerging guidance:

- **Visual Contrast** (replaces 1.4.3/1.4.11): Uses the APCA (Advanced Perceptual Contrast Algorithm) model, which better accounts for text size, font weight, and polarity (light-on-dark vs dark-on-light). APCA produces different numbers than the current WCAG contrast ratio formula — some things that pass WCAG 2 fail APCA and vice versa.
- **Structured Alternatives**: Explicit guidance on when data tables are required as alternatives to complex visualizations.
- **Cognitive Accessibility**: New guidelines around clear language, consistent navigation, and reducing cognitive load — directly applicable to dashboard information architecture.

WCAG 3.0 is not finalized; do not design exclusively for it, but APCA contrast checking (via the Accessible Perceptual Contrast Checker tool: apcacontrast.com) is worth running even today on critical UI text.

---

## Gotchas & Anti-Patterns

### 1. SVG `aria-hidden` Without an Alternative
The most common failure: a chart library renders an SVG and the developer adds `aria-hidden="true"` thinking this is "handled," without providing any adjacent accessible alternative. Screen reader users get nothing.

### 2. Tooltip-Only Data
Interactive tooltips that only appear on hover are inaccessible by definition. If a data point's value is only visible on hover/focus tooltip, the chart fails 2.1.1 (keyboard users can't trigger hover) and 1.1.1 (no text alternative for the encoded value). Solutions: always show values on the chart, or provide a data table.

### 3. Legends Without Labels
A legend that uses color swatches with no text label — or a label rendered inside the SVG as non-selectable text — creates failures for both color-blind users (1.4.1) and screen reader users (1.1.1).

### 4. Infinite-Scroll Dashboards Without Skip Links
Long dashboards with many chart sections need "skip to chart" or section navigation landmarks. Without them, keyboard users must Tab through every widget to reach a specific section.

### 5. Low-Contrast Gridlines and Axis Text
Gray axis labels and light gridlines are pervasive in "minimal" dashboard design. Common failure: axis label text at 1.5:1 or 2:1 contrast. They must meet 4.5:1 (normal text) or 3:1 (large text, which means 18pt/24px or 14pt/~18.6px bold).

### 6. Focus Traps in Modal/Overlay Charts
Clicking a chart to "expand" it in a modal that doesn't properly trap focus, or a modal that can't be dismissed with Escape, violates 2.1.2 (No Keyboard Trap) and frustrates keyboard users.

### 7. Animated Entry Transitions Without Reduced-Motion Support
Chart bars flying in, lines drawing themselves, number counters ticking up: all of these violate 2.3.3 (Animation from Interactions, WCAG 2.1 AAA) and can trigger vestibular disorders. For AA compliance there's no hard criterion, but failing to respect `prefers-reduced-motion` is an increasingly recognized accessibility failure and will likely be a Silver-level requirement in WCAG 3.0.

### 8. Using Brand Colors Directly in Multi-Platform Comparison Charts
YouTube red + TikTok red/pink are too similar under protanopia and deuteranopia. Never pull brand colors directly into a comparative series palette without running through a color-blind simulator first.

### 9. `<canvas>` Charts Without Accessible Alternatives
Canvas-based chart rendering (Chart.js defaults, some ECharts configs) produces a bitmap with no semantic information. The accessible pattern is: `<canvas role="img" aria-label="...">` with fallback content between the tags, plus a linked data table. SVG-based charts (Recharts, Highcharts, D3) are easier to make accessible because the DOM elements can carry ARIA attributes.

### 10. Conflating "Decorative" with "Informational" for Charts
Using `role="presentation"` or `aria-hidden` is correct for genuinely decorative SVG icons and illustrations. It is wrong for a chart that encodes data. The distinction is: does removing this element cause a user to lose information? If yes, it needs an accessible alternative.

---

## Sources & Further Reading

**WCAG Specifications**
- WCAG 2.2 Understanding Docs: https://www.w3.org/WAI/WCAG22/Understanding/
- WCAG 2.2 Quick Reference: https://www.w3.org/WAI/WCAG22/quickref/
- WCAG 2.1 Understanding 1.4.11 (Non-text Contrast): https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html
- WCAG 3.0 Working Draft: https://www.w3.org/TR/wcag-3.0/

**Data Visualization Accessibility**
- Highcharts Accessibility Module docs: https://www.highcharts.com/docs/accessibility/accessibility-module
- Frank Elavsky's "Chartability" workbook (rigorous a11y heuristics for data viz): https://chartability.fizz.studio/
- "Accessible data visualization" by Amy Cesal: https://www.amycesal.com/accessible-viz/
- Visa Chart Components (open source, accessible chart library from Visa): https://github.com/visa/visa-chart-components
- WAI tutorial on images (charts are "complex images"): https://www.w3.org/WAI/tutorials/images/complex/

**Color & Palette**
- Paul Tol's Notes on color schemes: https://personal.sron.nl/~pault/
- ColorBrewer 2.0: https://colorbrewer2.org/
- Viz Palette by Elijah Meeks & Susie Lu: https://projects.susielu.com/viz-palette/
- Bottosson's Oklab perceptual color space: https://bottosson.github.io/posts/oklab/
- Colorgorical (research-based palette generator): http://vrl.cs.brown.edu/color
- "How to use color in data visualization" (Datawrapper Academy, comprehensive): https://academy.datawrapper.de/article/140-what-to-consider-when-choosing-colors-for-data-visualization

**Component Libraries**
- Adobe React Spectrum accessibility: https://react-spectrum.adobe.com/react-spectrum/accessibility.html
- Radix UI accessibility overview: https://www.radix-ui.com/primitives/docs/overview/accessibility
- Headless UI: https://headlessui.com/

**Testing**
- axe DevTools: https://www.deque.com/axe/
- WAVE Web Accessibility Evaluator: https://wave.webaim.org/
- APCA Contrast Calculator: https://www.myndex.com/APCA/
- Contrast Grid (check multiple foreground/background combos at once): https://contrast-grid.eightshapes.com/

**Real-World Examples**
- ONS Chart Components (UK gov): https://github.com/ONSvisual
- Datawrapper Academy (best practices articles): https://academy.datawrapper.de/
- US Web Design System (USWDS) — data components: https://designsystem.digital.gov/

**Motion & Animation**
- MDN prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- "Designing Safer Web Animation For Motion Sensitivity" (A List Apart): https://alistapart.com/article/designing-safer-web-animation-for-motion-sensitivity/

---

## Recommended for The Library

1. **Chartability Workbook** — https://chartability.fizz.studio/
   Frank Elavsky's heuristic-based evaluation framework for data visualization accessibility. Covers 14 "POUR+S" principles applied specifically to charts. The most focused and rigorous a11y checklist that exists for visualization work. Scrape the full workbook and methodology notes.

2. **Paul Tol's Color Notes** — https://personal.sron.nl/~pault/
   The definitive researcher's guide to color-blind safe palettes. Includes the Bright, Muted, Vibrant, and High-Contrast schemes with CSS hex values and usage guidance. Short, dense, authoritative.

3. **Highcharts Accessibility Module Documentation** — https://www.highcharts.com/docs/accessibility/accessibility-module
   Even if the project uses Recharts, this is the clearest documentation of what a fully accessible chart looks like in practice. The feature list serves as a checklist for manual ARIA implementation in other libraries.

4. **WAI Complex Images Tutorial** — https://www.w3.org/WAI/tutorials/images/complex/
   The W3C's own guidance on providing text alternatives for complex images including charts, graphs, and diagrams. Authoritative, with worked examples of both `aria-describedby` and data table patterns.

5. **Datawrapper Academy: Color in Data Visualization** — https://academy.datawrapper.de/article/140-what-to-consider-when-choosing-colors-for-data-visualization
   Practical, tool-independent guide to color choices for charts. Covers categorical vs. sequential vs. diverging palettes, color-blind testing, and the specific traps of red-green and blue-yellow palettes. Datawrapper is used by major newsrooms and their accessibility standards are high.
