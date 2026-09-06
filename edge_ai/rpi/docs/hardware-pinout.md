2.13inch e-Paper HAT (B) Manual
2.13inch e-Paper (B)
2.13inch-e-Paper-B-1.jpg

250x122, 2.13inch EPD panel
2.13inch e-Paper HAT (B)
2.13inch-e-paper-hat-b-5 1.jpg

250x122, 2.13inch EPD HAT for Raspberry Pi, three-color, SPI interface
Introduction
Version

V4: resolution of 250 × 122, V4 version hardware structure and interface compatible with V3 version, using V4 program. If you are buying for the first time and have a V4 label on the back of the screen, just use the V4 program.
V3: The resolution is 212 × 104, and the hardware structure and interface of V3 version are compatible with older versions. The V3 program is used.
Parameters
Dimensions	2.13inch
Driver Board Dimensions	65mm × 30.2mm
Display Dimensions	48.55mm × 23.71mm
Outline Dimensions (screen only)	59.2mm × 29.2mm × 0.98mm
Operating Voltage	3.3V / 5V (5V is required for power and signal)
Communication Interface	SPI
Dot Pitch	0.194mm × 0.194mm
Resolution	250 × 122
Display Color	Black, White, Red
Grey Scale	2
Refresh Time	15s
Refresh Power	26.4mW（typ.）
Standby Current	< 0.01uA (almost 0)
Working Temperature	0 ~ 40 ℃
Storage Temperature	-25 ~ 40 ℃
Refresh time: The refresh time is the experimental results, the actual refresh time will have errors, and the actual effect shall prevail. There will be a flickering effect during the global refresh process, this is a normal phenomenon.
Power consumption: The power consumption data is the experimental results. The actual power consumption will have a certain error due to the existence of the driver board and the actual use situation. The actual effect shall prevail.
Communication Method
Operating Principle
Program Principle
We define the pixels in a monochrome picture, 0 is black and 1 is white.
White: □: Bit 1
Black: ■: Bit 0

The dot in the figure is called a pixel. As we know, 1 and 0 are used to define the color, therefore we can use one bit to define the color of one pixel, and 1 byte = 8pixels
For example, If we set the first 8 pixels to black and the last 8 pixels to white, we show it by codes, they will be 16-bit as below:
E-paper hardware work 1.png

For the computer, the data is saved in MSB format:
E-paper hardware work 2.png
So we can use two bytes for 16 pixels.

For the 2.13inch e-paper B, it is red and black, we need to split the picture into 2 pictures, one black and white picture, a red and white picture because one register controls the black and white display during transmission, and the other register controls the red and white show. 1 byte of 2.13 black and white part controls 8 pixels, and 1 byte of red and white part controls 8 pixels
For example, suppose there are 8 pixels, the first 4 are red, and the last 4 are black:
They need to be split into a black-and-white picture and a red-and-white picture. Both pictures have 8 pixels, but the first four pixels of the black and white picture are white, the last 4 pixels are black, and the first 4 pixels of the red and white picture are black. pixels are red, the last four pixels are white.
2.13inch-epPaer-B-pixels.png

If we specify that white is stored as 1 and red or black is stored as 0, then we have the following representation:
2.13inch-epPaer-B-pixels-2.png

And 1 byte of black and white part controls 8 pixels, and 1 byte of red and white part controls 8 pixels, then it can be expressed as follows:

2.13inch-epPaer-B-pixels-3.png

Precautions
For e-Paper displays that support partial refresh, please note that you cannot refresh them with the partial refresh mode all the time. After refreshing partially several times, you need to fully refresh EPD once. Otherwise, the display effect will be abnormal.
It is a normal phenomenon that the three-color or multi-color EPD will have a certain color difference in different batches. Hence, it is recommended to use the program to clear all the pictures on the EPD and store it facing up. Please clear the screen several times before powering on.
Note that the screen cannot be powered on for a long time. When the screen is not refreshed, please set the screen to sleep mode or power off it. Otherwise, the screen will remain in a high voltage state for a long time, which will damage the e-Paper and cannot be repaired!
When using the e-Paper display, it is recommended that the refresh interval be at least 180s, and refresh at least once every 24 hours. If the e-Paper is not used for a long time, you should use the program to clear the screen before storing it. (Refer to the datasheet for specific storage environment requirements.)
After the screen enters sleep mode, the sent image data will be ignored, and it can be refreshed normally only after initializing again.
Control the 0x3C or 0x50 (refer to the datasheet for details) register to adjust the border color. In the demo, you can adjust the Border Waveform Control register or VCOM AND DATA INTERVAL SETTING to set the border.
If you find that the created image data is displayed incorrectly on the screen, it is recommended to check whether the image size setting is correct, change the width and height settings of the image and try again.
The working voltage of the e-Paper display is 3.3V. If you buy the raw panel, you need to add a level convert circuit for compatibility with 5V voltage. The new version of the driver board (V2.1 and subsequent versions) has added a level processing circuit, which can support both 3.3V and 5V. The old version only supports a 3.3V working environment. You can confirm the version before using it. (The version number is under the board name.)
The FPC cable of the screen is fragile, Please note: Do not bend the cable along the vertical direction of the screen to avoid tearing the cable; Do not repeatedly excessive bending the cable, to avoid the cable fracture; Do not bend the cable toward the front of the screen to avoid the cable from being disconnected from the panel. It is recommended to use fixed wiring during debugging and development.
The screen of e-Paper is relatively fragile, please try to avoid dropping, bumping and pressing hard.
We recommend that customers use the sample program provided by us to test with the corresponding development board.
Working With Raspberry Pi
Hardware Connection
When connecting the Raspberry Pi, you can directly insert the board into the 40PIN pin header of the Raspberry Pi, and pay attention to the correct pins.
If you choose to connect with an 8PIN cable, please refer to the pin correspondence table below:

