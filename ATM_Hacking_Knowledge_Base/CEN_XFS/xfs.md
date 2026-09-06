Source: https://en.wikipedia.org/wiki/CEN/XFS

# CEN/XFS - Wikipedia

Source: https://en.wikipedia.org/wiki/CEN/XFS

---

Toggle the table of contents
CEN/XFS
4 languages
Deutsch
Italiano
日本語
Русский
Edit links
Article
Talk
English
Read
Edit
View history
Tools
Tools
move to sidebar
hide
Actions
Read
Edit
View history
General
What links here
Related changes
Upload file
Permanent link
Page information
Cite this page
Get shortened URL
Print/export
Download as PDF
Printable version
In other projects
Wikidata item
Appearance
move to sidebar
hide
From Wikipedia, the free encyclopedia
Financial server architecture for Microsoft Windows
This article is about a computing standard. For other uses, see
XFS (disambiguation)
.
This article has multiple issues.
Please help
improve it
or discuss these issues on the
talk page
.
(
Learn how and when to remove these messages
)
This article's
use of
external links
may not follow Wikipedia's policies or guidelines
.
Please
improve this article
by removing
excessive
or
inappropriate
external links, and converting useful links where appropriate into
footnote references
.
(
April 2017
)
(
Learn how and when to remove this message
)
This article includes a
list of references
,
related reading
, or
external links
,
but its sources remain unclear because it lacks
inline citations
.
Please help
improve
this article by
introducing
more precise citations.
(
March 2025
)
(
Learn how and when to remove this message
)
This article
needs additional citations for
verification
.
Please help
improve this article
by
adding citations to reliable sources
. Unsourced material may be challenged and removed.
Find sources:
"CEN/XFS"
–
news
·
newspapers
·
books
·
scholar
·
JSTOR
(
April 2024
)
(
Learn how and when to remove this message
)
(
Learn how and when to remove this message
)
CEN/XFS
or
XFS
(
extensions for financial services
)
[
1
]
provides a client-server architecture for financial applications on the
Microsoft Windows
platform, especially peripheral devices such as
EFTPOS
terminals and
ATMs
which are unique to the financial industry. It is an international standard promoted by the
European Committee for Standardization
(known by the acronym CEN, hence CEN/XFS). The standard is based on the
WOSA
Extensions for Financial Services
or
WOSA/XFS
developed by
Microsoft
.
With the move to a more standardized software base, financial institutions have been increasingly interested in the ability to pick and choose the application programs that drive their equipment.  XFS provides a common
API
for accessing and manipulating various financial services devices regardless of the manufacturer.
History
[
edit
]
Chronology:
1991 - Microsoft forms "Banking Solutions Vendor Council"
1995 - WOSA/XFS 1.11 released
1997 - WOSA/XFS 2.0 released - additional support for 24 hours-a-day unattended operation
1998 - adopted by European Committee for Standardization as an international standard.
2000 - XFS 3.0 released by CEN
2008 - XFS 3.10 released by CEN
2011 - XFS 3.20 released by CEN
2015 - XFS 3.30 released by CEN
2020 - XFS 3.40 released by CEN
2022 - XFS 3.50 released by CEN
WOSA/XFS changed name to simply XFS when the standard was adopted by the international CEN/ISSS standards body. However, it is most commonly called CEN/XFS by the industry participants.
XFS middleware
[
edit
]
While the perceived benefit of XFS is similar to Java's "
write once, run anywhere
" mantra, often different hardware vendors have different interpretations of the XFS standard.  The result of these differences in interpretation means that applications typically use a
middleware
to even out the differences between various platforms implementation of XFS.
Notable XFS middleware platforms include:
F1 Solutions
- F1 TPS (multi-vendor ATM & POS solution)
Serquo - Dwide
(REST API middleware for XFS)
Nexus Software LLC
- Nexus Evolution
Nautilus Hyosung
-
Nextware
Cyttek Gen3XFS
- Multivendor terminal solution for ATM
Hitachi-Omron Terminal Solutions
ATOM
Diebold Agilis Power
NCR
-
NCR XFS
KAL
-
KAL Kalignite
Auriga - The Banking E-volution
- WWS Omnichannel Platform
Phoenix Interactive
Archived
2010-07-28 at the
Wayback Machine
VISTAatm
Archived
2010-11-12 at the
Wayback Machine
Acquired by Diebold
Diebold Nixdorf
ProBase (ProBase C as WOSA/XFS platform - ProBase J as J/XFS platform)
SBS Software
KIXXtension
Dynasty Technology Group
- (JSI) Jam Service Interface
HST Systems & Technologies
-
HAL Interface
FreeXFS
- open source XFS platform
GRG banking
eCAT
(multi-vendor ATM terminal solution)
TIS
xfs.js implementation
(open source for node.js community)
TEB
Orion
ibXFS (Multi-vendor ATM terminal solution) -
Hitachi Digital Payment Solutions
XFS test tools
[
edit
]
XFS test tools allow testing of XFS applications and middleware on simulated hardware. Some tools include sophisticated automatic regression testing capabilities.
Providers of XFS test tools include:
Cyttek Group
-
XFS Middleware
Abbrevia Simplicity
[1]
Paragon VirtualATM
Product Page
ATM Testing
FIS ATM TestLab,
Open Test Solutions
,
Product Brochure
(was Clear2Pay, formerly Level Four Software and Lexcel TestSystem ATM)
Serquo XFS ATM Simulator
Atmirage
KAL
KAL Kalignite
Test Utilities
Dynasty Technology Group
-
JSI Simulators
HST Systems & Technologies
(Brazil)
Takkto Technologies
(Mexico)
LUTZWOLF JDST
- Testtool for J/XFS compatibility
Afferent Software RapidFire ATM XFS
[2]
J/XFS
[
edit
]
J/XFS is an alternative
API
to CEN/XFS (which is
Windows
specific) and also to Xpeak (which is Operating System independent, based on XML messages). J/XFS is written in
Java
with the objective to provide a
platform
agnostic
client-server architecture
for financial applications, especially
peripheral devices
used in the financial industry such as
EFTPOS
terminals and
ATMs
.
With the move to a more standardized software base, financial institutions have been increasingly interested in the ability to pick and choose the application programs that drive their equipment. J/XFS provides a common
Object Oriented
API between a pure Java application and a wide range of financial devices, providing a layer of separation between application and device logic that can be implemented using a native J/XFS API or wrapping an existing implementation in
JavaPOS
or CEN/XFS.
J/XFS was developed by the companies
De La Rue
,
IBM
,
NCR
,
Wincor Nixdorf
and
Sun Microsystems
and is now hosted, monitored and maintained by the
European Committee for Standardization
, CEN.
See also
[
edit
]
Xpeak - Devices Connectivity using XML (Open Source Project).
Automated teller machine
Teller assist unit
References
[
edit
]
^
"CEN Workshop on eXtensions for Financial Services (WS/XFS)"
.
CEN-CENELEC
. Retrieved
2024-04-15
.
Braeuer, Johannes; Gmeiner, Bernadette; Sametinger, Johannes (2016).
"A Risk Assessment of Logical Attacks on a CEN/XFS-based ATM Platform"
.
International Journal on Advances in Security
.
9
(3 and 4). International Academy, Research, and Industry Association:
122–
132
. Retrieved
18 March
2025
.
External links
[
edit
]
CEN/XFS Home Page
Retrieved from "
https://en.wikipedia.org/w/index.php?title=CEN/XFS&oldid=1348328930
"
Categories
:
Windows communication and services
Device drivers
Embedded systems
Application programming interfaces
Microsoft application programming interfaces
Banking technology
Hidden categories:
Articles with short description
Short description is different from Wikidata
Wikipedia external links cleanup from April 2017
Articles lacking in-text citations from March 2025
All articles lacking in-text citations
Articles needing additional references from April 2024
All articles needing additional references
Articles with multiple maintenance issues
Webarchive template wayback links