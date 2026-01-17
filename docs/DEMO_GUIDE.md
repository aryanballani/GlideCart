# Grocery Buddy - Demo Guide

## Hackathon Demo Strategy (3-5 minutes)

### Pre-Demo Setup (30 minutes before)

1. **Charge everything**
   - Raspberry Pi power bank: 100%
   - Motor battery: Fully charged
   - Android device: 100%

2. **Test run**
   - Verify camera works
   - Test motor response
   - Confirm WebSocket connection
   - Practice calibration

3. **Prepare demo space**
   - Clear 3m x 3m area minimum
   - Good lighting
   - Marker attached to volunteer
   - Emergency stop accessible

4. **Have backup plans**
   - Video recording of working demo
   - Slides showing architecture
   - Code walkthrough prepared

### Demo Script

#### 1. Opening (30 seconds)

**What to say:**
> "Meet Grocery Buddy - an autonomous shopping cart that follows you around the store. We built this to help people with mobility challenges shop independently."

**What to show:**
- Physical robot on display
- Point out key components (camera, Pi, motors)

#### 2. Problem Statement (30 seconds)

**What to say:**
> "For wheelchair users and elderly shoppers, pushing a heavy cart is challenging. Our robot uses computer vision to follow a colored marker, maintaining a safe distance while carrying groceries."

**What to show:**
- Show the marker on volunteer's back
- Gesture to demonstrate the problem

#### 3. Calibration Demo (30 seconds)

**What to do:**
1. Open Android app on your phone
2. Position marker in camera view
3. Press "CALIBRATE" button
4. Show "TARGET LOCKED" status

**What to say:**
> "Setup is simple - just press calibrate, and the robot locks onto your unique marker using OpenCV color detection."

#### 4. Live Following Demo (2 minutes)

**What to do:**
1. Press "START" in app
2. Volunteer walks forward slowly
3. Robot follows maintaining distance
4. Volunteer turns left/right
5. Robot adjusts direction
6. Show obstacle detection (optional)
7. Press "STOP"

**What to say while demoing:**
> "Watch as the robot maintains a consistent 1-meter following distance. The ultrasonic sensor detects obstacles and stops automatically. The Android app gives us real-time status and emergency stop control."

**Key points to highlight:**
- Smooth following
- Distance maintenance
- Turning response
- Safety features

#### 5. Technology Deep Dive (1 minute)

**What to say:**
> "We built this full-stack - a native Android app with Kotlin and Jetpack Compose, communicating via WebSocket to our Raspberry Pi. The Pi runs real-time computer vision with OpenCV, tracking the marker at 30fps. Motor control uses hardware PWM for smooth acceleration. Everything is modular and extensible."

**What to show:**
- Quick architecture diagram on phone/tablet
- Show the clean Android UI
- Mention the code structure

#### 6. Future Vision & Accessibility Impact (30 seconds)

**What to say:**
> "This is just the start. We're planning to add grocery item recognition using the Roboflow dataset, so the cart can help you find products. Imagine autonomous store navigation and automatic checkout. This isn't just convenient - it's independence for people who struggle with traditional shopping."

#### 7. Closing (15 seconds)

**What to say:**
> "Grocery Buddy - making shopping accessible for everyone. Thank you!"

**What to do:**
- Smile, make eye contact with judges
- Be ready for questions

## Handling Questions

### Technical Questions

**Q: "How does the color tracking work?"**
> "We convert the camera feed to HSV color space, which is more robust to lighting changes. During calibration, we sample the center region and set HSV bounds with tolerance. Then we use OpenCV's contour detection to find the largest matching blob and track its centroid."

**Q: "What if tracking is lost?"**
> "The robot immediately stops and enters search mode. We maintain a position history buffer for smoothing, so brief occlusions don't break tracking. The emergency stop is always available via the app."

**Q: "How do you handle multiple colored objects?"**
> "We filter by contour area - the target marker must be at least 15cm x 15cm. We also track the largest contour, assuming that's our target. For production, we'd add QR code verification."

