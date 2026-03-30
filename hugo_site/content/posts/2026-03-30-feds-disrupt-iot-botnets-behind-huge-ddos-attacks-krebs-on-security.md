---
title: "Feds Disrupt IoT Botnets Behind Huge DDoS Attacks – Krebs on Security"
date: 2026-03-30T21:30:21+00:00
slug: "feds-disrupt-iot-botnets-behind-huge-ddos-attacks-krebs-on-security"
draft: false
tags:
  - "iot"
  - "ddos"
  - "botnet"
  - "cybersecurity"
  - "distributed denial-of-service"
  - "internet of things"
  - "router security"
  - "web camera"
categories:
  - "translated-articles"
original_url: "https://krebsonsecurity.com/2026/03/feds-disrupt-iot-botnets-behind-huge-ddos-attacks/"
---

The U.S. Justice Department joined authorities in Canada and Germany to dismantle the online infrastructure behind four highly disruptive botnets that compromised over three million Internet of Things (IoT) devices, such as routers and web cameras. The federal government claims that these four botnets—named **Aisuru**, **Kimwolf**, **JackSkid**, and **Mossad**—are responsible for a series of recent record-breaking distributed denial-of-service (DDoS) attacks capable of taking nearly any target offline.

![](https://krebsonsecurity.com/wp-content/uploads/2026/01/ss-botnet.png)

Image: Shutterstock, @Elzicon.

The Justice Department stated that the Department of Defense Office of Inspector General’s (DoDIG) **Defense Criminal Investigative Service** (DCIS) executed seizure warrants targeting multiple U.S.-registered domains, virtual servers, and other infrastructure involved in DDoS attacks against Internet addresses owned by the DoD.

The government alleges that the unnamed individuals controlling these four botnets used their crime machines to launch hundreds of thousands of DDoS attacks, often demanding extortion payments from victims. Some victims reported losses and remediation expenses amounting to tens of thousands of dollars.

The oldest of the botnets—Aisuru—issued more than 200,000 attack commands, while JackSkid launched at least 90,000 attacks. Kimwolf issued over 25,000 attack commands, and Mossad was blamed for roughly 1,000 digital sieges.

The DOJ [announced](https://www.justice.gov/usao-ak/pr/authorities-disrupt-worlds-largest-iot-ddos-botnets-responsible-record-breaking-attacks) that the law enforcement action was designed to prevent further infection of victim devices and to limit or eliminate the ability of the botnets to launch future attacks. The case is being investigated by DCIS with assistance from the FBI’s field office in Anchorage, Alaska, and nearly two dozen technology companies are credited for their support.

“By working closely with DCIS and our international law enforcement partners, we collectively identified and disrupted criminal infrastructure used to carry out large-scale DDoS attacks,” said Special Agent in Charge **Rebecca Day** of the FBI’s Anchorage Field Office.

Aisuru emerged late in 2024 and by mid-2025 was launching [record-breaking DDoS attacks](https://krebsonsecurity.com/2025/10/ddos-botnet-aisuru-blankets-us-isps-in-record-ddos/) as it rapidly infected new IoT devices. In October 2025, Aisuru was used to seed Kimwolf, an Aisuru variant that introduced a novel spreading mechanism allowing the botnet to infect devices hidden behind internal networks.

On January 2, 2026, the security firm **Synthient** [publicly disclosed](https://krebsonsecurity.com/2026/01/the-kimwolf-botnet-is-stalking-your-local-network/) the vulnerability Kimwolf was exploiting to propagate so quickly. This disclosure helped curtail Kimwolf’s spread somewhat, but since then several other IoT botnets have emerged that effectively copy Kimwolf’s spreading methods while competing for the same pool of vulnerable devices. According to the DOJ, JackSkid also targeted systems on internal networks like Kimwolf.

The DOJ said its disruption of the four botnets coincided with “law enforcement actions” conducted in Canada and Germany targeting individuals who allegedly operated those botnets, although no further details were provided about the suspected operators.

In late February, KrebsOnSecurity identified [a 22-year-old Canadian man](https://krebsonsecurity.com/2026/02/who-is-the-kimwolf-botmaster-dort/) as a core operator of the Kimwolf botnet. Multiple sources familiar with the investigation told KrebsOnSecurity that another prime suspect is a 15-year-old living in Germany.
