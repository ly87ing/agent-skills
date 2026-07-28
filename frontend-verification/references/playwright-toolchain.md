# Playwright Toolchain Failures

Load this only when a Playwright check fails before it reaches the app because the runner, browser, download,
or media helper cannot start. A run that never launched a browser proves nothing about the UI, so establish
toolchain health before reading the failure as application evidence.

- **A browser directory is not an installed browser.** Playwright marks a finished install with an
  `INSTALLATION_COMPLETE` file inside the browser directory, and every `playwright install` reclaims any browser
  directory missing that marker (or unreferenced by a linked installation), logging `Removing unused browser at
  ...`. So an interrupted download leaves a directory that *looks* installed, fails at launch, and then silently
  disappears during the next install — which is easily misread as "the installer deleted my working browser."
  Check for the executable or the marker file, never for the directory.
- **Silence is not a hang — resist the urge to kill the install.** Playwright downloads each archive to
  `$TMPDIR/playwright-download-*/` and only populates the browser cache afterwards, so the cache stays near-empty
  for the whole download. Worse, when a download host is unreachable Playwright waits out a **30s per-host socket
  timeout with no output and no CPU** before retrying a fallback host (`cdn.playwright.dev` →
  `playwright.download.prss.microsoft.com`) — an install that is quietly recovering looks exactly like a dead one.
  Watch the growing zip in `$TMPDIR/playwright-download-*/`, and probe host reachability with `curl -I` on the
  URL in the log; do not infer "stuck" from a quiet log, an empty cache dir, or 0% CPU on Playwright's own
  processes (which cannot see work done by extraction or OS security scanning anyway).
- **Never kill an install mid-write — a truncated binary is worse than a missing one.** The file ends up present,
  correctly named, executable, and still identified as a valid Mach-O/ELF by `file`, so every existence check
  passes; but the kernel `SIGKILL`s it at exec (exit **137**, zero output), and a feature that shells out to it —
  video recording via `ffmpeg` — hangs indefinitely instead of failing. Compare the installed file's byte size
  against the copy inside the downloaded archive to confirm; an interrupted install is repaired by extracting the
  already-downloaded, `unzip -t`-verified archive over it, not by re-downloading.
- **Reaching for a mirror is usually the wrong move.** Playwright already retries its own fallback host, so a
  blocked primary can resolve itself if you wait. If you do set `PLAYWRIGHT_DOWNLOAD_HOST`, first check the mirror
  carries the layout your version fetches: recent Playwright pulls Chrome for Testing from
  `builds/cft/<version>/<platform>/chrome-<platform>.zip`, and a mirror lacking that path 404s *and* leaves the
  cache empty, turning a slow install into a broken one.
- **Fallback: drive a browser that is already installed** via `channel: 'chrome'` (also set `video: 'off'` when
  `ffmpeg` is missing, so a recording error cannot surface in place of the real failure). Keep the override
  *outside* the repo — a throwaway config that `require`s the committed one and spreads over `use` — so an
  emergency workaround never lands in version control.

**Never read an exit code through a pipe.** `cmd | tail` reports `tail`'s status, so a failed install or test
run happily prints `exit 0`. Redirect instead (`cmd > log 2>&1; echo "EXIT=$?" >> log`), and confirm success
from the artifact that proves it — the browser binary on disk, the suite's own result file — never from a
directory existing or a status line alone.
