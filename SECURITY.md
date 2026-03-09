# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in First Steps, **please do NOT open a public GitHub issue.** Instead, report it privately using one of the following methods:

1. **GitHub Security Advisory (preferred):** Navigate to the [Security tab](https://github.com/Naftaliro/first-steps/security/advisories) of this repository and click "Report a vulnerability."
2. **Private contact:** Open a [private vulnerability report](https://github.com/Naftaliro/first-steps/security/advisories/new) directly.

## Scope

This policy covers the First Steps application, its installer scripts, the privileged helper (`first-steps-helper`), and the `.deb` packaging. Vulnerabilities in upstream system packages (GTK4, LibAdwaita, Flatpak, Timeshift, etc.) should be reported to their respective maintainers.

## What Qualifies

The following are examples of issues that should be reported as security vulnerabilities:

- The application or helper script executes arbitrary code beyond its documented purpose
- The privileged helper (`pkexec`) can be tricked into running unintended commands
- The auto-update feature downloads or executes code from an unexpected source
- Temporary files in `/tmp/first-steps-*` can be exploited via symlink attacks or race conditions
- The application transmits data to an unexpected remote endpoint
- Hardcoded credentials or secrets accidentally committed to the repository

## Response

I will acknowledge receipt of your report within **72 hours** and aim to provide a fix or mitigation within **7 days** for confirmed vulnerabilities.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Older releases | Best effort |
