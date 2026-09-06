Source: https://boschko.ca/atm-kiosk-hacking-phd2022/

# ATM/Kiosk Hacking Reloaded

Source: https://boschko.ca/atm-kiosk-hacking-phd2022/

---

ATM Hacking
Hacking ATM's & Financially Oriented Web Applications
Solving the ATM/Kiosk & Banking software hacking challenges from Positive Hack Days 2022 Payment Village.
Olivier Laflamme
06 Jun 2022
•
17 min read
Share
This blog revolves around
Positive Hack Days 2022
payment village challenges. This came to my attention by accident via some of the
Payment Village
members who personally attended this conference. Personally, it's a conference I'll make an effort to attend next year as it genuinely looks amazing.
I blogged about PHDays 2021 ATM/Kiosk challenges a few months ago, you can find that blog
here
. The machines this year were significantly better and more complex than last year. I'm seriously looking forwards to next years challenges.
It's my understanding that the people who developed this track work at
Positive Technologies
, so huge shoutout to those guys.
Online Banking Portal
One of the challenges this year was through their custom online banking application. The description is fairly barebone. In essence, during the event report everything you find.
After creating an account and signing into the application you'll be presented with the following UI. Within the app you can transfer funds, apply for loans, calculate loans as well as configure personal user data.
Rounding Attack
When converting, bank rounds the amount to two decimal places, that is, too
$0.01
. As an example, let's say that the rates for 1GBP = 1.30USD then a fraudster would transfer a small GBP amount into USD. During the transfer, as a result of conversion, they would profit 0.01 USD from the transaction. The following would apply:
0.02 USD => float(0.0153; 2) == 0.02 GBP
0.02 GBP => float(0.026; 2) == 0.03 USD
Profit = 0.01 USD
If this is confusing let me rephrase it. In this banking app, the conversion rate from USD to RUB is 79.5 therefore
$1.3 RUB = $0.01635 USD
(1.3 / 79.5 = 0.01635)
. So, if I send the equivalent of $0.01635 USD in RUB (1.3) into the USD account $0.01635 will round up to $0.02. As a result, I'll have effectively made $0.00365 out of thin air.
Let's actually prove this. As seen below, I'm transferring $1.3 rubles from the RUB account into the USD one.
The transfer was successful and $1.3 RUB (which is
≡
$0.01635 USD) was transferred/converted into USD. In the process $0.01
635
USD was rounded up to $0.02 USD netting me a $0.00365 USD profit.
Scientific Notation Bug
This is a vulnerability I've found in old MMORPG back in 2012-2014 but they appear everywhere. This occurs when the
e
scientific notation is handled for numbers. For example, sending
1.1e5
will actually send
110000
.
To prove this bug I'll send
1e1
USD which is
≡
10
from the USD account to the RUB account.
Now since the transfer rate from USD to RUB is 79.5 if we were to send 10 USD we should expect to receive 795 RUB.
Besides using this to perform the rounding attack
1.635e-2 = 0.01635
I'm not sure how to abuse this maliciously. If it's obvious to you ping me on
twitter
.
Since most of the input fields in this application are in Russian, a language I don't speak, I won't be spending time trying to find exploits within the loan applications. If I had to bet money, I'd say chances are its vulnerable to flash loan attacks or some form of credit / loan interest manipulation.
ATM Images
There are two ATM images, respectively
ATM1
and
ATM2
the descriptions to the challenges will be found before the technical details. Huge shoutout to the creator
circuit
for these VM's I highly recommend you try them out for yourself.
ATM1.ova (Difficulty Medium)
Tasks:

1. Kiosk bypass;
2. Bypass the applocker;
3. Elevation of privileges to administrator;

There are several files on the C:\ drive task_kiosk.exe , task_applocker.exe, task_escalation.exe, which need to be launched in order for the task to be counted.

task_kiosk.exe available to launch immediately after the kiosk crawl, task_applocker.exe blocked by the applocker, to run task_escalation.exe administrator rights are required.

Additional tasks - attacks on the ATM web interface (classic WEB vulnerabilities)

Limitations:

