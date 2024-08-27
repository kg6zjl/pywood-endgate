Our scouting troop in TrailLifeUSA needs a way to identify which Pinewood Derby car place first and second. We run two brackets, one for first place and one for second. Our current track is a 4 lane with manually operated lever gate for release.

I decided that from a KISS standpoint, I don't care about timing the cars. Could be a future state, but for this iteration it doesn't matter. We really only care about the order that the cars reach the end gate.

This is my first time ever working at an PIO/hardware level, so feedback is appreciated. I'm learning along the way!

# Initial Design
- Micropython as the language
- Waveshare RP2040 Plus as the MCU
- 4 digit 7-segment with driver for displaying the order of the lanes as they place (1st to 4th place, left to right)
- A momentary reset button to trigger a display reset
- Light Dependent Resistors (Digital Module LM393) under the track, existing light source in endgate as primary light source


# Setup
- use https://github.com/mcauser/micropython-tm1637 for 4-digit 7-segment display


# Future State/Improvements/Ideas
- Add duplicate display at start gate so that bracket manager can see results on stage
- Add a microswitch at the start gate and add timing functionality
- Print race slips for winners with times
- Add solenoid for automated start gate
- A camera/photo of the winner would be fun, especially if we setup a projector
- Automated bracket tracking?
- IR Break Beam sensors for end gate (introduces more wiring, but same amount of programatic complexity I think)
