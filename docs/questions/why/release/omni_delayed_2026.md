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

Omni is a terminal-first interface, and the browser interface in GUI Omni now carries the
project's day-to-day development. Rather than ship an incremental CLI release, Omni's next
release is being held so that it can land the work that follows GUI Omni's recent releases
(the v2026.8 "French Macaron" and v2026.9 "Galette" lines) together in a single, coherent
2027 release.

## What is unaffected

- **GUI Omni keeps shipping.** The delay applies to Omni only. OmniAssist GUI continues to
  receive updates on its usual schedule.
- **The existing Omni release still works.** v2026.7 "Eton Mass" remains available and
  installable; nothing is withdrawn.
- **This repository stays open.** Issues and pull requests are still welcome; changes are
  simply not cut into a release until v2027.1.

## Related

- Sister project: [OmniAssist GUI](https://github.com/AfifaM9/omniassist-gui)
- Nicknames and project relationships: `docs/omni_personal/nickname_notice.md` in the
  OmniAssist GUI repository.