Raspberry Pi Pinout
e-Paper	Raspberry Pi
BCM2835	Board
VCC	3.3V	3.3V
GND	GND	GND
DIN	MOSI	19
CLK	SCLK	23
CS	CE0	24
DC	25	22
RST	17	11
BUSY	24	18
Enable SPI Interface
Open the Raspberry Pi terminal and enter the following command in the config interface:
sudo raspi-config
Choose Interfacing Options -> SPI -> Yes Enable SPI interface
RPI open spi.png
Then reboot your Raspberry Pi:

sudo reboot
Check /boot/config.txt, and you can see 'dtparam=spi=on' was written in.
Raspberry Pi Guides for 4.37 e-Paper.jpg

To make sure SPI is not occupied, it is recommended to close other drivers' coverage. You can use ls /dev/spi* to check whether SPI is occupied. If the terminal outputs /dev/spidev0.1 and /dev/spidev0.1, SPI is not occupied.
Raspberry Pi Guides for 4.37 e-Paper02.jpg

C
Install lg library
#Open the Raspberry Pi terminal and run the following commands: 
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
make
sudo make install
#For more details, you can refer to the source code: https://github.com/gpiozero/lg
Install gpiod library (Optional)
#Open the Raspberry Pi terminal and run the following commands: 
sudo apt-get update
sudo apt install gpiod libgpiod-dev
Install BCM2835:
#Open the Raspberry Pi terminal and run the following command
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
# For more information, please refer to the official website: http://www.airspayce.com/mikem/bcm2835/
Install WiringPi (Optional):
#Open the Raspberry Pi terminal and run the following command:
sudo apt-get install wiringpi
#For Raspberry Pi systems after May 2019 (earlier than before, you may not need to execute), you may need to upgrade:
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
#Run gpio -v and version 2.52 will appear. If it does not appear, the installation is wrong.

#Bullseye branch system use the following command:
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# Run gpio -v and version 2.60 will appear. If it does not appear, it means that there is an installation error.
Download the demo via GitHub (You can skip this step if you have downloaded it.)
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/
Download the demo (You can skip this step if you have downloaded it.)
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Alternate method of decompression:
sudo apt-get install p7zip-full
7z x E-Paper_code.zip -O./e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Compile the demo (Note: -j4 is to compile with 4 threads, the numbers can be modified by yourself; EPD=epd2in13bV4 is to specify a macro definition, and epd2in13bV4 corresponds to the test demo in the main function).
# Now at e-Paper/RaspberryPi_JetsonNano
cd c
sudo make clean
sudo make -j4 EPD=epd2in13bV4
Run the demo
sudo ./epd
Python
Install the function library.
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
Install the function library (python2).
sudo apt-get update
sudo apt-get install python-pip
sudo apt-get install python-pil
sudo apt-get install python-numpy
sudo pip install spidev
Install gpiozero library (it is installed in the system by default, if not, you can install it by following the commands below)
sudo apt-get update
# python3
sudo apt install python3-gpiozero
# python2
sudo apt install python-gpiozero
Download the demo via GitHub (You can skip this step if you have downloaded it.)
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/
Download the demo (You can skip this step if you have downloaded it.)
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Alternate method of decompression:
sudo apt-get install p7zip-full
7z x E-Paper_code.zip -O./e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Run the demo.
# Make sure it's in e-Paper/RaspberryPi_JetsonNano/
cd python/examples/
python3 epd_2in13b_V4_test.py
