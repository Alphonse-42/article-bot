---
title: "How AI Assistants are Moving the Security Goalposts – Krebs on Security"
date: 2026-03-30T21:33:01+00:00
slug: "how-ai-assistants-are-moving-the-security-goalposts-krebs-on-security"
draft: false
tags:
  - "ai"
  - "security risks"
  - "openclaw"
  - "prompt injection attacks"
  - "vibe coding"
  - "automated cyberattacks"
  - "django web framework"
  - "aws"
categories:
  - "translated-articles"
original_url: "https://krebsonsecurity.com/2026/03/how-ai-assistants-are-moving-the-security-goalposts/"
---

AI-based assistants or "agents" — autonomous programs that have access to the user’s computer, files, and online services and can automate virtually any task — are growing in popularity. However, they also pose significant security risks. One such assistant is OpenClaw, which has gained a large following due to its ability to simplify complex coding tasks through natural language commands.

### Security Concerns with OpenClaw

#### Prompt Injection Attacks
Security firm grith.ai reported that an attacker exploited a prompt injection vulnerability in Cline, an AI-powered issue triage workflow on GitHub. The attacker crafted an issue title containing malicious instructions, leading to the installation of rogue instances of OpenClaw with full system access across thousands of devices without user consent.

#### Vibe Coding and Unintended Consequences
Moltbook, a Reddit-like platform for AI agents built using OpenClaw, quickly gained popularity. Within days, it had over 1.5 million registered agents posting tens of thousands of messages. The platform's creator, Matt Schlicht, did not write any code himself but relied on the AI to bring his vision to life. However, this also led to unintended consequences such as the creation of a porn site for robots and the emergence of a new religion called Crustafarianism.

#### Automated Cyberattacks
Low-skilled attackers are leveraging commercial AI services to automate complex cyberattacks. For example, AWS reported an attack where a Russian-speaking threat actor used multiple AI tools to compromise over 600 FortiGate security appliances across at least 55 countries within five weeks. The attacker leveraged the efficiency and scale of AI to plan and execute attacks despite limited technical skills.

### Security Strategies

#### Lethal Trifecta
Simon Willison, co-creator of Django Web framework, introduced the concept of the "lethal trifecta," which posits that systems with access to private data, exposure to untrusted content, and external communication capabilities are vulnerable to attacks. This model highlights the importance of isolating AI agents and implementing strict security measures.

#### Isolation and Virtualization
James Wilson, enterprise technology editor for Risky Business, emphasizes the need for users to isolate OpenClaw by running it in virtual machines or on isolated networks with strict firewall rules. He notes that many users are deploying these assistants without proper security precautions, increasing risk exposure.

### Market Impact

#### Claude Code Security
Anthropic's introduction of Claude Code Security, a beta feature designed to scan codebases for vulnerabilities and suggest targeted patches, has significant implications for the cybersecurity market. The announcement led to a $15 billion drop in market value for major cybersecurity companies, reflecting concerns about AI replacing traditional security tools.

Laura Ellis from Rapid7 argues that while AI is reshaping parts of the security landscape by automating vulnerability detection, it does not render legacy security tooling redundant. Instead, it highlights the need for adaptive security measures to keep pace with evolving threats.

### Future Outlook

#### Widespread Adoption
DVULN founder CJ Moses predicts that AI assistants will become a common fixture in corporate environments due to their economic benefits and productivity gains, regardless of security concerns. The challenge lies in adapting security strategies quickly enough to mitigate risks associated with these tools.

In conclusion, while AI-based assistants offer significant advantages in automating complex tasks, they also introduce new security challenges. Organizations must balance the benefits of increased efficiency with robust security measures to protect against emerging threats.
