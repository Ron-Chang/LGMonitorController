from sys import exit
from time import sleep

import hid

from lib.ultragear import brightness_commands, control_commands, find_monitors, get_set_color_command, send_command

monitors = find_monitors()
if not monitors:
    print('No monitors found')
    exit(0)

print(f'Found {len(monitors)} monitor' + ('' if len(monitors) == 1 else 's'))

devs = []
for monitor in monitors:
    dev = hid.Device(path=monitor['path'])
    print(f'Got monitor with serial number {dev.serial}')
    devs.append(dev)

print('Starting demonstration')
print('Switching to static color slot 1')
send_command(control_commands['color1'], devs)
print('Setting brightness to 12 (maximum)')
send_command(brightness_commands[12], devs)
sleep(2)
print('Setting slot 1 color to red with a bit of blue')
send_command(get_set_color_command(1, 'ff0020'), devs)
sleep(2)
print('Setting slot 1 color to greenish blue')
send_command(get_set_color_command(1, '00e0ff'), devs)
sleep(2)
print('Switching to static color slot 2')
send_command(control_commands['color2'], devs)
print('Setting brightness to 5')
send_command(brightness_commands[5], devs)
sleep(3)
print('Setting brightness to 12')
send_command(brightness_commands[12], devs)
print('Switching to dynamic color mode')
send_command(control_commands['color_dynamic'], devs)
sleep(4)
print('Switching to peaceful color mode')
send_command(control_commands['color_peaceful'], devs)
sleep(6)
print('Turning off lighting')
send_command(control_commands['turn_off'], devs)
sleep(2)
print('Turning lighting on to static color slot 1 with brightness 9')
# The monitor doesn't require an explicit turn_on command. However, doing
#   turn_on will maintain the previous (pre-turn_off) color mode/state,
#   whereas this will always set it to the 1st static color.
send_command(control_commands['color1'], devs)
send_command(brightness_commands[9], devs)
print('All done, exiting')

for dev in devs:
    dev.close()
