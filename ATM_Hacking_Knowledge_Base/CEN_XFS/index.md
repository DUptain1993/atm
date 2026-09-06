Source: https://kaimi.io/en/2024/07/analyzing-xfs-api-calls/

# Analyzing XFS API Calls - Misc

Source: https://kaimi.io/en/2024/07/analyzing-xfs-api-calls/

---

Analyzing XFS API Calls
Hello, my dear readers who have been missing the posts! I know you've all been waiting for brilliant posts over the past two years. But both I and d_x have been busy with matters that, to be honest, are second only to saving the world... or maybe not. Today's topic is
CEN/XFS
, a specific and extremely necessary standard for interacting with banking equipment, more specifically, the way to analyze XFS API calls on Windows. If you still don't know what CEN/XFS is (not to be confused with XFS, the file system), then you probably had a blissful life without a headache. But for those who are ready to dive into this swamp - welcome.
What is XFS?
The acronym stands for "Extensions for Financial Services". It allows various applications to interact with different types of banking equipment through uniform interfaces. Imagine you need to develop software that has to communicate not with one type of equipment, but with a whole zoo of various devices. That's where XFS comes to the rescue. For a very general explanation, let me refer to the following diagram:
(c) Kaspersky Lab
XFS originated from the WOSA/XFS standard. WOSA (Windows Open Service Architecture) is an older architecture from Microsoft, which... well, everything is written in Wikipedia:
https://en.wikipedia.org/wiki/Windows_Open_Services_Architecture
. Documentation on the standard is available here:
https://www.cencenelec.eu/areas-of-work/xfs_cwa16926_350_release/
.
msxfs.dll
Now for the main reason this post was conceived. msxfs.dll is a small library and one of the key components of XFS (available in the
SDK
). It acts as an intermediary between the application and various financial equipment, providing a standardized API for devices like card readers, PIN pads, receipt printers, as well as dispensers. There is a lot of malware targeting ATMs that dispense money by accessing XFS (let's skip the encryption/signature and so on aside), for instance, the old
ATMii
piece of malware.
When analyzing standard ATM software, malicious software, or creating signatures to detect it, it may be useful to track which functions were called from msxfs.dll, in what order, with what arguments, etc. Historically, for such analysis in the context of WinAPI, I've used
Rohitab API Monitor
: a convenient but somewhat outdated tool.
It allows intercepting function calls in the context of a process and displaying information about arguments, call results, and so on. The only caveat is that it requires function and argument descriptions in XML format. While such descriptions are available for most WinAPI functions, I couldn't find one for XFS, so I had to make one myself. This file I would like to share:
https://github.com/kaimi-/xfs-api-monitor
.
Place it, for example, in the following path:
API Monitor (rohitab.com)\API\XFS\XFSAPI.xml
. After that, API Monitor will pick up the specification, and you'll be able to intercept calls to msxfs.dll functions.
That's all for now. I'll try to publish the next post within a month, not in two years.
Author
Kaimi
Posted on
July 29, 2024
Categories
For newbies
,
Snippets
,
Windows
Tags
hook
,
winapi
,
windows
,
xfs
,
xml