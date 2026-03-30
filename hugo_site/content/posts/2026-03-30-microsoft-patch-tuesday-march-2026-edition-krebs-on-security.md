---
title: "Microsoft Patch Tuesday, March 2026 Edition – Krebs on Security"
date: 2026-03-30T21:32:24+00:00
slug: "microsoft-patch-tuesday-march-2026-edition-krebs-on-security"
draft: false
tags:
  - "microsoft"
  - "windows"
  - "sql server"
  - "rapid7"
  - ".net"
  - "patch tuesday"
  - "cve"
  - "office"
categories:
  - "translated-articles"
original_url: "https://krebsonsecurity.com/2026/03/microsoft-patch-tuesday-march-2026-edition/"
---

**Microsoft Corp.** released security updates today to address at least 77 vulnerabilities in its **Windows** operating systems and other software. There are no critical "zero-day" flaws this month (compared to the five zero-day vulnerabilities reported in February), but as usual, some of these patches may require urgent attention from organizations using Windows. Here are a few highlights from this month's Patch Tuesday.

![](https://krebsonsecurity.com/wp-content/uploads/2026/03/winupdatechecking.png)

Image: Shutterstock, @nwz.

Two of the vulnerabilities Microsoft patched today were previously disclosed publicly. [CVE-2026-21262](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-21262) is a weakness that allows an attacker to elevate their privileges on **SQL Server 2016** and later editions.

"This isn't just any elevation of privilege vulnerability; the advisory notes that an authorized attacker can elevate privileges to sysadmin over a network," said Adam Barnett from **Rapid7**. "The CVSS v3 base score of 8.8 is just below the threshold for critical severity, since low-level privileges are required. It would be courageous to defer patching this one."

The other publicly disclosed flaw is [CVE-2026-26127](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-26127), a vulnerability in applications running on **.NET**. Barnett said the immediate impact of exploitation is likely limited to denial-of-service by triggering a crash, with potential for other types of attacks during a service reboot.

It would hardly be a proper Patch Tuesday without at least one critical **Microsoft Office** exploit, and this month doesn't disappoint. [CVE-2026-26113](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-26113) and [CVE-2026-26110](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-26110) are both remote code execution flaws that can be triggered simply by viewing a booby-trapped message in the Preview Pane.

**Satnam Narang** at **Tenable** notes that just over half (55%) of all Patch Tuesday CVEs this month are privilege escalation bugs, and of those, six were rated "exploitation more likely" — across Windows Graphics Component, Windows Accessibility Infrastructure, Windows Kernel, Windows SMB Server, and Winlogon. These include:

- [CVE-2026-24291](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-24291): Incorrect permission assignments within the Windows Accessibility Infrastructure to reach SYSTEM (CVSS 7.8)
- [CVE-2026-24294](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-24294): Improper authentication in the core SMB component (CVSS 7.8)
- [CVE-2026-24289](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-24289): High-severity memory corruption and race condition flaw (CVSS 7.8)
- [CVE-2026-25187](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-25187): Winlogon process weakness discovered by Google Project Zero (CVSS 7.8).

**Ben McCarthy**, lead cybersecurity engineer at **Immersive**, highlighted [CVE-2026-21536](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-21536), a critical remote code execution bug in the Microsoft Devices Pricing Program component. Microsoft has already resolved this issue on their end, and fixing it requires no action from Windows users. However, McCarthy noted that it is one of the first vulnerabilities identified by an AI agent and officially recognized with a CVE attributed to the Windows operating system. It was discovered by **XBOW**, a fully autonomous AI penetration testing agent.

XBOW has consistently ranked at or near the top of the Hacker One bug bounty leaderboard for the past year. McCarthy said CVE-2026-21536 demonstrates how AI agents can identify critical 9.8-rated vulnerabilities without access to source code.

"Although Microsoft has already patched and mitigated the vulnerability, it highlights a shift toward AI-driven discovery of complex vulnerabilities at increasing speed," McCarthy said. "This development suggests that AI-assisted vulnerability research will play an increasingly important role in the security landscape."

Microsoft earlier provided patches to address nine browser vulnerabilities, which are not included in the Patch Tuesday count above. Additionally, Microsoft issued a crucial out-of-band (emergency) [update on March 2](https://support.microsoft.com/en-us/topic/march-2-2026-kb5082314-os-build-20348-4776-out-of-band-606518e5-28d2-4ebe-be25-26287e2fc703) for **Windows Server 2022** to address a certificate renewal issue with passwordless authentication technology Windows Hello for Business.

Separately, **Adobe** shipped updates to fix 80 vulnerabilities — some of them critical in severity — in [a variety of products](https://helpx.adobe.com/security/Home.html), including **Acrobat** and **Adobe Commerce**. **Mozilla Firefox** v148.0.2 resolves three high-severity CVEs.

For a complete breakdown of all the patches Microsoft released today, check out the SANS Internet Storm Center's [Patch Tuesday post](https://isc.sans.edu/forums/diary/Microsoft%20Patch%20Tuesday%20March%202026/32782/). Windows enterprise administrators who wish to stay informed about any problematic updates should visit [AskWoody.com](https://www.askwoody.com). Please feel free to drop a comment below if you experience any issues applying this month's patches.
