# Robotframework-MobileWright

Robot Framework library for [MobileWright](https://github.com/mobile-next/mobilewright) — mobile test automation for iOS and Android.

Wraps the MobileWright `mobilecli` WebSocket JSON-RPC protocol so you can drive devices from `.robot` files.

## Compatibility

| | Version |
|---|---|
| Mobilewright (RF lib) | `0.1.0` |
| MobileWright server | `>= v0.0.30` |
| Python | `>= 3.9` |
| Robot Framework | `>= 6.0` |

The library follows its own SemVer cycle, independent of MobileWright's version. Each release is tested against the MobileWright version listed above.

## Install

```bash
pip install robotframework-mobilewright
```

## Quick start

```robotframework
*** Settings ***
Library    Mobilewright    server_url=ws://localhost:9100

Suite Setup       Connect To Device
Suite Teardown    Close All Connections

*** Test Cases ***
Login
    Launch App    com.example.myapp
    Fill Element    testid=username    admin@test.com
    Fill Element    testid=password    secret
    Tap Element    label=Submit
    Wait Until Element Is Visible    text=Welcome    timeout=10s
```

## Locator syntax

| Strategy | Example |
|---|---|
| `label=` | `label=Submit` |
| `testid=` | `testid=login-btn` |
| `text=` | `text=Hello World` |
| `type=` | `type=UIButton` |
| `role=` | `role=button` |
| `placeholder=` | `placeholder=Search` |

Chain with `>>`: `type=ListView >> text=Item 1`

Index selector: `index=first` (default) / `index=last` / `index=N`

## Docs

Full keyword reference: [docs/Mobilewright.html](docs/Mobilewright.html)

Generate locally:

```bash
python -m robot.libdoc Mobilewright docs/Mobilewright.html
```

## License

Apache 2.0
