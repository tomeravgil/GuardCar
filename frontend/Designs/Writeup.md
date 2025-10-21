# GuardCar Frontend Dashboard Write-Up

## Overview
The GuardCar frontend dashboard is designed to provide clear and usable web-based monitoring, playback, and notification features. Since the app will run on a server with no local display, the focus is on accessibility, clarity, and ease of use for users managing security events remotely.

## UI Research
- Reviewed Tesla Sentry Mode and similar security dashboards to understand common patterns and effective layouts.  
- Identified that users need quick access to live monitoring, playback controls, and settings for efficient system management.

## Core UI Components
1. **Live Monitoring Indicator**  
   Displays the current state of cameras and highlights suspicious activity in real time.
2. **Playback Controls**  
   Allows users to review recorded incidents with intuitive navigation (play, pause, skip, timeline view).
3. **Settings Panel**  
   Enables configuration of thresholds, alert preferences, and user settings, ensuring customization for each user.

## Wireframes & User Flows
- **Login**: Simple login for MVP access; optional additional authentication for security.  
- **Home/Landing Page**: Provides an overview and navigation to key dashboard sections.  
- **Real-Time Monitoring Screen**: Displays active cameras and live alerts.  
- **Playback Screen**: Lists saved videos and allows users to review recordings.  
- **Settings Panel**: Lets users adjust alert thresholds, notification preferences, and other website controls.

**User Flow Example:**  
1. Suspicious event detected → alert sent.  
2. User clicks alert link → navigates to live camera view.  
3. Footage is automatically saved and available in the playback interface.

---

*This document establishes the design direction and usability goals guiding the frontend implementation.*