**Q: "Battery life?"**
> "The Pi can run 6-8 hours on a 10000mAh power bank. Motors depend on usage but typically 2-3 hours on a 3S LiPo. We monitor battery levels in real-time via the app."

### Business/Impact Questions

**Q: "Who is this for?"**
> "Primarily wheelchair users and elderly shoppers who find pushing carts difficult. But also useful for anyone doing large shopping trips, parents with children, or people with temporary injuries."

**Q: "How would stores deploy this?"**
> "Stores could offer these at entrances like current shopping carts. The marker could be a store badge or attach to wheelchairs. We'd add store navigation and integrate with shopping lists."

**Q: "What about liability if it hits someone?"**
> "Safety is paramount - we have ultrasonic sensors, multiple emergency stops, speed limits, and operator oversight. In production, we'd add 360° sensors and compliance with ISO 13482 for personal care robots."

### Tricky Questions

**Q: "Isn't this just following a colored marker? That's basic."**
> "The core insight is that simple, robust solutions are often best. We prioritized reliability over complexity. Our full-stack integration - Android app, real-time computer vision, motor control, WebSocket communication - shows engineering breadth. Plus, we have a clear path to add item recognition and navigation."

**Q: "Why not use GPS/RFID/Bluetooth?"**
> "GPS doesn't work indoors with sub-meter accuracy. RFID/Bluetooth require infrastructure installation. Computer vision is infrastructure-free and works immediately. It's also extensible - the same camera enables item recognition."

**Q: "This already exists, right?"**
> "Commercial solutions like Caper Cart exist but cost $5000+ per unit and require store infrastructure. We built a $200 prototype in 36 hours that works anywhere. Our open-source approach makes it accessible."

## Demo Checklist

### The Night Before
- [ ] Charge all batteries to 100%
- [ ] Test complete system
- [ ] Print marker (backup)
- [ ] Prepare slides (backup)
- [ ] Record working demo (backup)
- [ ] Pack tools (screwdrivers, tape, etc.)

### 30 Minutes Before
- [ ] Set up demo space
- [ ] Power on Raspberry Pi
- [ ] Connect Android app
- [ ] Test calibration
- [ ] Do practice run
- [ ] Identify volunteer

### Right Before Judges Arrive
- [ ] Fresh calibration
- [ ] App showing "CONNECTED"
- [ ] Motors responsive
- [ ] Marker visible and secure
- [ ] Emergency stop accessible

### During Demo
- [ ] Smile and make eye contact
- [ ] Speak clearly and enthusiastically
- [ ] Show don't tell (let robot demo itself)
- [ ] Highlight technical complexity casually
- [ ] Emphasize accessibility impact
- [ ] Be ready to hit emergency stop
- [ ] Have fun!

## What Makes a Winning Demo

1. **It works reliably** - Practice until it's smooth
2. **Clear problem/solution** - Judges understand immediately
3. **Technical depth** - Show you know your stuff
4. **Social impact** - Accessibility angle is compelling
5. **Polish** - Clean UI, smooth operation, clear presentation
6. **Passion** - Show you care about the problem

## Backup Plans

### If robot won't move
- Show video of working demo
- Walk through code and architecture
- Emphasize computer vision (show camera feed)
- Discuss challenges and solutions

### If connection fails
- Use video demo
- Show app functionality offline
- Explain system architecture
- Code walkthrough on laptop

### If judges seem unimpressed
- Pivot to technical depth
- Show clean code architecture
- Discuss scalability
- Highlight learning journey

## Victory Conditions

You'll know the demo went well if judges:
- Smile and seem engaged
- Ask follow-up technical questions
- Want to try it themselves
- Discuss future applications
- Take photos/videos

## Remember

- **Confidence**: You built something awesome
- **Preparation**: Practice makes perfect
- **Passion**: Show you care
- **Flexibility**: Adapt to judge interests
- **Fun**: Enjoy the moment!

Good luck! You've got this! 🚀🛒
