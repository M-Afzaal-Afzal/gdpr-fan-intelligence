# Pitch Script — Privacy-First Fan Intelligence

**Live demo URL: <https://fan-pulse-guard.vercel.app/>** — point judges here on slides 1, 5, and 8.

**Total: 3 minutes (180 s). 8 logical sections. Simple English. Hooky lines.**

> Style rules:
> - One idea per slide. Don't read the slide — say what's beside it.
> - Pause after every bold line. Let it land.
> - "→" means click / advance to next slide.
> - All times are speaking targets — leave ~10 s of buffer.
>
> **Deck variants:**
> - **HTML deck** (`pitch/index.html`) — 8 slides. Most animations run on Space / click.
> - **PowerPoint deck** (`pitch/Raumdeuter-Pitch.pptx`) — 18 slides total, 16
>   clicks across the same 8 logical sections. Multi-step sections are signalled
>   by a section badge in the top-right (e.g. `STAGE 03 / 05`, `STEP 02 / 04`).
>   Each click lands one beat of the script. Talk in sync with the clicks.
>
> **PPTX click budget per section:**
> - § 3 Insight — **2 clicks** ("Mask first." / "Analyze second.")
> - § 4 Pipeline — **5 clicks** (one stage lights up per click)
> - § 5 Live demo — **4 clicks** (Ready → Detect → Mask → Done)
> - § 7 Impact — **2 clicks** (stats / stakeholders)
> - All others — 1 click each

---

## Total time budget

| Slide | Title          | Target | Cumulative |
| ----- | -------------- | ------ | ---------- |
| 1     | Hook           | 15 s   | 0:15       |
| 2     | Problem        | 25 s   | 0:40       |
| 3     | Insight        | 15 s   | 0:55       |
| 4     | How it works   | 30 s   | 1:25       |
| 5     | Live demo      | 35 s   | 2:00       |
| 6     | The moat       | 25 s   | 2:25       |
| 7     | Impact         | 20 s   | 2:45       |
| 8     | Close          | 15 s   | 3:00       |

---

## Slide 1 — Hook · 15 s

**Action:** Walk on stage. Pause one second. Lock eyes with one judge.

> **"What if the AI you just shipped to read your fan messages…"**
>
> *(short pause)*
>
> **"…quietly forwarded their names, emails, and phone numbers straight to OpenAI?"**
>
> "That's not a bug. That's how most fan-message AI pipelines work today."
>
> "I'm \[your name]. Team Raumdeuter. In three minutes I'll show you the fix."

→ next slide

---

## Slide 2 — Problem · 25 s

**Action:** The €20M number animates on screen. Wait for it to land, then talk.

> "Football clubs are sitting on **millions** of fan messages — support tickets, emails, DMs, forum posts."
>
> "They all want AI to read them. **But fans don't talk in clean data.**"
>
> *(switch to a slightly faster tempo, like reading a real message)*
>
> "They write things like:
> *'Hi I'm Lukas Weber from München, my booking is BK-92811, the app charged me twice.'*"
>
> "Send **that** to GPT, and you just shipped personal data to a US server."
>
> **"GDPR's max fine? €20 million. Or 4 percent of global turnover."**
>
> "That's the wall every club hits before they ever go live."

→ next slide

---

## Slide 3 — Insight · 15 s

**HTML version:** Full slide already shows both lines. Let them land.

**PPTX version:** 2-slide build. You arrive on step 1 (only "Mask first." is on screen). After "Mask first." lands, click once to bring "Analyze second." up.

> *(arrive — only "Mask first." is visible)*
>
> "Our whole idea is **one line**."
>
> **"Mask first."**
>
> *(→ click — "Analyze second." appears in green)*
>
> **"Analyze second."**
>
> "Most teams treat privacy as a check **at the end**. We made it **step one**."
>
> "The LLM never even meets the raw text — so there's **nothing to leak**."

→ next slide

---

## Slide 4 — How it works · 30 s

**HTML version:** Click each stage in turn as you say its number.

**PPTX version:** 5-slide build. You arrive with **stage 1 already lit**.
Each "Next" click lights up the next card and the green progress dots above
fill in. The "What gets stored" footer appears only on the final click (5/5).

> *(arrive on stage 1/5 — Detect — already lit)*
>
> "Five stages. One Python boundary. Watch."
>
> **"One — Detect."** Four layers in parallel: regex, Presidio NER, German address rules, and football hard negatives — so 'Gate C' stays 'Gate C', not '\[CITY\_1]'.
>
> *(→ click — stage 2/5 lights up)*
> **"Two — Mask."** Every name, every email, every booking ID becomes a stable placeholder.
>
> *(→ click — stage 3/5 lights up)*
> **"Three — Safety Gate."** We re-scan the masked text. If **anything** leaks, the LLM is **never called**.
>
> *(→ click — stage 4/5 lights up)*
> **"Four — Analyze."** Only the masked version ever leaves the box.
>
> *(→ click — stage 5/5 lights up + storage footer appears)*
> **"Five — Validate."** The LLM's answer gets re-scanned **again** before storage.
>
> *(point at the blue footer)*
>
> "And the database? **No column for raw values. Ever.**"

→ next slide

---

## Slide 5 — Live demo · 35 s

**HTML version:** Press `Space` once — the demo animates in ~3 s. Talk over it.

**PPTX version:** Four sub-slides (5 → 8). Press "Next" four times. Each click
matches one beat in the script below.

The top-right of the slide has a pulsing "Try it on your phone · fan-pulse-guard.vercel.app" pill — point at it once at the start.

