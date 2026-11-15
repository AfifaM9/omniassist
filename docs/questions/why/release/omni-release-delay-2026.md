# Why are Omni's releases delayed to 2027?

**Short answer:** Omni (this repository, the OmniAssist CLI) will hold its next release until
**v2027.1 in 2027**. Its sister project, [OmniAssist GUI](https://github.com/AfifaM9/omniassist-gui)
(nickname **GUI Omni**), continues to receive updates on its normal cadence in the meantime.

## What this means

| Project | Repository | Release status |
| :--- | :--- | :--- |
| **Omni** (OmniAssist CLI) | [AfifaM9/omniassist](https://github.com/AfifaM9/omniassist) | Paused. Next release is **v2027.1** in 2027. |
| **GUI Omni** (OmniAssist GUI) | [AfifaM9/omniassist-gui](https://github.com/AfifaM9/omniassist-gui) | Active. Continues to receive updates. |

The most recent release of Omni is **v2026.7 "Eton Mass"** (2026-10-21). No further 2026
release is planned; the version line resumes at **v2027.1**.

## Why

The delay is not technical. It comes down to maintainer capacity:

- **The CLI is not currently being actively maintained.** The project owner's attention is on
  GUI Omni, and CLI release work is not happening on a regular cadence.
- **No one has stepped up to take it on.** Release duties have not been picked up by anyone
  else, and the people who would like to help do not currently have the time.

Rather than publish a release that nobody has had the time to prepare and test, the next
release is deferred to **v2027.1**, with the expectation that maintainer capacity returns
by then.

## What is unaffected

- **GUI Omni keeps shipping.** The delay applies to Omni only. OmniAssist GUI continues to
  receive updates on its usual schedule.
- **The existing Omni release still works.** v2026.7 "Eton Mass" remains available and
  installable; nothing is withdrawn.
- **This repository stays open.** Issues and pull requests are still welcome; changes are
  simply not cut into a release until v2027.1.

## How to help

If you would like the CLI to move again before v2027.1, the most useful thing is to help
maintain it — triaging issues, reviewing pull requests, or taking on release preparation.
Contributions are welcome and do not have to wait for a release to be reviewed and merged.

## Related

- Sister project: [OmniAssist GUI](https://github.com/AfifaM9/omniassist-gui)
- Nicknames and project relationships: `docs/omni_personal/nickname_notice.md` in the
  OmniAssist GUI repository.
