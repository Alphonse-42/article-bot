---
title: "Iran-Backed Hackers Claim Wiper Attack on Medtech Firm Stryker – Krebs on Security"
date: 2026-03-30T21:31:27+00:00
slug: "iran-backed-hackers-claim-wiper-attack-on-medtech-firm-stryker-krebs-on-security"
draft: false
tags:
  - "stryker"
  - "handala"
  - "cyber attack"
  - "iranian intelligence"
  - "data wiping"
  - "medical technology"
  - "palo alto networks"
  - "hacktivism"
categories:
  - "translated-articles"
original_url: "https://krebsonsecurity.com/2026/03/iran-backed-hackers-claim-wiper-attack-on-medtech-firm-stryker/"
---

A hacktivist group with ties to Iran's intelligence agencies is claiming responsibility for a data-wiping attack against **Stryker**, a global medical technology company based in Michigan. Reports from Ireland, where Stryker has its largest hub outside of the United States, indicate that the company sent home more than 5,000 workers today. Meanwhile, a voicemail message at Stryker’s main U.S. headquarters states that the company is currently experiencing a building emergency.

Based in Kalamazoo, Michigan, Stryker [NYSE:SYK] is a medical and surgical equipment manufacturer with global sales of $25 billion last year. In a lengthy statement posted to Telegram, a hacktivist group known as **Handala** (a.k.a. Handala Hack Team) claimed that the company’s offices in 79 countries have been forced to shut down after the group erased data from more than 200,000 systems, servers, and mobile devices.

![A manifesto posted by the Iran-backed hacktivist group Handala, claiming a mass data-wiping attack against medical technology maker Stryker.](https://krebsonsecurity.com/wp-content/uploads/2026/03/handala-stryker.png)

In their manifesto, Handala states that all acquired data is now in the hands of the free people of the world and ready to be used for the true advancement of humanity and the exposure of injustice and corruption.

The group said the wiper attack was in retaliation for a Feb. 28 missile strike on an Iranian school that killed at least 175 people, mostly children. **The New York Times** [reports](https://www.nytimes.com/2026/03/11/us/politics/iran-school-missile-strike.html) today that a military investigation has determined the United States is responsible for the deadly Tomahawk missile strike.

Handala was one of several hacker groups recently [profiled](https://unit42.paloaltonetworks.com/iranian-cyberattacks-2026/) by **Palo Alto Networks**, which links it to Iran’s **Ministry of Intelligence and Security** (MOIS). Palo Alto says Handala emerged in late 2023 and is assessed as one of several online personas maintained by [Void Manticore](https://malpedia.caad.fkie.fraunhofer.de/actor/void_manticore), a MOIS-affiliated actor.

Stryker’s website states that the company has 56,000 employees in 61 countries. A call to Stryker’s media line at its Michigan headquarters resulted in a voicemail message stating, “We are currently experiencing a building emergency. Please try your call again later.”

A [report](https://www.irishexaminer.com/news/munster/arid-41808308.html) from the **Irish Examiner** on Wednesday morning said Stryker staff are now communicating via WhatsApp for updates on when they can return to work. The story quoted an unnamed employee saying that anything connected to the network is down, and that “anyone with Microsoft Outlook on their personal phones had their devices wiped.”

“Multiple sources have confirmed that systems in the Cork headquarters have been ‘shut down’ and that Stryker devices held by employees have been wiped out,” the Examiner reported. “The login pages coming up on these devices have been defaced with the Handala logo.”

Wiper attacks typically involve malicious software designed to overwrite existing data on infected devices. However, a trusted source who spoke on condition of anonymity told KrebsOnSecurity that the perpetrators in this case appear to have used Microsoft Intune, a cloud-based service for IT teams to enforce security and compliance policies, to issue a ‘remote wipe’ command against all connected devices.

Intune provides a single web-based administrative console to monitor and control devices regardless of location. This connection is supported by [this Reddit discussion](https://www.reddit.com/r/cybersecurity/comments/1rqopq0/stryker_hit_by_handala_intune_managed_devices/) on the Stryker outage, where several users claiming to be Stryker employees said they were told to uninstall Intune urgently.

Palo Alto says Handala’s hack-and-leak activity is primarily focused on Israel, with occasional targeting outside that scope when it serves a specific agenda. The security firm noted that Handala has also taken credit for recent attacks against fuel systems in Jordan and an Israeli energy exploration company.

“Recent observed activities are opportunistic and ‘quick and dirty,’ with a noticeable focus on supply-chain footholds (e.g., IT/service providers) to reach downstream victims, followed by ‘proof’ posts to amplify credibility and intimidate targets,” Palo Alto researchers wrote.

The Handala manifesto posted to Telegram referred to Stryker as a “Zionist-rooted corporation,” which may be a reference to the company’s 2019 acquisition of the Israeli company OrthoSpace.

Stryker is a major supplier of medical devices, and the ongoing attack is already affecting healthcare providers. One healthcare professional at a major university medical system in the United States told KrebsOnSecurity they are currently unable to order surgical supplies that they normally source through Stryker.

“This is a real-world supply chain attack,” the expert said, who asked to remain anonymous because they were not authorized to speak to the press. “Pretty much every hospital in the U.S. that performs surgeries uses their supplies.”

**John Riggi**, national advisor for the **American Hospital Association** (AHA), said the AHA is not aware of any supply-chain disruptions as of yet.

“We are aware of reports of the cyber attack against Stryker and are actively exchanging information with the hospital field and the federal government to understand the nature of the threat and assess any impact on hospital operations,” Riggi said in an email. “As of this time, we are not aware of any direct impacts or disruptions to U.S. hospitals as a result of this attack. That may change as hospitals evaluate services, technology, and supply chain related to Stryker and if the duration of the attack extends.”

According to a March 11 memo from Maryland’s Institute for Emergency Medical Services Systems, Stryker indicated that some of their computer systems have been impacted by a “global network disruption.” The memo indicates that in response to the attack, several hospitals have opted to disconnect from Stryker’s various online services, including **LifeNet**, which allows paramedics to transmit EKGs to emergency physicians so that heart attack patients can expedite their treatment when they arrive at the hospital.

“As a precaution, some hospitals have temporarily suspended their connection to Stryker systems, including LIFENET, while others have maintained the connection,” wrote Timothy Chizmar, the state’s EMS medical director. “The Maryland Medical Protocols for EMS requires ECG transmission for patients with acute coronary syndrome (or STEMI). However, if you are unable to transmit a 12 Lead ECG to a receiving hospital, you should initiate radio consultation and describe the findings on the ECG.”

This is a developing story. Updates will be noted with a timestamp.

**Update, 2:54 p.m. ET:** Added comment from Riggi and perspectives on this attack’s potential to turn into a supply-chain problem for the healthcare system.

**Update, Mar. 12, 7:59 a.m. ET:** Added information about the outage affecting Stryker’s online services.
