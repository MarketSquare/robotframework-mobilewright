*** Settings ***
Library    Mobilewright    server_url=ws://localhost:9100    timeout=15s

Suite Setup       Connect To Device
Suite Teardown    Close All Connections

*** Test Cases ***
Connect And List Devices
    @{devices}=    List Devices
    Log    Found ${devices.__len__()} device(s)

Set And Restore Timeout
    ${old}=    Set MobileWright Timeout    20s
    Set MobileWright Timeout    ${old}