Do not use a bootable USB flash drive and safe mode;
Okay, when the VM is boot up we're presented with the following:
Let's keep it simple. Instead of finding fancy escapes try smashing down the shift key (~5 times) until we get the following popup.
Click on the "Disable this keyboard..." hyperlink.
Cool. Since this is an easy box, we have the ability to right-click on the page and go to print.
Then go to
Find printer...
to pop up the
iexplorer.exe
.
With this explorer we can spawn a
cmd.exe
shell. This is achieved by going to
C:\Windows\System32\cmd.exe
in explorer.
We have a cmd shell and we've confirmed that we are
ATM
user. If you remember from reading the challenge description, we were told that theres a lot of files on disk that we need to run to solve this VM. As seen below the
C:\Atm
is empty. This is where we should expect to see the binaries.
What I ended up doing was going to
C:\Users\ATM\Downloads
where I found the following folder.
The idea is to open it in a new window. The password to the zip is
123
and I extracted the binary to my downloads folder. In doing so you're no-longer inside the printer explorer. As seen below, this you get a proper windows explorer.
Now if you go back to
C:\Atm
or
C:\
voila we've got files.
There's a file called
atmkey
when opened in notepad we get the following string
MXTivV99iqrQLgA
no real idea what this does at this point maybe its the password to the
ATM
user?
If I open the
payout.exe
the following pops up which loosely translate to
successful issuance of money
.
Going back to basics I decided to do some recon on the system.
I thought that maybe the
atmkey.txt
is the password for the ATM user?
But that wasn't it. Before I forgot I went back to
C:\
and ran the
task_kiosk.exe
making to completion of the first of three steps official.
If I run the
task_applocker.exe
(steps i've clearly not finished) i'll receive the following message. Same applies for the
task_escalation.exe
.
While looking around I found the following file. This is actually super neat. Basically since the user ran the
Get-History
PowerShell cmdlet this lets us get the full history from that point (the list of commands entered during the current session). This is caused by the
PSReadline
module being installed and enabled by default starting from PowerShell Windows 10 onward. It is responsible for recording what is typed into the console. Think of it as the
history
command in linux. The default option is to save history to a file. In our case this file is
ConsoleHost_history.txt
From the explorer windows I opened PowerShell by running
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
. Then I ran
runas
to and tried the
Admin:hackhack
credentials found in the
ConsoleHost_history.txt
file.
The logical thing to do now would be to run the
task_escalation.exe
binary now that we're admin. As seen below turns out that we're admin but our process isn't so the binary wont execute successfully.
However, if I run the
task_applocker.exe
binary it turns out I bypassed AppLocker somehow. I'd like to think that an AppLocker rule for this binary wasn't simply assigned to
ATM
user only and rather to
EVERYONE
but I didn't bother checking
gpedit.msc
. Not really sure if this was the intended solution but I'll keep it moving.
Okay. Let's say I want to open explorer from this
runas
terminal I wont be unable to.
This also happened to the recycle-bin when running
start shell:RecycleBinFolder
and
taskmgr
. Additionally
net use
and
fsutil fsinfo drives
didn't show me anything hidden or interesting.
To get around this I decided to open ms-paint with the runas admin terminal session but again my explorer was downgraded and the
C:\Atm
and
C:\
directories were empty.
From paint you simply attempt to open a project and spawn PowerShell from the ms-paint explorer. Now I was able to go to
C:\Users\Admin\
which I previously was unable to as the
ATM
user. Unfortunately, I and found absolutely nothing there. Going back to see if there is a unique
ConsoleHost_history.txt
but its the same file at heart. By the way there is not password reuse from
Admin->Administrator
.
Remember how I said that running
@start iexplore
and
start .
didn't work. Let's just go full morbius mode and use
wmic.exe
to spawn explorer.
As a result we've completely exit the sandbox =:) What happens next is something I genuinely don't understand (and something I'm not going to bother understanding, sorry) If I right-click the windows icon and click on
Windows PowerShell (Admin)
The UAC will prompt and if I use the password
hackhack
it works and I get a PowerShell shell.
Then if I run the
task_escalation.exe
binary... success?
This is slightly annoying. But it makes sense,
runas
doesn't run with higher integrity as far as I know even when it's being ran as an admin. As you can see in the image below the same admin user is running the same command. So it has to be a feature of
runas
that I won't bother looking into right now. Or perhaps the issue is with how the binary perceives privileges which was a nice way to burn a good 1:30h =:)
ATM2.ova (Difficulty Hard)
ATM2 difficulty hard

Tasks:

1. Kiosk bypass;
2. Bypass the applocker;
3. Elevation of privileges to administrator;

There are several files on the C:\ drive task_kiosk.exe , task_applocker.exe , task_escalation.exe , which need to be launched in order for the task to be counted.
task_kiosk.exe available to launch immediately after the kiosk crawl, task_applocker.exe blocked by the applocker, to start task_escalation.exe administrator rights are required.


Additional tasks - attacks on the ATM web interface (classic WEB vulnerabilities)

Limitations:

Do not use a bootable USB flash drive and safe mode;
Okay so when we boot up the VM we're presented with the following.
Right-clicking doesn't work within this portal. Sticky keys also don't work. So let's keep it simple and hit
CTRL+P
and do just like before.
Cool. Literally 20 seconds after booting the VM the kiosk is already escaped.
I kinda feel bad about this so I'll show you other ways I could've escaped this kiosk. Doing
CTRL+N
to open a new windows as seen below will also provide you with everything you need to escape the kiosk.
From this point simply do
CTRL+J
and you'll have so many options to escape the kiosk.
Another kiosk bypass is by doing
CTRL+L
and you'll have a bypass in the
Browser
button as seen below.
Moving on. Within the
cmd.exe
I spawned I run
start .
to get an explorer.exe outside of the print restricted explorer spawned from the printing explorer.
There is a file
C:\Atm
with the following.
Just like in ATM1 I'll go ahead and 100% escape the sandbox/kiosk with the same
wmic
trick as before. You can also do this with
msbuild
so I don't think it's a challenge oversight.
I'll go ahead and include some embarrassing failures & low IQ moments that would have been funny if they had worked. This is really just sharing my thought process.
At this point we're looking for a way to run the
task_applocker.exe
binary.
In terms of recon I went  to Event Viewer and checked BagMRU to enumerate folders that were opened in Windows Explorer. I found nothing of real value.
So I went ahead with some generic AppLocker bypasses attempts like
rundll32.exe advpack.dll,RegisterOCX c:\task_applocker.exe
or stuff like
rundll32 url.dll, OpenURL file://c:\task_applocker.exe
I even tried to make it fancier
rundll32.exe javascript:"\..\mshtml.dll,RunHTMLApplication ";eval("w=new%20ActiveXObject(\"WScript.Shell\");w.run(\"cmd\");window.close()");
but eventually I concluded that
rundll32
,
regsvr32
,
installutil.exe
,
bginfo.exe
,
regasm.exe
,
regsvcs.exe
weren't going to work which are old / known methods of bypass the poorly made rules. I then attempted it with
Msbuild
but same story.
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Msbuild.exe C:\Atm\test.csproj
However, the main reason behind MsBuild failing was windows defender.
Obviously I didn't have the permissions to exclude AV locations for my binaries.
Don't get it twisted, it's not like defender will ever really prevent us from doing what we want. We can bypass it with little to no effort. Again, if we wanna go full morbius mode I can retrieve a CobaltStrike beacon. But ultimately this does nothing for us.
Going back to the AppLocker bypass If  I was admin I'd be able to simply reimport/overwrite/delete the existing group policies with null/* ones as demonstrated in
this technique
and
this blog
.
I'll mention that moving the binary to folders that are by default writable by normal users didn't help. The same goes for using a downgraded version of PowerShell. So I ended up trying a load of different stuff. Generally speaking I was trying to find a
lolbas
that might work. LOLBAS are Living Off The Land Binaries and Scripts, if the binary wasn't there then I "brought my own land" and these can be useful for bypassing AppLocker rules in general. Below are a few examples.
At this point I was seriously at a loss. I had committed ~6-7h trying to solve this with more-or-less no valuable progress so I asked the challenge creator for the hint.
I
NEVER
use
runas
so this was completely unknown to me. And while enumerating I found no
c:\ATM\username\appdata\roaming\microsoft\credentials
files or artifacts so I'm unclear as to how someone who doesn't know about this flag would figure it out. Everyday is a school day as they say. Since there is not a simple way to run a program with higher privileges without using the
/savecred
option in windows, it turns out that it's still used fairly often? I presume especially if the program must be interactive. Basically, since the Admin credentials have been previously saved by this user it can be retrieved with the
/savecred
flag.
Quickly checking the privileges to see if we can run
gpedit.msc
We are a member of Administrators so we should have no issues editing/creating AppLocker rules. Instead of creating a
*
path rule I'll simply delete the rule below.
And after running a quick
gpupdate -force
I was able to run the
task_applocker.exe
binary.
Nice. All that is left is to run
task_escalation.exe
. At this stage, just like in ATM1 I'm unable to open an explorer from within the
runas /user:Admin
command-line. To get around this I run
mspaint
to obtain a file explorer that would allow me to navigate to
C:\users\Admin
and notice a
.lnk
file on the Admin users desktop.
Simply right-click the
administrator_cmd.lnk
, go to
Properties
then navigate into the
Shortcut
tab. Basically all a
.lnk
really is, is a shortcut to a binary. We'll change this to the
task_escalation.exe
binary as seen below.
Then just save and apply the changes and run the
.lnk
In doing so it'll trigger a UAC prompt so clicking
Yes
will complete the execution.
And thats it! We've completed ATM2.
Additional tasks - attacks on the ATM web interface
This is an optional section that I did not complete. I personally have no interest at digging into web applications on my free time. Regardless, I'll  document my notes and progress. Maybe someone will want to pickup where I left-off.
Remember the kiosk escape with
CTRL+N
that disclosed the IP of the ATM. So that a public IP that resolves to
bank.paymentvillage.org
on port 80.
Doing some quick recon I found a few endpoints that didn't amount to much.
--- Ports ---
22 open ssh
80 open http
5432 open postgresql
6379 open redis
8081 open blackice-icecap
There's also another useless page that doesn't require authentication that we can access that looks like the following.
Below is some weird behavior. The way the app is failed authentications results in the banking dashboard being leaked. The redirection actually leaks the page the valid user is redirected upon successfully authentication.
When I attempt to log in with invalid credentials I get redirected back to the initial page. During this process the application leaks the
/cabinet
endpoint data which is only accessible when you log in successfully. So this is a weird "vuln" in & of itself.
To prove this I'm able render the page in burp preview. Notice that I don't have a valid user cookie.
Moving on. Turns out that I can simply use my credentials from the web challenges to authenticate. This application is completely useless, there's no actions or changes you can perform here.
I ran some cheap directory enumeration on the endpoint and retrieved the following endpoints.
The endpoint of interest to us is
favicon.ico
as seen below we get a verbose error message mentioning
file_get_contents
which screams path traversal / potential LFI.
As a result we have arbitrary file read as seen below.
I didn't peruse this path any further. Theres definitely something here. I'll leave finding it as an exercise to the reader. If you want to pick it up from here
curl --path-as-is http://bank.paymentvillage.org/favicon.ico/../index.php
. Feel free to let me know what you stumble upon.
Some extra notes. Theres a lot of files in the
C:\Atm
directory. They don't all spawn alters or create funky logs / have any visible important functionality. However, there is a binary
server.exe
that caught my attention. After starting the binary and confirming that it's running I got the following error messages.
This actually ends up happening when you try to reach the ATM on port 80 from another host on the same VNET or locally.
When you click
OK
an internet explorer page will launch and you'll be directed to the organizers site.
I guess what someone could do is trace the intended hackerguard.dll calls and make the lib yourself fulfilling what
server.exe
procs. This is not my definition of a good time. Also the main issue with this is that I can't run process hacker, daphne, or process explorer without "
cheating
" as Admin. This doesn't stop you from simply exporting them using my
gofileserver
. After-all building a custom dll that calls functions in
Kernel32.dll
which will in turn spawn a cmd or whatever isn't challenging. The idea here is that
server.exe
will load the DLL into a process. In a restricted environment, it can be injected into a legitimate process and thus bypass the restriction mechanisms.
Final Thoughts:
I personally think that anyone reading this blog should attempt this lab themselves. These VM's offer a unique challenge set & touch on skills/techniques you don't often use.
To my knowledge this is the first writeup of the Payment Village 2022 challenges. I'm really looking forwards to people releasing their own write-ups documenting the bugs they found and their solutions in the coming months. Feel free to ping me if you find new exploits or bugs. I'd genuinely be interested in seeing them.
I hope you liked the blogpost. Follow me on
twitter
I sometimes post interesting stuff there too.
Thank you for reading!