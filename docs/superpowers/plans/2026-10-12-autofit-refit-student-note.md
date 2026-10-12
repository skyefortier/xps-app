# Student note — Auto-Fit now refits after the charge shift (DRAFT, held; the owner sends it)

Subject: Auto-Fit C1s Graphite: a change to its numbers

Auto-Fit C1s Graphite now does one more step. It still fits your C 1s spectrum, finds the graphite
line and sets the charge correction from it. It then fits once more in the corrected energy frame,
with every peak centre locked, and shows you THAT fit. It takes about a second longer.

What this means for results you already have:

- Peak areas from an earlier Auto-Fit may differ by a few percent of the total (typically under one
  percentage point; at most about four on the lab's own spectra). Centres do not change.
- The R-factor shown on many earlier Auto-Fits was overstated — about 16 % where the true value is
  about 2 %. The fit was fine; the number compared it with data points the charge correction had
  already moved. Values shown now are correct.
- χ²ᵣ can move a little either way, because the fit is now made on exactly the points and
  background you see.

If you reported numbers from an Auto-Fit, run Auto-Fit (or Run Fit) again on that spectrum and use
the new values. Nothing else about the app changes.
