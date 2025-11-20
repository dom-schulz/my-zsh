# Auto-close Entra ID Auth Tabs in Chrome (macOS)

For azure CLI login and DBeaver auth

## 1. Create the AppleScript

```bash
mkdir -p ~/Scripts

cat <<'EOF' > ~/Scripts/close_azure_auth_tabs.applescript
-- Close Chrome tabs that look like DBeaver / Entra ID / Azure CLI localhost callbacks
tell application "Google Chrome"
    if (count of windows) is 0 then return

    repeat with w in windows
        set tabList to tabs of w
        repeat with t in tabList
            set theURL to URL of t

            -- Only match http://localhost:xxxxx...
            if theURL starts with "http://localhost:" then
                -- Read the body text and title of the page
                set bodyText to execute t javascript "document.body.innerText"
                set theTitle to execute t javascript "document.title"

                if bodyText contains "Authentication complete. You can close the browser and return to the application." ¬
                    or bodyText contains "You have logged into Microsoft Azure!" ¬
                    or bodyText contains "You can close this window, or we will redirect you to the Azure CLI documentation" ¬
                    or theTitle contains "Login successfully" then
                    close t
                end if
            end if
        end repeat
    end repeat
end tell
EOF
```

### Test the Script

```bash
osascript ~/Scripts/close_azure_auth_tabs.applescript
```
(May have to allow JavaScript automations in Google Chrome: View > Developer > Allow JavaScript from Apple Events)


## 2. Create the LaunchAgent (run every 10 seconds)

```bash
mkdir -p ~/Library/LaunchAgents

cat <<EOF > ~/Library/LaunchAgents/com.user.close-azure-auth-tabs.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.user.close-azure-auth-tabs</string>

  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/osascript</string>
    <string>$HOME/Scripts/close_azure_auth_tabs.applescript</string>
  </array>

  <!-- Run every 5 seconds -->
  <key>StartInterval</key>
  <integer>5</integer>

  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
EOF
```

### Load the LaunchAgent

```bash
launchctl load ~/Library/LaunchAgents/com.user.close-azure-auth-tabs.plist
```

### 3. Manage LaunchAgent

Unload/stop
```bash 
launchctl unload ~/Library/LaunchAgents/com.user.close-azure-auth-tabs.plist
```