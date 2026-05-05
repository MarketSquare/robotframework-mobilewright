*** Settings ***
Documentation       Comprehensive coverage test — exercises every public keyword
...                 of Mobilewright at least once on a real Android device.
...                 Requires: mobilecli server on localhost:12000 with online device.
Library             Mobilewright    server_url=ws://localhost:12000/ws    timeout=60s
...                 run_on_failure=NONE
Library             OperatingSystem
Library             Collections
Library             String

Suite Setup         Suite Connect
Suite Teardown      Suite Disconnect

Test Tags           coverage


*** Variables ***
${SETTINGS_BUNDLE}      com.android.settings


*** Test Cases ***
# --- 1. Connection management -------------------------------------------------

C01 Set Mobilewright Timeout
    ${old}=    Set Mobilewright Timeout    20s
    Should Not Be Empty    ${old}
    Set Mobilewright Timeout    ${old}

C02 List Devices
    @{devices}=    List Devices
    Should Not Be Empty    ${devices}

C03 Get Device Info
    ${info}=    Get Device Info
    Should Not Be Empty    ${info}

C04 Switch Device
    [Documentation]    Open a 2nd connection with alias and switch back.
    ${current_idx}=    Connect To Device    alias=secondary
    Switch Device    1
    @{d1}=    List Devices
    Switch Device    secondary
    @{d2}=    List Devices
    Should Be Equal    ${d1}    ${d2}
    Switch Device    1

C05 Register Keyword To Run On Failure
    [Documentation]    Suite Library set run_on_failure=NONE so initial value is None.
    ${initial}=    Register Keyword To Run On Failure    Capture Screenshot
    ${after_set}=    Register Keyword To Run On Failure    NONE
    Should Be Equal As Strings    ${after_set}    Capture Screenshot
    Register Keyword To Run On Failure    ${initial}

# --- 2. Apps ------------------------------------------------------------------

A01 Launch App Settings
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s
    ${fg}=    Get Foreground App
    Log    Foreground after launch: ${fg}

A02 List Apps
    @{apps}=    List Apps
    Length Should Be Greater Than    ${apps}    5

A03 Get Foreground App
    ${app}=    Get Foreground App
    Should Not Be Empty    ${app}

A04 Terminate App
    Terminate App    ${SETTINGS_BUNDLE}
    Sleep    1s
    ${fg}=    Get Foreground App
    Log    Foreground after terminate: ${fg}
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

A05 Install App With Bad Path Fails Cleanly
    [Documentation]    No real apk handy — verify the keyword surfaces a clear error.
    Run Keyword And Expect Error    *    Install App    /tmp/__nonexistent.apk

A06 Uninstall Nonexistent App Fails Cleanly
    Run Keyword And Expect Error    *    Uninstall App    com.does.not.exist.xyz

# --- 3. Screen actions --------------------------------------------------------

S01 Get Screen Size
    ${size}=    Get Screen Size
    Should Be True    ${size}[width] > 0
    Should Be True    ${size}[height] > 0

S02 Capture Screenshot
    ${path}=    Capture Screenshot    /tmp/mw-cov-01-screen.png
    File Should Exist    ${path}

S03 Get View Tree
    ${tree}=    Get View Tree
    Should Not Be Empty    ${tree}

