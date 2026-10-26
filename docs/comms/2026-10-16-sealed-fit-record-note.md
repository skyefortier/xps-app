# Student note — fits are now recorded and checked; what you will see — HELD (the owner sends it)

Status: drafted 2026-10-16 with the deploy (`docs/deploy-log.md`). Numbers from the committed measurements:
χ² — `docs/findings/seal-1c/README.md` (202 committed fits); project size — the same file, "Larger saves";
LA speed — `docs/findings/seal-la/README.md`, "Speed"; the two sites — the same file, "Across the machines".

---

Subject: XPS Fitting Studio — your fits are now recorded and checked

Hi all,

This update changes what the app keeps when you fit, and what you see when you open a project again.

The short version: **every fit you run now carries a complete record of itself, and the app checks
that record whenever the fit is shown. Projects saved before this update open as before but are
marked "saved before sealed records" (or with their peaks only): press Run Fit before you report
numbers from them.**

What is new

- When you press Run Fit, the app keeps the server's own record of the fit: what you asked for,
  the data, and every number the server returned. Results, the chart, the exports and the saved
  project all read their numbers from that record.
- Whenever a fit is shown (after the fit, and when you reopen a project), the server recomputes the
  record from scratch and checks that it holds together. For a moment the fit says
  "confirming…"; once checked, the marker disappears — a fit with no marker is confirmed.

What the labels mean

- **No marker — confirmed.** The server recomputed this fit's record and it holds exactly.
- **"confirming…"** — the check has not come back yet (a second or two).
- **"unconfirmed: …"** — the fit is shown exactly as recorded, but the server could not check it
  exactly here, and the label says why. The usual reasons: the server could not be reached, or the
  fit was made on our other site (xps2) or by an older version ("made on a different platform;
  exact recheck not possible here — use Re-run this fit"). Nothing is wrong with the fit; use
  **Re-run this fit** (below) if you want it tested.
- **"no longer applies" / statistics shown as "—"** — you changed the model or its settings (a
  peak, a lock, a link, the background, the window, the charge correction) after the fit. The
  numbers belonged to the previous model. Press Run Fit.
- **"saved before sealed records"** — a fit from a project saved before this update. Its peaks and
  numbers are shown as they were saved, but the app cannot check them (those saves do not hold
  the record). **Press Run Fit** to fit it again in this version, as the label says. (The
  "Re-run this fit" button below is only for fits made in this version.)
- **Peaks only** — an older fit that could not be reconstructed at all opens with its peaks and no
  fit. Press Run Fit.

On our seven committed lab projects: all 121 older fits open as "saved before sealed records" (81)
or peaks only (40); after pressing Run Fit, every one is confirmed.

The "Re-run this fit" button

Under Results, beside every fit made in this version, **Re-run this fit** sends the fit's own
request back to the server, with the same random starts, and compares the new fit with the one you
have. It says either "reproduced within rounding" or "a different solution — this fit is not
unique", and reports the scattered starts on their own line. It never changes your fit: it is a
test, not a replacement. Use it when a fit reads "unconfirmed", or whenever you want to know
whether a decomposition is the only one the data give.

Numbers that change

- **χ² (not the reduced χ²ᵣ) is corrected by up to about 3 % on fits with links or locks.** The
  page used to rebuild χ² from χ²ᵣ assuming three free parameters per peak. That is wrong whenever
  peaks are linked, locked, held or have extra shape parameters: on our 202 committed fits it was
  off on 113, by a median of 1.0 % and at most 2.9 %. The page now shows the server's own χ².
  The reduced χ²ᵣ, the R-factor, RMSE, the component curves and the areas do not change.

Other things you may notice

- **Projects are larger** — about 2.7 times on our committed projects, because each fit now carries
  its full record (roughly 25–40 KB per fit, compressed).
- **LA(α,β,m) fits are a little slower** — about 20 % on our U 4f fits (median 1.3 s → 1.5 s); a few
  take up to about twice as long, more if m is locked at a large value. In exchange, an LA fit now
  recomputes to exactly the same numbers every time, so it can be confirmed (before, about one LA fit
  in three could not be).

What to do

- Older project: open it, press Run Fit on each spectrum, save it again.
- A fit that says "unconfirmed": nothing is wrong with it; press Re-run this fit if you want it tested.
- Before reporting any number: check the fit has no marker (confirmed), or press Run Fit.

Thanks — questions to me as usual.
