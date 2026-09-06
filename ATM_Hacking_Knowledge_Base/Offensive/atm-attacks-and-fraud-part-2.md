Source: https://www.malwarebytes.com/blog/news/2019/08/atm-attacks-and-fraud-part-2

# Everything you need to know about ATM attacks and fraud: part 2 | Malwarebytes Labs

Source: https://www.malwarebytes.com/blog/news/2019/08/atm-attacks-and-fraud-part-2

---

This is the second and final installment of our two-part series on automated teller machine (ATM) attacks and fraud.
In
part 1
, we identified the reasons why ATMs are vulnerable—from inherent weaknesses of its frame to its software—and delved deep into two of the four kinds of attacks against them: terminal tampering and physical attacks.
Terminal tampering has many types, but it involves either physically manipulating components of the ATM or introducing other devices to it as part of the fraudulent scheme. Physical attacks, on the other hand, cause destruction to the ATM and to the building or surrounding area where the machine is situated.
We have also supplied guidelines for users—before, during, and after—that will help keep them safe when using the ATM.
For part 2, we’re going to focus on the final two types of attacks: logical attacks and the use of
social engineering
.
Logical ATM attacks
As ATMs are essentially computers, fraudsters can and do use software as part of a coordinated effort to gain access to an ATM’s computer along with its components or its financial institution’s (FI’s) network. They do this, firstly, to obtain cash; secondarily, to retrieve sensitive data from the machine itself and strip or chip cards; and lastly, intercept data they can use to conduct fraudulent transactions.
Enter logical attacks—a term synonymous with
jackpotting
or
ATM cash-out attacks
. Logical attacks involve the exploitation and manipulation of the ATM’s system using
malware
or another electronic device called a black box. Once cybercriminals gain control of the system, they direct it to essentially spew cash until the safe empties as if it were a slot machine.
The concept of “jackpotting” became mainstream after the late renowned security researcher
Barnaby Jack
presented and demoed his research on the subject at the
Black Hat security conference in 2010
. Many expected ATM jackpotting to become a real-world problem since then. And, indeed, it has—in the form of logical attacks.
In order for a logical attack to be successful, access to the ATM is needed. A simple way to do this is to use a tool, such as a drill, to make an opening to the casing so criminals can introduce another piece of hardware (a USB stick, for example) to deliver the payload. Some tools can also be used to pinpoint vulnerable points within the ATM’s frame or casing, such as an endoscope, which is a medical device with a tiny camera that is used to probe inside the human body.
If you think that logical attacks are too complex for the average cybercriminal, think again. For a substantial price, anyone with cash to spare can visit Dark Web forums and purchase ATM malware complete with easy how-to instructions. Because the less competent ATM fraudsters can use malware created and used by the professionals, the distinction between the two blurs.
Logical attack types
To date, there are two sub-categories of logical attacks fraudsters can carry out: malware-based attacks and black box attacks.
Malware-based attacks.
As the name suggests, this kind of attack can use several different types of malware, including Ploutus, Anunak/Carbanak, Cutlet Maker, and SUCEFUL, which we’ll profile below. How they end up on the ATM’s computer or on its network is a matter we should all familiarize ourselves with.
Installed at the ATM’s PC:
Via a USB stick. Criminals load up a USB thumb drive with malware and then insert it into a USB port of the ATM’s computer. The port is either exposed to the public or behind a panel that one can easily remove or punch a hole through. As these ATM frames are not sturdy nor secure enough to counter this type of physical tampering, infecting via USB and external hard drive will always be an effective attack vector. In a 2014 article, SecurityWeek covered
an ATM fraud that successfully used a malware-laden USB drive
.
Via an external hard drive or CD/DVD drive. The tactic is similar to the USB stick but with an external hard drive or bootable optical disk.
Via infecting the ATM computer’s own hard drive. The fraudsters either disconnect the ATM’s hard drive to replace it with an infected one or they remove the hard drive from its ATM, infect it with a Trojan, and then reinsert it.
Installed at the ATM’s network:
Via an insider. Fraudsters can coerce or team up with a bank employee with ill-intent against their employer to let them do the dirty work for them. The insider gets a cut of the cashed-out money.
Via
social engineering
. Fraudsters can use
spea
r phishing
to target certain employees in the bank to get them to open a malicious attachment. Once executed, the malware infects the entire financial institution’s network and its endpoints, which include ATMs. The ATM then becomes a slave machine. Attackers can send instructions directly to the slave machine for it to dispense money and have money mules collect.
Note that as criminals are already inside the FI’s network, a new opportunity to make money opens its doors: They can now break into sensitive data locations to steal information and/or proprietary data that they can further abuse or sell in the underground market.
Installed via
Man-in-the-Middle (MiTM)
tactics:
Via fake updates. Malware could be introduced to ATM systems via a bogus software update, as explained by Benjamin Kunz-Mejri, CEO and founder of Vulnerability Lab after he discovered (by accident) that ATMs in Germany publicly display sensitive system information during their software update process.
In an interview
, Kunz-Mejri said that fraudsters could potentially use the information to perform a MiTM attack to get inside the network of a local bank, run malware that was made to look like a legitimate software update, and then control the infected the ATM.
Black box attacks.
A black box is an electronic device—either another computer, mobile phone, tablet, or even
a modified circuit board linked to a USB wire
—that issues ATM commands at the fraudster’s bidding. The act of physically disconnecting the cash dispenser from the ATM computer to connect the black box bypasses the need for attackers to use a card or get authorization to confirm transactions. Off-premise retail ATMs are likely targets of this attack.
A black box attack could involve social engineering tactics, like dressing up as an ATM technician, to allay suspicions while the threat actor physically tamper with the ATM. At times, fraudsters use an endoscope, a medical tool used to probe the human body, to locate and disconnect the cash dispenser’s wire from the ATM computer and connect it to their black box. This device then issues commands to the dispenser to push out money.
As this type of attack does not use malware, a black box attack usually leaves little to no evidence—unless the fraudsters left behind the hardware they used, of course.
Experts have observed that as reports of black box attacks have dropped, malware attacks on ATMs are increasing.
ATM malware families
As mentioned in part 1, there are over 20 strains of known ATM malware. We’ve profiled four of those strains to give readers an overview of the diversity of malware families developed for ATM attacks. We’ve also included links to external references you can read in case you want to learn more.
Ploutus.
This is a malware family of ATM backdoors that was first detected in 2013. Ploutus is specifically designed to force the ATM to dispense cash, not steal card holder information. An earlier variant was introduced to the ATM computer via inserting an infected boot disk into its CD-ROM drive. An external keyboard was also used, as the malware responds to commands executed by pressing certain function keys (the F1 to F12 keys on the keyboard). Newer versions also use mobile phones, are persistent, target the most common ATM operating systems, and can be tweaked to make them vendor-agnostic.
Daniel Regalado, principal security researcher for Zingbox,
noted in a blog post
that a modified Ploutus variant called Piolin was used in the first ATM jackpotting crimes in the North America, and that the actors behind these attacks are not the same actors behind the jackpotting incidents in Latin America.
References on Ploutus:
Criminals hit the ATM jackpot
(Source: Symantec)
New variant of Ploutus ATM malware observed in the wild in Latin America
(Source: FireEye)
Anunak/Carbanak.
This advanced persistent malware was first encountered in the wild affecting Ukrainian and Russian banks. It’s a backdoor based on Carberp, a known information-stealing Trojan. Carbanak, however, was designed to siphon off data, perform espionage, and remotely control systems.
It arrives on financial institution networks as attachment to a spear phishing email. Once in the network, it looks for endpoints of interest, such as those belonging to administrators and bank clerks. As the APT actors behind Carbanak campaigns don’t have prior knowledge of how their target’s system works, they surreptitiously video record how the admin or clerk uses it. Knowledge gained can be used to move money out of the bank and into criminal accounts.
References on Anunak/Carbanak:
Anunak: APT against financial institutions
[PDF] (Source: Group-IB and For-IT)
The great bank robbery: the Carbanak APT
(Source: Kaspersky)
Cutlet Maker.
This is one of several ATM malware families being sold in underground hacking forums. It is actually a kit comprised of (1) the malware file itself, which is named Cutlet Maker; (2) c0decalc, which is a password-generating tool that criminals use to unlock Cutlet Maker; and (3) Stimulator, another benign tool designed to display information about the target ATM’s cash cassettes, such as the type of currency, the value of the notes, and the number of notes for each cassette.
References on Cutlet Maker:
ATM malware sold is being sold on Darknet market
(Source: Securelist)
SUCEFUL.
Hailed as the first multi-vendor ATM malware, SUCEFUL was designed to capture bank cards in the infected ATM’s card slot, read the card’s magnetic strip and/or chip data, and disable ATM sensors to prevent immediate detection.
References on SUCEFUL:
SUCEFUL: next generation ATM malware
(Source: FireEye)
Social engineering
Directly targeting ATMs by compromising their weak points, whether they’re found on the surface or on the inside, isn’t the only effective way for fraudsters to score easy cash. They can also take advantage of the people using the ATMs. Here are the
ways users can be social engineered
into handing over hard-earned money to criminals, often without knowing.
Defrauding the elderly.
This has become
a trend in Japan
. Fraudsters posing as relatives in need of emergency money or government officials collecting fees target elderly victims. They then “help” them by providing instructions on how to transfer money via the ATM.
Assistance fraud.
Someone somewhere at some point in the past may have been approached by a kindly stranger in the same ATM queue, offering a helping hand. Scammers uses this tactic so they can memorize their target’s card number and PIN, which they then use to initiate unlawful money transactions.
The likely targets for this attack are also the elderly, as well as confused new users who are likely first-time ATM card owners.
Shoulder surfing.
This is the act of being watched by someone while you punch in your PIN using the ATM’s keypad. Stolen PIN codes are particularly handy for a shoulder surfer, especially if their target absent-mindedly leaves the area after retrieving their cash but hasn’t fully completed the session. Some ATM users walk away before they can even answer the machine when it asks if they have another transaction. And before the prompt disappears, the fraudster enters the stolen PIN to continue the session.
Eavesdropping.
Like the previous point, the goal of eavesdropping is to steal the target’s PIN code. This is done by listening and memorizing the tones the ATM keys make when someone punches in their PIN during a transaction session.
Distraction fraud.
This tactic swept through Britain a couple years ago. And the scenario goes like this: An unknowing ATM user gets distracted by the sound of dropping coins behind him/her while taking out money. He or she turns around to help the person who dropped the coins, not knowing that someone else is already either stealing the cash the ATM just spewed out or swapping a fake card to his real one. The ATM user looks back at the terminal, content that everything looked normal, then goes on their way. The person they helped, on the other hand, is either given the stolen card to or tells their accomplice the stolen card’s PIN, which he/she memorized when their target punched it in and before deliberately dropping the coins.
Continued vigilance for ATM users and manufacturers
Malware campaigns, black box attacks, and social engineering are problems that are actively being addressing by both ATM manufacturers and their financial institutions. However, that doesn’t mean that ATM users should let their guards down.
Keep in mind the social engineering tactics we outlined above when using an ATM, and don’t forget to keep a lookout for something “off” with the machine you’re interacting with. While it’s quite unlikely a user could tell if an information-stealer had compromised her ATM (until she saw the discrepancies in her transaction records later), there are some malware types that can physically capture cards.
If this happens, do not leave the ATM premises. Instead, record every detail in relation to what happened, such as the time it was captured, the ATM branch you use, and which transactions you made prior to realizing the card would not eject. Take pictures of the surroundings, the ATM itself, and attempt to stealthily snap any people potentially lingering about. Finally, call your bank and/or card issuer to report the incident and request card termination.
We would also like to point you back to
part 1 of this series
again, where we included a useful guideline for reference on what to look out for before dropping by an ATM outlet.
As always, stay safe!