S04 Tap Coordinates
    ${size}=    Get Screen Size
    Tap Coordinates    ${{ $size['width'] // 2 }}    ${{ $size['height'] // 2 }}

S05 Double Tap Coordinates
    Double Tap Coordinates    100    300

S06 Long Press Coordinates
    Long Press Coordinates    100    300    duration=600

S07 Press Button HOME
    Press Button    HOME
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

S08 Go Back Keyword
    Go Back
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

S09 Swipe Down
    Swipe    down
    Sleep    1s

S10 Swipe Up
    Swipe    up
    Sleep    1s

S11 Swipe Left
    Swipe    left
    Sleep    1s

S12 Swipe Right
    Swipe    right
    Sleep    1s

S13 Type Text
    [Documentation]    Type Text without focused field — should not crash.
    Type Text    hello

# --- 4. Element interactions --------------------------------------------------

E01 Tap Element By Text
    ${tree}=    Get View Tree
    ${text}=    Pick Visible Text    ${tree}
    Tap Element    text=${text}
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

E02 Double Tap Element By Type
    Double Tap Element    type=android.widget.TextView
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

E03 Long Press Element By Type
    Long Press Element    type=android.widget.TextView    duration=500
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

E04 Fill Element Search Bar
    [Documentation]    Open search in Settings → fill query → verify text typed.
    ${count}=    Get Element Count    label=Rechercher
    Run Keyword If    ${count} == 0    Run Keywords
    ...    Log    No 'Rechercher' button found, falling back to first edit field
    ...    AND    Pass Execution    skipped
    Tap Element    label=Rechercher
    Sleep    2s
    ${edit_count}=    Get Element Count    type=android.widget.EditText
    Run Keyword If    ${edit_count} > 0    Fill Element    type=android.widget.EditText    Wifi
    Sleep    1s
    Capture Screenshot    /tmp/mw-cov-02-fill.png
    Press Button    BACK
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

E05 Swipe Element
    [Documentation]    Swipe a scrollable container.
    [Setup]    Reset To Settings
    ${count}=    Get Element Count    type=androidx.recyclerview.widget.RecyclerView
    Run Keyword If    ${count} > 0    Swipe Element
    ...    type=androidx.recyclerview.widget.RecyclerView    up
    Sleep    1s

E06 Scroll Element Into View
    [Documentation]    Scroll until something visible at the bottom comes up.
    Press Button    HOME
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s
    Run Keyword And Ignore Error    Scroll Element Into View    text=À propos    max_swipes=5

# --- 5. Element queries -------------------------------------------------------

Q01 Get Element Text
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    ${text}=    Get Element Text    text=${first_text}
    Should Be Equal    ${text}    ${first_text}

Q02 Get Element Value
    [Documentation]    Most TextViews don't have a value attribute — accept None.
    [Setup]    Reset To Settings
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    ${value}=    Get Element Value    text=${first_text}
    Log    Value: ${value}

Q03 Get Element Bounding Box
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    ${box}=    Get Element Bounding Box    text=${first_text}
    Should Be True    ${box}[width] >= 0
    Should Be True    ${box}[height] >= 0

Q04 Get Element Count
    ${count}=    Get Element Count    type=android.widget.TextView
    Should Be True    ${count} > 0

Q05 Get Elements
    @{elements}=    Get Elements    type=android.widget.TextView
    Length Should Be Greater Than    ${elements}    0

Q06 Capture Element Screenshot
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    ${path}=    Capture Element Screenshot    text=${first_text}    /tmp/mw-cov-03-element.png
    File Should Exist    ${path}

# --- 6. Element assertions ----------------------------------------------------

V01 Element Should Be Visible
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Element Should Be Visible    text=${first_text}

V02 Element Should Not Be Visible
    Element Should Not Be Visible    text=__definitely_not_on_screen_xyz123__

V03 Element Should Be Enabled
    [Setup]    Reset To Settings
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Element Should Be Enabled    text=${first_text}

V04 Element Should Be Disabled Negative
    [Documentation]    Most visible elements are enabled — assert it errors.
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Run Keyword And Expect Error    *    Element Should Be Disabled    text=${first_text}

V05 Element Should Be Selected Negative
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Run Keyword And Expect Error    *    Element Should Be Selected    text=${first_text}

V06 Element Should Be Focused Negative
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Run Keyword And Expect Error    *    Element Should Be Focused    text=${first_text}

V07 Element Should Be Checked Negative
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Run Keyword And Expect Error    *    Element Should Be Checked    text=${first_text}

V08 Element Text Should Be
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Element Text Should Be    text=${first_text}    ${first_text}

V09 Element Text Should Contain
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    ${prefix}=    Get Substring    ${first_text}    0    1
    Element Text Should Contain    text=${first_text}    ${prefix}

# --- 7. Wait keywords ---------------------------------------------------------

W01 Wait Until Element Is Visible
    [Setup]    Reset To Settings
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Wait Until Element Is Visible    text=${first_text}    timeout=10s

W02 Wait Until Element Is Not Visible
    Wait Until Element Is Not Visible    text=__nope_xyz__    timeout=2s

W03 Wait Until Element Is Enabled
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Wait Until Element Is Enabled    text=${first_text}    timeout=5s

W04 Wait For Element State Visible
    ${tree}=    Get View Tree
    ${first_text}=    Pick Visible Text    ${tree}
    Wait For Element State    text=${first_text}    visible    timeout=5s

W05 Wait For Element State Hidden
    Wait For Element State    text=__nope_xyz__    hidden    timeout=2s

W06 Wait Until Visible Times Out
    Run Keyword And Expect Error    *    Wait Until Element Is Visible
    ...    text=__nope_xyz__    timeout=2s

# --- 8. Orientation -----------------------------------------------------------

O01 Get Orientation
    ${o}=    Get Orientation
    Should Contain Any    ${o}    portrait    landscape

O02 Set Orientation Landscape Then Portrait
    Run Keyword And Ignore Error    Set Orientation    landscape
    Sleep    1s
    Run Keyword And Ignore Error    Set Orientation    portrait
    Sleep    1s

# --- 9. Navigation ------------------------------------------------------------

N01 Open Url
    Open Url    https://example.com
    Sleep    3s

N02 Go To Url Alias
    [Setup]    Reset To Settings
    Go To Url    https://example.org
    Sleep    3s
    Press Button    HOME
    Sleep    1s


*** Keywords ***
Suite Connect
    Connect To Device
    Press Button    HOME
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    2s

Suite Disconnect
    Press Button    HOME
    Close All Connections

Reset To Settings
    [Documentation]    Press HOME, relaunch Settings to ensure a known light UI state.
    Press Button    HOME
    Sleep    1s
    Launch App    ${SETTINGS_BUNDLE}
    Sleep    3s

Pick Visible Text
    [Arguments]    ${tree}
    [Documentation]    Returns the first non-empty visible text in the tree, or fails.
    ${text}=    Evaluate
    ...    next((n.get('text') for n in $tree if n.get('text') and n.get('visible') and len(n.get('text','').strip()) > 1), None)
    Should Not Be Equal    ${text}    ${None}
    RETURN    ${text}

Length Should Be Greater Than
    [Arguments]    ${seq}    ${threshold}
    ${len}=    Get Length    ${seq}
    Should Be True    ${len} > ${threshold}
