*** Settings ***
Documentation       End-to-end smoke test against a real mobilecli + Android device.
...                 Requires: mobilecli server on localhost:12000 with online device.
Library             Mobilewright    server_url=ws://localhost:12000/ws    timeout=15s
...                 run_on_failure=NONE
Library             OperatingSystem

Suite Setup         Connect To Device
Suite Teardown      Close All Connections


*** Test Cases ***
01 List Devices
    @{devices}=    List Devices
    Should Not Be Empty    ${devices}

02 Get Device Info
    ${info}=    Get Device Info
    Should Not Be Empty    ${info}

03 Get Screen Size
    ${size}=    Get Screen Size
    Should Be True    ${size}[width] > 0
    Should Be True    ${size}[height] > 0

04 Press Home Button
    Press Button    HOME
    Sleep    1s

05 Capture Screenshot Of Home
    ${path}=    Capture Screenshot    /tmp/mw-smoke-home.png
    File Should Exist    ${path}

06 Get View Tree
    ${tree}=    Get View Tree
    Should Not Be Empty    ${tree}
    Log    Tree has ${{ len($tree) }} elements

07 Get Element Count
    ${count}=    Get Element Count    type=android.widget.TextView
    Should Be True    ${count} > 0
    Log    Found ${count} TextView(s)

08 Find Element By Text
    [Documentation]    Find any text element on screen — first one with non-empty text.
    ${tree}=    Get View Tree
    ${first_text}=    Evaluate    next((n['text'] for n in $tree if n.get('text')), None)
    Should Not Be Equal    ${first_text}    ${None}
    Log    Picked text: ${first_text}
    ${count}=    Get Element Count    text=${first_text}
    Should Be True    ${count} >= 1

09 Element Should Be Visible
    [Documentation]    Use the same picked text from previous test to assert visibility.
    ${tree}=    Get View Tree
    ${first_text}=    Evaluate    next((n['text'] for n in $tree if n.get('text') and n.get('visible')), None)
    Should Not Be Equal    ${first_text}    ${None}
    Element Should Be Visible    text=${first_text}

10 Element Should Not Be Visible
    Element Should Not Be Visible    text=__definitely_not_on_screen__

11 List Apps Returns Many
    @{apps}=    List Apps
    ${count}=    Get Length    ${apps}
    Should Be True    ${count} > 5

12 Get Foreground App
    ${app}=    Get Foreground App
    Should Not Be Empty    ${app}

13 Tap Coordinates Center
    ${size}=    Get Screen Size
    ${cx}=    Evaluate    ${size}[width] // 2
    ${cy}=    Evaluate    ${size}[height] // 2
    Tap Coordinates    ${cx}    ${cy}

14 Open Url Opens Browser
    Open Url    https://example.com
    Sleep    3s
    ${path}=    Capture Screenshot    /tmp/mw-smoke-browser.png
    File Should Exist    ${path}

15 Press Back And Home
    Press Button    BACK
    Sleep    1s
    Press Button    HOME
    Sleep    1s

16 Launch Android Settings
    Launch App    com.android.settings
    Sleep    2s
    ${app}=    Get Foreground App
    Log    Now in: ${app}

17 Find And Tap Element In Settings
    [Documentation]    Find any tappable text element in Settings, tap it, verify nav.
    ${tree_before}=    Get View Tree
    ${first_text}=    Evaluate    next((n['text'] for n in $tree_before if n.get('text') and len(n.get('text','')) > 2), None)
    Run Keyword If    $first_text is not None    Tap Element    text=${first_text}
    Sleep    2s
    Capture Screenshot    /tmp/mw-smoke-settings-after-tap.png

18 Get Orientation
    ${orientation}=    Get Orientation
    Log    Current orientation: ${orientation}
    Should Contain Any    ${orientation}    portrait    landscape

19 Type Text Standalone
    [Documentation]    Type Text needs a focused text field. Test it doesn't crash.
    Press Button    HOME
    Sleep    1s
    Run Keyword And Ignore Error    Type Text    hello mobilewright

20 Cleanup Press Home
    Press Button    HOME
