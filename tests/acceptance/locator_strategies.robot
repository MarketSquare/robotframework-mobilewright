*** Settings ***
Library    Mobilewright    server_url=ws://localhost:9100    timeout=15s

Suite Setup       Connect To Device
Suite Teardown    Close All Connections

*** Variables ***
${BUNDLE_ID}    com.example.testapp

*** Test Cases ***
Find By Label
    Launch App    ${BUNDLE_ID}
    Tap Element    label=Submit Button
    [Teardown]    Terminate App    ${BUNDLE_ID}

Find By TestId
    Launch App    ${BUNDLE_ID}
    ${text}=    Get Element Text    testid=header-title
    Log    Header title: ${text}
    [Teardown]    Terminate App    ${BUNDLE_ID}

Find By Type
    Launch App    ${BUNDLE_ID}
    ${count}=    Get Element Count    type=UITextField
    Log    Found ${count} text fields
    [Teardown]    Terminate App    ${BUNDLE_ID}

Find By Role
    Launch App    ${BUNDLE_ID}
    Tap Element    role=button
    [Teardown]    Terminate App    ${BUNDLE_ID}

Find By Placeholder
    Launch App    ${BUNDLE_ID}
    Fill Element    placeholder=Enter email    user@example.com
    [Teardown]    Terminate App    ${BUNDLE_ID}

Chained Locator With Separator
    Launch App    ${BUNDLE_ID}
    Tap Element    type=ListView >> text=Settings
    Wait Until Element Is Visible    text=Preferences
    [Teardown]    Terminate App    ${BUNDLE_ID}

Index Selector First
    Launch App    ${BUNDLE_ID}
    Tap Element    type=UIButton    index=first
    [Teardown]    Terminate App    ${BUNDLE_ID}

Index Selector Last
    Launch App    ${BUNDLE_ID}
    Tap Element    type=UIButton    index=last
    [Teardown]    Terminate App    ${BUNDLE_ID}

Index Selector Numeric
    Launch App    ${BUNDLE_ID}
    Tap Element    type=UIButton    index=1
    [Teardown]    Terminate App    ${BUNDLE_ID}
