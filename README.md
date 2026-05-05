# Robotframework-MobileWright

Robot Framework library for [MobileWright](https://github.com/mobile-next/mobilewright) — mobile test automation for iOS and Android.

Wraps the `mobilecli` HTTP JSON-RPC server so you can drive iOS / Android devices from `.robot` files.

## Compatibility

| | Version |
|---|---|
| Mobilewright (RF lib) | `0.1.0` |
| `mobilecli` server | `>= v0.3.69` |
| Python | `>= 3.9` |
| Robot Framework | `>= 6.0` |

The library follows its own SemVer cycle, independent of the upstream `mobilecli` version. Each release is tested against the version above.

## Setup

You need a running `mobilecli` server (it talks to the device via ADB or iOS instruments):

```bash
npm install -g mobilecli
mobilecli server start --listen localhost:12000 --cors -d
```

## Install

```bash
pip install robotframework-mobilewright
```

## Quick start

```robotframework
*** Settings ***
Library    Mobilewright    server_url=ws://localhost:12000/ws

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

Full keyword reference: <https://marketsquare.github.io/robotframework-mobilewright/>

Generate locally:

```bash
python -m robot.libdoc Mobilewright docs/index.html
```

## License

Apache 2.0
