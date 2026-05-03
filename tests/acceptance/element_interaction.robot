*** Settings ***
Library    Mobilewright    server_url=ws://localhost:9100    timeout=15s

Suite Setup       Connect To Device
Suite Teardown    Close All Connections

*** Variables ***
${BUNDLE_ID}    com.example.testapp

*** Test Cases ***
Tap Element By Text
    Launch App    ${BUNDLE_ID}
    Tap Element    text=Login
    [Teardown]    Terminate App    ${BUNDLE_ID}

Fill Input Field
    Launch App    ${BUNDLE_ID}
    Fill Element    testid=username-input    admin@test.com
    Fill Element    testid=password-input    password123
    [Teardown]    Terminate App    ${BUNDLE_ID}

Verify Element Text
    Launch App    ${BUNDLE_ID}
    Element Text Should Be    testid=title    Welcome
    Element Text Should Contain    testid=subtitle    Hello
    [Teardown]    Terminate App    ${BUNDLE_ID}

Assert Element Visibility
    Launch App    ${BUNDLE_ID}
    Element Should Be Visible    text=Login
    Element Should Not Be Visible    text=Dashboard
    [Teardown]    Terminate App    ${BUNDLE_ID}

Wait For Element
    Launch App    ${BUNDLE_ID}
    Tap Element    text=Login
    Wait Until Element Is Visible    text=Welcome    timeout=10s
    [Teardown]    Terminate App    ${BUNDLE_ID}

Get Element Count
    Launch App    ${BUNDLE_ID}
    ${count}=    Get Element Count    type=UIButton
    Log    Found ${count} buttons
    [Teardown]    Terminate App    ${BUNDLE_ID}

Capture Screenshot On Demand
    Launch App    ${BUNDLE_ID}
    Capture Screenshot
    [Teardown]    Terminate App    ${BUNDLE_ID}