> *(slide 5 — Ready)* "Let me show you. **And — this is live right now at fan-pulse-guard.vercel.app — open it on your phone, follow along.**"
>
> "Here's a real bilingual fan complaint — name, city, email, phone, booking ID, all in one breath."
>
> *(→ click — slide 6 — PII highlights light up red on the left)*
>
> "Stage 1 — detect. The pipeline finds every piece of PII…"
>
> *(→ click — slide 7 — masked text streams in on the right)*
>
> "Stage 2 — mask. **Name… gone. City… gone. Email… gone.**"
>
> *(pause, then point at the screen)*
>
> "And look — '**Match Day 12**' is still there. '**Gate C**' is still there. That's the hard-negative layer. We **don't** mask things that **aren't** PII."
>
> *(→ click — slide 8 — "Done" status lands)*
>
> **"Five entities masked. Zero leaked. Under a second end-to-end."**
>
> "That's exactly what the LLM sees. Same meaning. Zero personal data."

→ next slide

---

## Slide 6 — The moat · 25 s

**Action:** The 4 moat cards are visible; the bottom ticker is cycling the 10 privacy rules. Don't read the ticker — let it run.

> "Why is this hard? Anyone can call an LLM. **Almost no one gets the masking layer right.**"
>
> **"Four detection layers"** — including football-specific hard negatives.
>
> **"Zero entity-value columns"** in the database — a full DB dump can't reconstruct one name.
>
> **"Two safety scans"** — input and output.
>
> *(point at the cycling rules)*
>
> "And **ten hard privacy rules** baked into the architecture. **77 of 77 tests** pass. Hostile prompts, prompt-injection, mixed English-German — **zero leakage**."

→ next slide

---

## Slide 7 — Impact · 20 s

**HTML version:** Full slide visible — three big numbers above, three stakeholders below.

**PPTX version:** 2-slide build. You arrive on step 1 (three big stats only). After the stats line, click once to reveal the stakeholder row.

> *(arrive — three big numbers: €20M → 0, < 1s, 72h)*
>
> "So what does this unlock?"
>
> **"GDPR exposure goes from twenty million euros down to zero."** At the architecture level — not added on at the end.
>
> "Latency: **under one second**."
>
> "Built in **72 hours**."
>
> *(→ click — three stakeholder cards appear)*
>
> "Fan Insights Managers, Support Leads, and Data teams all get the answers they were already paying for — **without ever touching a fan**."

→ next slide

---

## Slide 8 — Close · 15 s

**Action:** Stand still. Final line slow. There's a **scannable QR code** on this slide pointing to the live site — point at it once when you say "scan this".

> "One line to remember."
>
> *(slow, one beat between sentences)*
>
> **"Raw PII never reaches the LLM."**
>
> **"Never stored."**
>
> **"By design."**
>
> *(point at the QR)*
>
> "**Scan this** — it's already live. Try it on a real fan message of your own."
>
> "**Raumdeuter.** Thank you."

*(slight bow / smile / step back — wait for applause)*

---

## Stage rehearsal checklist

Before you walk on, run this once on the actual laptop you'll present from:

**If presenting the HTML deck:**

- [ ] Open `pitch/index.html` in Chrome / Safari / Firefox — they all work.
- [ ] Press **F** for fullscreen.
- [ ] Press **T** once to start the 3-minute timer the moment you start talking.
- [ ] Walk through with **→** keys end to end. The demo on slide 5 needs **Space** to fire.
- [ ] Backup PDF: press **P** in the deck to print → save as PDF.

**If presenting the PPTX deck:**

- [ ] Open `pitch/Raumdeuter-Pitch.pptx` in PowerPoint / Keynote / Google Slides — all render the same.
- [ ] Enter presenter mode (Cmd-Shift-Enter in Keynote, F5 in PowerPoint).
- [ ] The live-demo section is **4 slides** (5 → 8) — one click per masking stage. Practice the cadence: click, line, click, line.
- [ ] The 3-minute timer is a stage prop here (no built-in countdown) — use your phone / watch.

**Both versions:**

- [ ] Test on the projector resolution if possible.
- [ ] Have the **live site** open in a second tab at <https://fan-pulse-guard.vercel.app/> as backup — if anyone asks "is it real?", `cmd-tab`, show it.
- [ ] Confirm the live site loads on the venue WiFi (do this before you go on stage).

## In-deck keyboard shortcuts

| Key                  | What it does                            |
| -------------------- | --------------------------------------- |
| `→` / `Space` / click | Next slide (or run demo on slide 5)    |
| `←`                  | Previous slide                          |
| `Home` / `End`       | Jump to first / last                    |
| `T`                  | Start / pause 3-min countdown timer     |
| `S`                  | Show / hide speaker notes               |
| `F`                  | Toggle fullscreen                       |
| `P`                  | Print → PDF export                      |
| `R`                  | Reset live demo (only on slide 5)       |
| Click pipeline stage | Light up that stage (on slide 4)        |

## Tips during the pitch

1. **Stand sideways to the screen, not in front.** Judges are watching you and the deck, not your back.
2. **Click the stage on slide 4.** It's interactive — judges remember interaction.
3. **Mention the live URL twice.** On slide 5 ("open it on your phone"), and on slide 8 ("scan this"). It turns judges into users.
4. **Don't apologize** if the deck flickers — just say "and you can see it running live at fan-pulse-guard dot vercel dot app." Then move on.
5. **End with a hard stop.** No "uh, yeah, that's it." Just: "By design. Thank you."
