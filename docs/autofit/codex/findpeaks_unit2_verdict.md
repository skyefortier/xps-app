# Find Peaks UI unit 2 (commit 5dade0d) — Codex review verdicts

## Run A
```
128:        before = _box(pg)
132:        pg.mouse.move(start_x, start_y)
134:        pg.mouse.move(start_x + 220, start_y + 140, steps=8)
137:        assert abs(after["left"] - before["left"] - 220) < 3
138:        assert abs(after["top"] - before["top"] - 140) < 3
147:def test_drag_clamps_within_viewport_never_fully_offscreen(browser, server):
154:        pg.mouse.move(start_x, start_y)
156:        # drag far past the top-left corner, well off-screen
157:        pg.mouse.move(-5000, -5000, steps=5)
162:        assert b["right"] > 0 and b["left"] < vw       # not fully off-screen horizontally
163:        assert b["bottom"] > 0 and b["top"] < vh - 1   # header band stays reachable
165:        # drag far past the bottom-right corner too
168:        pg.mouse.move(hb2["x"] + 30, hb2["y"] + hb2["height"] / 2)
170:        pg.mouse.move(vw + 5000, vh + 5000, steps=5)
173:        assert b2["left"] < vw and b2["right"] > 0
174:        assert b2["top"] < vh
179:def test_close_button_does_not_start_a_drag_and_still_closes(browser, server):
183:        before = _box(pg)
184:        pg.click("#find-peaks-modal-box h3 button")   # the close (X) button
189:        is_dragging = pg.evaluate(
191:        assert is_dragging is False
196:def test_inner_controls_still_work_after_a_drag(browser, server):
202:        pg.mouse.move(hb["x"] + 30, hb["y"] + hb["height"] / 2)
204:        pg.mouse.move(hb["x"] + 120, hb["y"] + 60, steps=5)
207:        pg.select_option("#fp-material", "conductor")
210:        pg.select_option("#fp-method", "least_squares")
217:def test_modal_resets_to_centered_on_fresh_open(browser, server):
225:        pg.mouse.move(hb["x"] + 30, hb["y"] + hb["height"] / 2)
227:        pg.mouse.move(hb["x"] + 300, hb["y"] + 200, steps=5)
232:        pg.click("#find-peaks-modal-box h3 button")  # close
236:            "#find-peaks-modal-box", "el => el.style.position")

codex
1. **MINOR** — `tests/test_browser_find_peaks_drag.py:183-191`: the close-button test does not actually prove the close button failed to start a drag. `before = _box(pg)` is unused, and the assertions only check that the modal closed and `dragging` is false after mouseup. If the `button` blocking selector regressed, the bubbled mousedown could still set `position: fixed`/`left`/`top`, then click closes and mouseup clears `dragging`, so this test could pass while violating the claim.

2. **MINOR** — `templates/index.html:13116-13117`: `_fpIsDragBlockingTarget` covers current header controls correctly, including the close button at `templates/index.html:12746`, and it has the required `instanceof Element` guard. But the “any future header control” claim is broader than the selector: a future `<span onclick>`, `[role=button]`, `[tabindex]`, or `<label>` in the header would not be blocked and could initiate a drag.

No BLOCKER/MAJOR findings. The implementation is scoped to `#find-peaks-modal-box`, uses current dimensions with `RefCore.clampToViewport(..., 8)`, leaves never-dragged resize behavior flex-centered, resets before opening, and does not alter content/apply/close logic. I did not run pytest in the read-only sandbox.

VERDICT: GO
```

## Run B
```
 12213	    offX = e.clientX - r.left;
 12214	    offY = e.clientY - r.top;
 12215	    document.body.style.cursor = 'grabbing';
 12216	    document.body.style.userSelect = 'none';
 12217	    e.preventDefault();
 12218	  });
 12219	  document.addEventListener('mousemove', e => {
 12220	    if (!dragging) return;

 succeeded in 139ms:
5dade0d:templates/index.html:3476:    fresh.addEventListener('keydown', (e) => {
5dade0d:templates/index.html:3498:      } else if (e.key === 'Escape') {
5dade0d:templates/index.html:5237:document.addEventListener('keydown', function(e) {
5dade0d:templates/index.html:5245:  if (e.key === 'Escape') {
5dade0d:templates/index.html:10892:        ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();_refToggleElement(\'' + a + '\')}">×</button>' +
5dade0d:templates/index.html:10945:  document.addEventListener('keydown', _refChipEsc, true);
5dade0d:templates/index.html:10952:  document.removeEventListener('keydown', _refChipEsc, true);
5dade0d:templates/index.html:10963:  if (e.key === 'Escape') { const b = _refChipOpenBtn; _refCloseChipDropdown(); if (b) b.focus(); }
5dade0d:templates/index.html:11013:        'onclick="_refBlendedPick(this)" onkeydown="if(event.key===\'Enter\'){event.preventDefault();_refBlendedPick(this)}">' +
5dade0d:templates/index.html:11186:        ' onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();_refToggleElement(\'' + e.sym + '\')}"' : '') +
5dade0d:templates/index.html:11345:    'onkeydown="if(event.key===\'Escape\'){_refCloseSearch()}" ' +
5dade0d:templates/index.html:12565:document.getElementById('spec-combo-search').addEventListener('keydown', function(e) {
5dade0d:templates/index.html:12577:  } else if (e.key === 'Escape') {
5dade0d:templates/index.html:12637:      <input type="text" id="save-fname" placeholder="filename" onkeydown="if(event.key==='Enter')confirmSave()">
5dade0d:templates/index.html:12743:<div id="find-peaks-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
5dade0d:templates/index.html:12746:      <button class="btn btn-sm" onclick="closeFindPeaksModal()" style="float:right">&#x2715;</button>
5dade0d:templates/index.html:13097:  document.getElementById('find-peaks-overlay').classList.add('open');
5dade0d:templates/index.html:13100:function closeFindPeaksModal() {
5dade0d:templates/index.html:13101:  document.getElementById('find-peaks-overlay').classList.remove('open');
5dade0d:templates/index.html:13160:  const overlay = document.getElementById('find-peaks-overlay');
5dade0d:templates/index.html:13550:  closeFindPeaksModal();

codex
1. MINOR [tests/test_browser_find_peaks_drag.py:184] The close-button test does not prove the close button failed to start a drag. A buggy implementation could start drag on `mousedown`, clear `.dragging` on `mouseup`, then still close on `click`; this test would pass. Add an assertion that inline `style.position/left/top` stayed empty or unchanged after the button click.

2. MINOR [tests/test_browser_find_peaks_drag.py:207] The “inner controls still work” test uses `pg.select_option`, which is more programmatic than a real post-drag pointer interaction. It may not catch bugs like a lingering capture listener or pointer-event issue that eats clicks. A real click/focus interaction on a visible control would discriminate better.

No implementation blocker found: the diff is scoped to the expected files, modal drag wiring is Find-Peaks-only, clamp uses the shared `RefCore.clampToViewport(..., 8)`, reset runs before showing, and Unit 3 identifiers are not introduced by this commit.

VERDICT: GO
```
