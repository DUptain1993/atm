Source: https://www.malwarebytes.com/blog/news/2019/05/everything-you-need-to-know-about-atm-attacks-and-fraud-part-1

# Everything you need to know about ATM attacks and fraud: Part 1 | Malwarebytes Labs

Source: https://www.malwarebytes.com/blog/news/2019/05/everything-you-need-to-know-about-atm-attacks-and-fraud-part-1

---

Flashback to two years ago. At exactly 12:33 a.m., a solitary ATM somewhere in Taichung City, Taiwan, spewed out 90,000 TWD (New Taiwan Dollar)—about US$2,900 today—in bank notes.
No one was cashing out money from the ATM at the time. In fact, this seemingly odd system glitch was actually a test: The culprit who successfully infiltrated one of
First Commercial Bank
’s London branch servers issued an instruction to a cashpoint 7,000 miles away to check if a remote-controlled heist was possible.
Within 15 hours, 41 more ATM machines in other branches in Taichung and Taipei cities doled out an accumulated 83.27 million TWD, which is worth US$2.7 million today.
And while the Taiwan police
were able to successfully nab the suspects
of this million-dollar heist—most of whom hailed from European countries—many unnamed criminals taking advantage of flaws and weaknesses in ATM machines (even
financial systems
as a whole) are still at large.
Normal ATM users cannot fight against such an attack on their banks. But with vigilance, they can help bring criminals to justice. The catalyst for the successful capture of the heisters was intel provided by citizens who, after noticing the foreign nationals acting suspiciously and gathering relevant information—in this case, a car license plate number, and a credit card one of the suspects accidentally left behind—reported it to law enforcement.
Why ATMs are vulnerable
Just like any computing device, ATMs have vulnerabilities. And one way to understand why bad guys are drawn to them is to understand its components and the way it communicates with the bank network.
An ATM is composed of a computer (and its peripherals) and a safe. The former is enclosed in a cabinet. This is the same whether the ATM is a stand-alone kiosk or a “hole in the wall.” The cabinet itself isn’t particularly secure or sturdy, which is why criminals can use simple tools and a lock key purchasable online to break into it to gain access either to the computer or the safe.
The computer usually runs on Windows—a version specifically created for ATMs. ATM users don’t see the familiar Windows desktop interface because access is restricted. What we do see are user-facing applications that aid us in making transactions with the machine.
Up to now,
many ATMs
have still been running on Windows XP. If the OS is outdated, expect that the software in them may need some upgrading as well. That said, criminals can take their pick of which
exploits to use
to make the most of software vulnerabilities and take control of the remote system.
In some cases, interfaces like a USB port visible in public can encourage users with ill-intent to introduce malware to the machine via portable device. Since security software may not be installed in them, and there is a significant absence of authentication between peripherals and the OS, there is increased likelihood of infection. To date, there are already
20 strains of known ATM malware
discovered.
The cash dispenser is directly attached to the safe where the cash is stored. A compromised computer can easily give criminals access to the interface between the computer and the safe to command it to dispense cash without using stolen customer card information.
The traffic between the ATM computer and the transaction processing server is usually not encrypted, making it a breeze for hackers to intercept transmitted data from customer to bank server. Worse, ATMs are notoriously known for implementing poor
firewall
protection, which makes them susceptible to network attacks.
Other notable weaknesses are missing or misconfigured Application Control software, lack of hard drive encryption, and little-to-no protection against users accessing the Windows interface and introducing other hardware devices to the ATM.
Types of ATM attacks and scams
Hacking a bank’s server is only one of the many known ways criminals can get their hands on account holders’ card details and their hard-earned cash. Some methods are clever and tactical. Some can be crude. And others are more destructive and dangerous. Whatever the cost, we can bet that criminals will do whatever it takes to pull off a successful heist.
We have highlighted types of ATM attacks here based on their classification: terminal tampering, physical attacks, logical attacks, and social engineering.
For this post, we’ll be delving deep into the first two. (The second two attacks will be featured in Part 2 of this series.)
Terminal tampering
The majority of ATM fraud campaigns involve a level of physically manipulating parts of the machine or introducing devices to it to make the scheme work.
Skimming.
This is a type of fraud where a skimming device, usually a tandem of a card reader (skimmer) and keypad overlay or
pinhole camera
, is introduced to the machine by placing it over the card slot and keypad, respectively. The more closely it resembles that of the machine’s, the better it’ll work (and less likely to draw suspicion).
The purpose of the second reader is to copy data from the card’s magnetic stripe and PIN so the criminal can make forgeries of the card.
Of course, there are many ways to capture card and PIN data surreptitiously. They all fall under this scheme. Examples include
skimming devices that tap into the ATM’s network cables
, which can intercept data in transit.
Criminals can up the ante of their skimming campaign by purchasing a second-hand ATM (
at a bargain price
) and then rigging it to record data. These do not dispense cash. This, by far, is the most convincing method because wary account holders wouldn’t think that an entire ATM is fake. Unfortunately, no amount of card slot jiggling can save their card details from this.
Skimming devices can also be slotted at point-of-sale (POS) terminals in shops or inside gas pumps. Some skimmers are small enough to be concealed in one’s hand so that, if someone with ill intent is handed a payment card, they can quickly swipe it with their skimmer after swiping it at a POS terminal. This is
a video of a former McDonald’s employee
manning the drive-thru window caught doing just that.
Shimming.
One may refer to shimming as an upgraded form of skimming. While it still targets cards, its focus is recording or stealing sensitive data from their embedded chips.
A paper-thin shimming device is inserted in the ATM’s card slot, where it sits between the card and the ATM’s chip reader. This way, the shimmer records data from the card chip while the machine’s chip reader is reading it. Unlike earlier skimming devices, shimmers can be virtually invisible if inserted perfectly, making them difficult to detect. However, one sign that an ATM could have a shimming device installed is a tight slot when you insert your bank card.
Data stolen from chip cards (also known as EMV cards) can be converted to magnetic stripe data, which in turn can be used to create fake-out versions of our traditional magnetic stripe cards.
If you may recall, issuers once said that
EMV cards offer better protection against fraud
compared to traditional bank cards.
With more users and merchants now favoring chip cards, either due to convenience or industry compliance, it was expected that criminals would eventually find a way to circumvent the chip’s security and read data from it. Regrettably, they didn’t disappoint.
Card trapping.
Although not as broadly reported as other ATM attack schemes, card trapping is alive and, unfortunately, kicking. Of late, this has victimized
a 17-year old who lost her life savings
and
a friend o
f
a former detective from Dundee, Scotland
.
Card trapping is a method wherein criminals physically capture their target’s debit or credit card via an ATM. They do this by introducing a device, usually a
Lebanese loop
, that prevents the card from getting ejected once a transaction is completed. Criminals steal their target’s PIN by shoulder surfing or by using a small hidden camera similar to those used in skimming.
Another known card trap is called a spring trap.
Cash trapping.
This is like card trapping, only criminals are after the cash their target just withdrew. A tool—either a claw-like tool, a huge fork-like device that keeps the cash slot open after an ATM withdrawal, or a “glue trap”—is introduced to the ATM cash slot to trap at least some of the cash or most all of it.
Cash trapping that doesn’t involve pincer implements normally use what is called a false ATM presenter. This is a fake ATM cash dispenser placed in front of the real one.
Physical attacks
If wit isn’t enough to pull off a successful ATM heist, brute force might. As rough, unsophisticated, and sloppy as they look, criminals have achieved some success going this route.
Crooks who’d rather be loud than quiet in their activities have opted to
using explosives
—solid and gas, alike—
chain lassoing
the machine to be uprooted and dragged away,
ram-raiding
, and
using a digger
to dig a wall-mounted ATM out of a building. A sledgehammer, crowbar, and hammer have worked wonders, too.
In its fourth consecutive year, overall physical attacks on ATMs
continue to increase
in Europe, according to the European Association for Secure Transactions (EAST). From 2017 to 2018, there was a 16 percent increase in total losses (from US$34.6 million to US$40.2 million) and a 27 percent increase in reported incidents (from 3,584 to 4,549). The bulk of losses was due to explosive or gas attacks followed by robbery and ram-raiding.
“The success rate for solid explosive attacks is of particular concern,” said EAST Executive Director Lachlan Gunn in the report. “Such attacks continue to spread geographically with two countries reporting them for the first time in early 2019.”
The ATM Security Working Group (ATMSWG) published a document on
best practices against ATM physical attacks
[PDF] that financial institutions, banks, and ATM merchants can refer to and use in their planning to beef up the physical security of their machines. Similarly, the ATM Industry Association (ATMIA) has a handy
guide on how to prevent ATM gas and explosive attacks
[PDF].
Know when you’re dealing with a tampered ATM
Financial institutions and ATM providers know that they have a long way to go to fully address fraud and theft, and they have been finding and applying ways to step up their security measures. Of course, ATM users shouldn’t let their guard down, too.
Minimize the likelihood of facing a tampered ATM—or other dangers lurking about—by reading through and following these tips:
Before visiting an ATM
Pick an ATM that appears safe to use. It’s well lit, passers-by can see it, and it has a CCTV camera pointed at it. Ideally, go for an indoor ATM, which can be found in bank branches, shopping malls, restaurants, convenience shops, and others. Avoid machines that have been neglected or vandalized.
If you find yourself in an area you’re not familiar with, try going for ATMs that meet most of the physical requirements we mentioned.
Limit going to ATM locations alone, especially when you’re doing it outside of normal banking hours. Your friend or relative might help if the transaction goes awry. Also, their mere presence could fend off muggers and/or strangers.
Check over the ATM. Look for devices that may be sticking out from behind it or from any of its peripherals. Look for false fronts (over card and money slots, keypad, or, worse, over the entire face of the machine), tiny holes where cameras could be watching, cracks, mismatched key colors, etc. Report any of these signs to the bank then look for another ATM.
Lastly, spot anyone you think is loitering around your vicinity or acting suspiciously. Do not confront them. Instead, if their behavior is disturbing enough, report them to the police.
While using the ATM
Put away anything that will distract you while you use the ATM. Yes, we mean your phone and your Nintendo Switch. These could make one easily miss their awareness of their surroundings, which criminals can use to their advantage.
Tug on the card reader and cash dispenser to make sure there are no extra devices attached.
It pays to cover the keypad when entering your PIN, whether you’re alone in the queue or not. You may have checked over the ATM for signs for physical tampering but it’s always possible to miss things. Also, if the person next in the queue is too close, either remind them to move further back or cover the PIN pad as much as you can.
Always print a copy of your ATM receipt and put it away for safety. This way, you have something to refer to and compare against your bank statement.
After withdrawing from an ATM
Put your card, cash, and receipt away quickly and discretely.
If the ATM didn’t hand out your card, stay beside the machine and call your bank’s 24/7 support number to terminate your card, so when the criminals try to use it, it won’t work. Tell others behind you in the queue that your card is stuck, and they wouldn’t be able to use the machine until you get it out.
If the ATM didn’t dispense any money, record the exact date, time, and ATM location where this happened, and call the bank’s 24/7 support number. Snap a few pictures using your phone, too, and send a copy of it to yourself (either via SMS or email) so you have a digital record.
Also call your card issuer or bank to file for a claim, saying the ATM you use wouldn’t dispense the cash. Claiming would be a lot easier and faster if you used your own bank’s ATM inside the bank’s building.
If this happened at a convenience store, alert an employee at once. They may have a process to move things along. They can also stop other store shoppers from using the problematic machine.
Regularly review your bank statement for potential withdrawals and/or card use that you didn’t do yourself. Report the fraud to your bank if you spot any.
Considering other payment options
One doesn’t always have to keep withdrawing money from the ATM. If there are ways consumers can pay for goods without using cash from an ATM, they should at least consider these options.
Many are claiming that using the contactless or tap-and-pay feature of your card or smartphone is an effective way to combat account (and ATM fraud) entirely.
For
Part 2
of this series, we’ll be looking at logical and social engineering attacks criminals use against ATMs and their users. Until then, be on the lookout and stay safe!