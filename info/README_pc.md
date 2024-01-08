# Vision-Motion
Repository for python-based vision and motion processing code

&nbsp;

## For Running on a PC ##

The Team 4121 Vision Processing can be run on a desktop or laptop PC in a virtual
environment which emulates the services available on a Raspberry Pi 4.

To accomplish this reliably, however, requires two layers of virtualization.
The first layer is a Virtual Machine (VM) running a Linux distribution of your
choice (this has been tested on Debian 11).  Either [VMware](https://www.vmware.com/)
or [VirtualBox](https://www.virtualbox.org/) can
run the Linux distribution.  This Linux distribution is a "guest" operating
system on your MS-Windows "host" operating system.

The second layer is a [Docker](https://www.docker.com/) container / sandbox running
*within* that virtualized Linux operating system.  It is the *container* which provides
a consistent set of libraries and tools which mimic the Team 4121 Raspberry Pi 4.

&nbsp;

### First-Time Run ###



&nbsp;

### Subsequent Runs ###

Navigate to the **4121-Vision** directory.  This is the directory which will emulate
**/home/pi** from the Raspberry Pi.  Note that it is recommended to launch your
"editor of choice" *before* the container, because that editor is unlikely to be
available from the container's command line.  Also, *ensure that you have attached
a camera to your Linux VM* -- Vision Proccessing won't run without it...

To enter the "Pi emulator" container, issue the command:
<pre>Utilities/docker_vision_shell.sh</pre>

You will now be at the **bash** command line within the Pi emulator.  It will *appear*
as if you are at the home directory of your login account.  *This is an illusion -- you
are still within <b>4121-Vision</b>*  (specifically, Docker used **chroot** to
provide this illusion).

Next, run a script to set some environment variables which tell the Vision Processing
application that it's not running on a Pi.  Issue the command:
<pre>source Utilities/run_pc.inc</pre>

Do *not* try to just execute **run_pc.inc** as a shell script - the environment
variables it sets will be reset immediately upon its completion.

Finally, run the Vision Processing application with
<pre>./raspberrypi4.py</pre>

The processing results will be displayed in a popup window within your Linux desktop.
