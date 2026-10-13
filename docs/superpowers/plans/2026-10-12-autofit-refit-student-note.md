# Student note — Auto-Fit now refits after the charge shift (DRAFT, held; the owner sends it)

Subject: Auto-Fit C1s Graphite: a change to its numbers

Auto-Fit C1s Graphite now does one more step. It still fits your C 1s spectrum, finds the graphite
line and sets the charge correction from it. It then fits once more in the corrected energy frame,
with every peak centre held where the first fit put it, and shows you THAT fit. It takes about a
second longer, and while it runs the page waits (you can cancel it).

What this means for results you already have:

- The R-factor shown on many earlier Auto-Fits was overstated — about 16 % where the true value is
  about 2 % (on a third of the lab's C 1s spectra). The fit was fine; the number compared it with data
  points the charge correction had already moved. Values shown now are correct.
- The final fit can change the peak areas a little: on the lab's spectra, compared with the first fit
  of the same Auto-Fit, typically under one percentage point of the total and at most about four.
  χ²ᵣ can move either way, by up to about a third, because the fit is now made on exactly the points
  and background you see.
- If you run Auto-Fit again on a spectrum, its result can also differ from your earlier one for a
  reason that is not new: on a few spectra the first fit can land on a different solution from run to
  run. To check a result, press Run Fit after Auto-Fit: its "scattered starts" line under Results says
  whether other starting points reach the same solution. Compare with care.

If you reported numbers from an Auto-Fit, run it again on that spectrum and use the new values.
Nothing else about the app changes.
