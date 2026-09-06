This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
.gitignore
cdm.cpp
cdm.h
cmd.cpp
cmd.h
HF2020_XFS_ATM_Jackpotting_Alexandre_Beaulieu.pdf
LICENSE
main.cpp
output.txt
README.md
xfsapi.cpp
xfsapi.h
xfsc.sln
xfsc.vcxproj
xfsc.vcxproj.filters
xfscdm.h
````

# Files

## File: .gitignore
````
# Prerequisites
*.d

# Object files
*.o
*.ko
*.obj
*.elf

# Linker output
*.ilk
*.map
*.exp

# Precompiled Headers
*.gch
*.pch

# Libraries
*.lib
*.a
*.la
*.lo

# Shared objects (inc. Windows DLLs)
*.dll
*.so
*.so.*
*.dylib

# Executables
*.exe
*.out
*.app
*.i*86
*.x86_64
*.hex

# Debug files
*.dSYM/
*.su
*.idb
*.pdb

# Kernel Module Compile Results
*.mod*
*.cmd
.tmp_versions/
modules.order
Module.symvers
Mkfile.old
dkms.conf
````

## File: cdm.cpp
````cpp
#include "cmd.h"
#include "cdm.h"

const char* cdmtype2str(WORD type)
{
    switch (type)
    {
    case WFS_CDM_TELLERBILL:      return "Bills (Teller)";
    case WFS_CDM_SELFSERVICEBILL: return "Bills (Self-Serve)";
    case WFS_CDM_TELLERCOIN:      return "Coins (Teller)";
    case WFS_CDM_SELFSERVICECOIN: return "Coins (Self-Serve)";
    }
    return "Unknown";
}

const char* pos2str(DWORD pos) {
    switch (pos) {
    case WFS_CDM_POSLEFT: return "LEFT";
    case WFS_CDM_POSRIGHT: return "RIGHT";
    case WFS_CDM_POSFRONT: return "FRONT";
    case WFS_CDM_POSREAR: return "REAR";
    case WFS_CDM_POSTOP: return "TOP";
    case WFS_CDM_POSBOTTOM: return "BOTTOM";
    case WFS_CDM_POSCENTER: return "CENTER";
    default: return "UNKNOWN";
    }
}

// CONTROL CASH DISPENSER (WFS_CDM_DISPENSE)
// ------------------------------------------------------
// The input parameters are amount, currency and mix number. In this case the amount is
// denominatedand, if this succeeds, the items are dispensed.
// Denominations are significantly more complex to use because they require to know
// the bill numbers from each cash.
HRESULT cdm_dispense(int argc, char** argv)
{
    if (argc < 2 || argc > 4) return WFSC_BAD_CMD;
    Service * svc = get_service(atoi(argv[0]));
    if (!svc) return WFSC_BAD_CMD;
    LPWFSRESULT res; HRESULT out;

    DWORD  amt = atoi(argv[1]);
    USHORT mix = (argc == 4) ? atoi(argv[3]) : 1;
    char* cur = (argc >= 3) ? argv[2] : (char*)"USD";
    if (strlen(cur) < 3) return WFSC_BAD_CMD;

    lock(svc);
    WFSCDMDENOMINATION denom;
    denom.cCurrencyID[0] = cur[0];
    denom.cCurrencyID[1] = cur[1];
    denom.cCurrencyID[2] = cur[2];

    denom.lpulValues = NULL; // Let the ATM figure out the actual denomination.
    denom.usCount = 0;

    denom.ulAmount = amt; // Amount to dispense.
    denom.ulCashBox = 0;  // Unused.

    WFSCDMDISPENSE cmdDispense;
    cmdDispense.bPresent = TRUE;              // Present money to customer.
    cmdDispense.fwPosition = WFS_CDM_POSNULL; // Default output position.
    cmdDispense.usMixNumber = mix;
    cmdDispense.lpDenomination = &denom;
    cmdDispense.usTellerID = 0; // UNUSED
    out = WFSExecute(svc->handle, WFS_CMD_CDM_DISPENSE, &cmdDispense, WFS_INDEFINITE_WAIT, &res);
    printf("[+] Dispensing %d %s from %s...\n", amt, cur, svc->name.c_str());
    check(out);
    unlock(svc);
    return WFS_SUCCESS;
}

// Dump cash dispenser capabilities
HRESULT cdm_caps(int argc, char** argv)
{
    if (argc != 1) return WFSC_BAD_CMD;
    Service * svc = get_service(atoi(argv[0]));
    if (!svc) return WFSC_BAD_CMD;
    LPWFSRESULT res; HRESULT out;

    out = WFSGetInfo(svc->handle, WFS_INF_CDM_CAPABILITIES, /*IN*/ NULL, WFS_INDEFINITE_WAIT, /*OUT*/ &res);
    check(out);
    printf("[+] Capabilities for %s\n", svc->name.c_str());
    if (out == WFS_SUCCESS)
    {
        LPWFSCDMCAPS caps = (LPWFSCDMCAPS)res->lpBuffer;
        printf("    bCashBox: %d\n", caps->bCashBox);
        printf("    bCompound: %d\n", caps->bCompound);
        printf("    bIntermediateStacker: %d\n", caps->bIntermediateStacker);
        printf("    bItemsTakenSensor: %d\n", caps->bItemsTakenSensor);
        printf("    bPowerSaveControl: %d\n", caps->bPowerSaveControl);
        printf("    bPrepareDispense: %d\n", caps->bPrepareDispense);
        printf("    bSafedoor: %d\n", caps->bSafeDoor);
        printf("    bShutter: %d\n", caps->bShutter);
        printf("    bShutterControl: %d\n", caps->bShutterControl);
        printf("    fwExchangeType: %d\n", caps->fwExchangeType);
        printf("    fwType: %s\n", cdmtype2str(caps->fwType));
        printf("    Max Dispense: %d\n", caps->wMaxDispenseItems);
        printf("    Extra: %s\n", caps->lpszExtra);
        WORD pos = caps->fwPositions; // Specifies the CDM output positions.
        printf("    Positions:\n");
        printf("    ----------\n");
        if (pos & WFS_CDM_POSLEFT)   printf("      - LEFT\n");
        if (pos & WFS_CDM_POSRIGHT)  printf("      - RIGHT\n");
        if (pos & WFS_CDM_POSTOP)    printf("      - TOP\n");
        if (pos & WFS_CDM_POSBOTTOM) printf("      - BOTTOM\n");
        if (pos & WFS_CDM_POSFRONT)  printf("      - FRONT\n");
        if (pos & WFS_CDM_POSREAR)   printf("      - REAR\n");
        if (pos & WFS_CDM_POSCENTER) printf("      - CENTER\n");
    }

    if (res) WFSFreeResult(res);
    return WFS_SUCCESS;
}

// Dump cash dispenser mix algorithms
HRESULT cdm_mixes(int argc, char** argv)
{
    if (argc != 1) return WFSC_BAD_CMD;
    Service * svc = get_service(atoi(argv[0]));
    if (!svc) return WFSC_BAD_CMD;
    LPWFSRESULT res; HRESULT out;

    out = WFSGetInfo(svc->handle, WFS_INF_CDM_MIX_TYPES, NULL, WFS_INDEFINITE_WAIT, &res);

    printf("[+] Mixing Algorithms for %s\n", svc->name.c_str());
    check(out);
    if (res) {
        LPWFSCDMMIXTYPE* mixes = (LPWFSCDMMIXTYPE*)res->lpBuffer;
        while (*mixes) {
            LPWFSCDMMIXTYPE mix = *mixes;
            printf("    %02d - %02d - %s\n", mix->usMixNumber, mix->usMixType, mix->lpszName);
            mixes++;
        }
        WFSFreeResult(res);
    }
    return WFS_SUCCESS;
}

// Dump cash dispenser info
HRESULT cdm_info(int argc, char** argv)
{
    if (argc != 1) return WFSC_BAD_CMD;
    Service * svc = get_service(atoi(argv[0]));
    if (!svc) return WFSC_BAD_CMD;
    LPWFSRESULT res; HRESULT out;

    out = WFSGetInfo(svc->handle, WFS_INF_CDM_STATUS, NULL, WFS_INDEFINITE_WAIT, &res);

    printf("[+] Dispenser Satus for %s:\n", svc->name.c_str());
    check(out);
    if (res) {
        LPWFSCDMSTATUS s = (LPWFSCDMSTATUS)res->lpBuffer;
        printf("    Device:    %d\n", s->fwDevice);
        printf("    Dispenser: %d\n", s->fwDispenser);
        printf("    Stacker:   %d\n", s->fwIntermediateStacker);
        printf("    Safedoor:  %d\n", s->fwSafeDoor);
        printf("    Position:  %d\n", s->wDevicePosition);
        printf("    Output Positions:\n");
        printf("    -----------------\n");
        LPWFSCDMOUTPOS* pos = s->lppPositions;
        auto i = 0;
        while (*pos) {
            LPWFSCDMOUTPOS p = *pos;
            printf("    %02d - %s (status=0x%x) Shutter=0x%x  Transport=0x%x (status=%d) \n", i, pos2str(p->fwPosition), p->fwPositionStatus, p->fwShutter, p->fwTransport, p->fwTransportStatus);
            pos++; ++i;
        }
    }

    out = WFSGetInfo(svc->handle, WFS_INF_CDM_CASH_UNIT_INFO, NULL, WFS_INDEFINITE_WAIT, &res);
    printf("[+] Cash Units for %s:\n", svc->name.c_str());
    check(out);
    if (res) {
        LPWFSCDMCUINFO info = (LPWFSCDMCUINFO)res->lpBuffer;
        LPWFSCDMCASHUNIT* units = (LPWFSCDMCASHUNIT*)info->lppList;
        printf("[*] Found %02d cash units (may not reflect physical units)\n", info->usCount);
        for (WORD i = 0; i < info->usCount; ++i) {
            LPWFSCDMCASHUNIT unit = units[i];
            printf("    %02d: %5s - (%c%c%c) - %s\n", i, (char*)unit->cUnitID, unit->cCurrencyID[0], unit->cCurrencyID[1], unit->cCurrencyID[2], unit->lpszCashUnitName);
            printf("    Type=%d Value=%d\n", unit->usType, unit->ulValues);
            printf("    Min=%08d Max=%08d Cur=%08d\n", unit->ulMinimum, unit->ulMaximum, unit->ulCount);
            printf("    %s\n", unit->bAppLock ? "LOCKED" : "USABLE");
        }

        WFSFreeResult(res);
    }
    return out;
}

// Register subcommands for parser
static cmd_t commands[] = {
    { "info",     "Queries information about the cash dispenser.\nUsage: cdm info <id>", cdm_info, NULL },
    { "caps",     "Queries capabilities of the cash dispenser.\nUsage: cdm caps <id>", cdm_caps, NULL },
    { "mix",      "Displays supported mixing algorithms\nUsage: cdm mix <id>", cdm_mixes, NULL },
    { "dispense", "Dispense cash\nUsage: cdm dispense <id> <amount> [currency=USD] [mix=1]", cdm_dispense, NULL },
};

// cdm subcommand implementation
HRESULT cdm_dispatch(int argc, char** argv) {
    if (!argc)
    {
        printf("Cash Dispenser Module Commands: info | caps | dispense\n");
        return WFS_SUCCESS;
    }
    dispatch(commands, CMD_COUNT(commands), argc, argv);

    char* cmd = argv[0];

    return WFS_SUCCESS;
}
````

## File: cdm.h
````c
#pragma once

#include "xfsapi.h"
#include "xfscdm.h"

HRESULT cdm_dispatch(int argc, char** argv);
````

## File: cmd.cpp
````cpp
#include <map>
#include <vector>

#include <windows.h>
#include <winreg.h>

#include "xfscdm.h"
#include "xfsapi.h"
#include "cmd.h"
#include "cdm.h"

#define HKEY_LOGICAL_SERVICES ".DEFAULT\\XFS\\LOGICAL_SERVICES"

std::map<HSERVICE, Service*> services;


Service* get_service(HSERVICE id)
{
    if (!services.count(id)) return NULL;
    return services[id];
}

void del_service(Service* svc)
{
    if (!svc) return;
    services.erase(svc->handle);
    WFSClose(svc->handle);
    delete svc;
}

HRESULT open_svc(int argc, char** argv)
{
    if (argc != 1) return WFSC_BAD_CMD;
    WFSVERSION svcver, spiver;
    HSERVICE svc;
    char* service = argv[0];
    printf("[+] Opening Service: %s\n", service);

    HRESULT out = WFSOpen(service, WFS_DEFAULT_HAPP, (char*)APPID, /*traceLevel=*/0, WFS_INDEFINITE_WAIT, 3, &svcver, &spiver, &svc);
    check(out);

    if (out == WFS_SUCCESS)
    {
        services[svc] = new Service(std::string(service), svc);
        printf("[*] Service:  %s\n", svcver.szDescription);
        printf("[*] Provider: %s\n", spiver.szDescription);
        printf("[+] %s assigned to handle %d\n", service, svc);
    }
    return out;
}

HRESULT close_svc(int argc, char** argv)
{
    if (argc != 1) return WFSC_BAD_CMD;
    HSERVICE id = atoi(argv[0]);
    Service * svc = get_service(id);
    if (!svc)
    {
        printf("[-] Service %d is not open.\n", id);
        return WFS_SUCCESS;
    }
    del_service(svc);
    return WFS_SUCCESS;
}

HRESULT do_quit(int argc, char** argv)
{
    printf("[+] Exiting...\n");
    // Close all services.
    for (auto& kv : services)
    {
        printf("    Closing %s\n", kv.second->name.c_str());
        WFSClose(kv.second->handle);
        delete kv.second;
    }
    services.clear();

    WFSCleanUp();
    exit(0);
    return WFS_SUCCESS;
}

HRESULT list_svc(int argc, char** argv)
{
    for (auto& kv : services) printf("%5d - %s\n", kv.first, kv.second->name.c_str());
    return WFS_SUCCESS;
}

HRESULT scan_svc(int argc, char** argv)
{
    // All services are configured in the registry at HKU\.DEFAULT\XFS\LOGICAL_SERVICES
    // or at a given user's SID. Currently scanning only supports DEFAULT. It could be
    // enhanced to scan all SIDs or filter on a specific SID.
    HKEY xfs;
    LRESULT res = RegOpenKeyEx(HKEY_USERS, HKEY_LOGICAL_SERVICES, NULL, KEY_READ, &xfs);

    if (res != ERROR_SUCCESS)
    {
        printf("[-] Code %d - No logical services found. Try with a SID?\n", res);
        return WFS_SUCCESS;
    }

    char name[100], clss[5];
    DWORD len = 100, type, class_len;

    while (RegEnumKeyEx(xfs, 0, (char*)& name, &len, NULL, NULL, NULL, NULL) != ERROR_NO_MORE_ITEMS)
    {
        res = RegGetValue(xfs, name, "class", RRF_RT_REG_SZ, &type, &clss, &class_len);
        if (res != ERROR_SUCCESS) continue;
        printf("%s - %s\n", clss, name);
    }

    return WFS_SUCCESS;
}

static cmd_t commands[] = {
    { "open",     "Establish a connection with a service provider.\nUsage: open <logical_name>", open_svc, NULL },
    { "close",    "Close an existing service connection.\nUsage: close <id>", close_svc, NULL },
    { "list",     "List active services.", list_svc, NULL },
    { "scan",     "Scans the computer for XFS services.", scan_svc, NULL},
    { "help",     "Print help about a function.\nUsage: help [function]", NULL, NULL},
    // ----
    { "cdm",      "Control a cash dispenser module.", cdm_dispatch, NULL},
    { "quit",     "Disconnect from the XFS manager.", do_quit, NULL },
    { "exit",     "See quit.", do_quit, NULL },
};


// Generic help printing.
// This is not fully implemented yet.
void help(cmd_t * cmds, int count, char* cmd)
{
    if (cmd == NULL) printf("Supported Commands\n------------------\nTODO\n");
    /*for (int i = 0; i < sizeof(cmds) / sizeof(cmd_t); ++i)
    {
        if (cmd == NULL) printf("%30s%s\n", cmds[i].name, )
    }*/
}

// Command parser and dispatch
char** parse(char* line, int* argc) {
    char* context;
    std::vector<char*> argv;
    char* tok = strtok_s(line, " ", &context);
    while (tok) {
        int len = strlen(tok) + 1;
        char* arg = (char*)malloc(sizeof(char) * len);
        strcpy_s(arg, len, tok);
        argv.push_back(arg);
        tok = strtok_s(NULL, " ", &context);
    }
    *argc = argv.size();
    char** args = (char**)malloc(sizeof(char*) * argv.size());
    memcpy(args, argv.data(), argv.size() * sizeof(char*));
    return args;
}

void free_args(int argc, char** args) {
    for (int i = 0; i < argc; ++i) free(args[i]);
    free(args);
}

// Check for error and print to terminal if necessary
void check(HRESULT res)
{
    if (res == WFS_SUCCESS) return;
    printf("[!] Error %d: ", res);

    switch (res)
    {
    case WFS_ERR_ALREADY_STARTED: /* -1) */
        printf("Already Started");
        break;
    case WFS_ERR_API_VER_TOO_HIGH: /* -2) */
        printf("Version too high");
        break;
    case WFS_ERR_API_VER_TOO_LOW: /* -3) */
        printf("Version too low");
        break;
    case WFS_ERR_CANCELED: /* -4) */
        printf("Canceled");
        break;
    case WFS_ERR_CFG_INVALID_HKEY: /* -5) */ break;
    case WFS_ERR_CFG_INVALID_NAME: /* -6) */ break;
    case WFS_ERR_CFG_INVALID_SUBKEY: /* -7) */ break;
    case WFS_ERR_CFG_INVALID_VALUE: /* -8) */ break;
    case WFS_ERR_CFG_KEY_NOT_EMPTY: /* -9) */ break;
    case WFS_ERR_CFG_NAME_TOO_LONG: /* -10) */ break;
    case WFS_ERR_CFG_NO_MORE_ITEMS: /* -11) */ break;
    case WFS_ERR_CFG_VALUE_TOO_LONG: /* -12) */ break;
    case WFS_ERR_DEV_NOT_READY: /* -13) */
        printf("Device Not Ready");
        break;
    case WFS_ERR_HARDWARE_ERROR: /* -14) */ break;
    case WFS_ERR_INTERNAL_ERROR: /* -15) */
        printf("Internal Error");
        break;
    case WFS_ERR_INVALID_ADDRESS: /* -16) */ break;
    case WFS_ERR_INVALID_APP_HANDLE: /* -17) */ break;
    case WFS_ERR_INVALID_BUFFER: /* -18) */ break;
    case WFS_ERR_INVALID_CATEGORY: /* -19) */ break;
    case WFS_ERR_INVALID_COMMAND: /* -20) */ break;
    case WFS_ERR_INVALID_EVENT_CLASS: /* -21) */ break;
    case WFS_ERR_INVALID_HSERVICE: /* -22) */
        printf("Invalid service handle.");
        break;
    case WFS_ERR_INVALID_HPROVIDER: /* -23) */ break;
    case WFS_ERR_INVALID_HWND: /* -24) */ break;
    case WFS_ERR_INVALID_HWNDREG: /* -25) */ break;
    case WFS_ERR_INVALID_POINTER: /* -26) */ break;
    case WFS_ERR_INVALID_REQ_ID: /* -27) */ break;
    case WFS_ERR_INVALID_RESULT: /* -28) */ break;
    case WFS_ERR_INVALID_SERVPROV: /* -29) */ break;
    case WFS_ERR_INVALID_TIMER: /* -30) */ break;
    case WFS_ERR_INVALID_TRACELEVEL: /* -31) */ break;
    case WFS_ERR_LOCKED: /* -32) */ break;
    case WFS_ERR_NO_BLOCKING_CALL: /* -33) */ break;
    case WFS_ERR_NO_SERVPROV: /* -34) */ break;
    case WFS_ERR_NO_SUCH_THREAD: /* -35) */ break;
    case WFS_ERR_NO_TIMER: /* -36) */ break;
    case WFS_ERR_NOT_LOCKED: /* -37) */ break;
    case WFS_ERR_NOT_OK_TO_UNLOAD: /* -38) */ break;
    case WFS_ERR_NOT_STARTED: /* -39) */ break;
    case WFS_ERR_NOT_REGISTERED: /* -40) */ break;
    case WFS_ERR_OP_IN_PROGRESS: /* -41) */ break;
    case WFS_ERR_OUT_OF_MEMORY: /* -42) */ break;
    case WFS_ERR_SERVICE_NOT_FOUND: /* -43) */ break;
    case WFS_ERR_SPI_VER_TOO_HIGH: /* -44) */ break;
    case WFS_ERR_SPI_VER_TOO_LOW: /* -45) */ break;
    case WFS_ERR_SRVC_VER_TOO_HIGH: /* -46) */ break;
    case WFS_ERR_SRVC_VER_TOO_LOW: /* -47) */ break;
    case WFS_ERR_TIMEOUT: /* -48) */ break;
    case WFS_ERR_UNSUPP_CATEGORY: /* -49) */ break;
    case WFS_ERR_UNSUPP_COMMAND: /* -50) */ break;
    case WFS_ERR_VERSION_ERROR_IN_SRVC: /* -51) */ break;
    case WFS_ERR_INVALID_DATA: /* -52) */ break;
    case WFS_ERR_SOFTWARE_ERROR: /* -53) */ break;
    case WFS_ERR_CONNECTION_LOST: /* -54) */ break;
    case WFS_ERR_USER_ERROR: /* -55) */ break;
    case WFS_ERR_UNSUPP_DATA: /* -56) */ break;
    case WFS_ERR_FRAUD_ATTEMPT: /* -57) */ break;
    case WFS_ERR_SEQUENCE_ERROR: /* -58) */ break;
    case WFS_ERR_CDM_INVALIDCURRENCY:
        printf("Invalid Currency");
        break;
    case WFS_ERR_CDM_INVALIDTELLERID:
        printf("Invalid Teller ID");
        break;
    case WFS_ERR_CDM_CASHUNITERROR:
        printf("Cash Unit Error");
        break;
    case WFS_EXEE_CDM_CASHUNITERROR:
    case WFS_ERR_CDM_INVALIDDENOMINATION:
        printf("Invalid Denomination");
        break;
    case WFS_ERR_CDM_INVALIDMIXNUMBER:
        printf("Invalid Mix Number");
        break;
    case WFS_ERR_CDM_NOCURRENCYMIX:
        printf("No Currency Mix");
        break;
    case WFS_ERR_CDM_NOTDISPENSABLE:
        printf("Not Dispensable");
        break;
    case WFS_ERR_CDM_TOOMANYITEMS:
        printf("Too Many Items to Dispense");
        break;
    default:
        printf("Unspecified Error");
    }

    printf(".\n");
}

// Top-level user input handler.
void handle(char* cmd) {
    int argc;
    char** args = parse(cmd, &argc);
    if (!argc) return;

    dispatch(commands, CMD_COUNT(commands), argc, args);
    free_args(argc, args);
}

// Dispatch command to sub-handler
HRESULT dispatch(cmd_t * fdt, int count, int argc, char** argv) {
    HRESULT res = WFSC_BAD_CMD;
    if (!argc) return res;
    // TODO: Help handler.

    for (; count > 0; --count) {
        cmd_t* c = fdt++;
        if (strcmp(c->name, argv[0]) == 0) {
            if (!c->func) {
                printf("[!] Unimplemented!\n");
                break;
            }
            res = c->func(argc - 1, argv + 1);
            if (res == WFSC_BAD_CMD) printf("[!] %s\n", c->help);
            break;
        }
    }
    return res;
}

// Lock WFS manager mutex for the given service
void lock(Service * svc) {
    LPWFSRESULT res;
    HRESULT out = WFSLock(svc->handle, WFS_INDEFINITE_WAIT, &res);
    check(out);

    // TODO: Check the result and handle when service is already locked.
    if (res) WFSFreeResult(res);
    res = NULL;
}

// Unlock WFS manager mutex for the given service
void unlock(Service * svc)
{
    HRESULT out = WFSUnlock(svc->handle);
    check(out);
}
````

## File: cmd.h
````c
#pragma once

#include "xfsapi.h"
#include <string>


#define WFSC_BAD_CMD 0x42
#define APPID "xfsc"
#define CMD_COUNT(x) (sizeof(x)/sizeof(cmd_t))

typedef HRESULT(*handler_t)(int, char**);
typedef void(*help_fn)();

typedef struct cmd_ {
    const char* name;
    const char* help;
    handler_t   func;
    help_fn     more;
    
} cmd_t;


class Service {
public:
    std::string name;
    // TODO: Other metadata...
    HSERVICE    handle;

    Service(std::string name, HSERVICE h) : name(name), handle(h) {}
    ~Service() {
        if (handle) WFSClose(handle);
    }
};

void handle(char* args);
HRESULT dispatch(cmd_t* fdt, int count, int argc, char** argv);
void check(HRESULT res);

Service* get_service(HSERVICE id);
void     del_service(Service* svc);

void lock(Service* svc);
void unlock(Service* svc);
````

## File: LICENSE
````
MIT License

Copyright (c) 2020 GoSecure

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: main.cpp
````cpp
#include "xfsapi.h"
#include "xfscdm.h"
#include "cmd.h"

#include <stdio.h>

// GLOBALS
WFSVERSION apiver, svcver, spiver;
HSERVICE svc;
HRESULT out;
LPSTR LOGICAL_NAME;

// Process a series of commands delimited by ;
void do_script(char* script) {
    char* context;
    char* tok = strtok_s(script, ";", &context);
    while (tok)
    {
        handle(tok);
        tok = strtok_s(NULL, ";", &context);
    }
}

int main(int argc, char** argv)
{

    printf(">>> XFS CLI - Copyright (c) 2019 GoSecure Inc. <<< \n");

    printf("--\n");
    printf("[+] Loading msxfs.dll... ");
    init();
    printf("OK\n");

    printf("[+] Establishing connection with XFSManager\n");
    out = WFSStartUp(3, &apiver);
    check(out);
    if (out != WFS_SUCCESS) exit(1);

    // Very rudimentary scripting support for now.
    if (argc == 3 && strcmp(argv[1], "-c")==0) do_script(argv[2]);

    printf("[*] API: %s\n", apiver.szDescription);

    char cmd[1024];
    do {
        printf("xfs> ");
        auto len = gets_s(cmd, 1024);
        handle(cmd);
    } while (1);

    return 0;
}
````

## File: output.txt
````
>>> XFS CLI - Copyright (c) 2019 GoSecure Inc. <<<
[+] Loading msxfs.dll... OK
[+] Establishing connection with XFSManager
[+] OK
[*] API: XFS API v2.00 to v3.30
[+] Opening Service: [redacted]
[+] OK
[*] Service:  [redacted] XFS
[*] Provider:
[+] Querying Capabilities...
[+] OK
    bCashBox: 0
    bCompound: 0
    bIntermediateStacker: 0
    bItemsTakenSensor: 0
    bPowerSaveControl: 7143535
    bPrepareDispense: 7274605
    bSafedoor: 0
    bShutter: 0
    bShutterControl: 1
    Exchange Type: 1
    Type: Self-Service Coin
    Max Dispense: 18
    Extra: 0=040111
    Positions:
      - FRONT
[+] Acquiring lock on [service]
[+] OK
[*] WFSLock returned: 0
[+] Querying Mix Types...
[+] OK
    01 - 01 - Algorithm - Minimum Number of Items
    02 - 01 - Algorithm - Maximum Number Of Cash Units
    03 - 01 - Algorithm - Equal Emptying Of Cash Units
[+] Querying Cash Dispenser Status
[+] OK
    Device:    1
    Dispenser: 3
    Stacker:   5
    Safedoor:  1
    Position:  104
    Output Positions
    -------------
    00 - FRONT (status=0x3) Shutter=0x4  Transport=0x2 (status=3)
[+] Listing cash units on [service]
[+] OK
[*] Found 00 cash units (may not reflect physical units)
[+] Done (for now.)
[+] Releasing lock
[+] OK
[*] WFSUnlock returned: 0
````

## File: README.md
````markdown
# XFSC - An Interactive XFS exploration Tool

eXtensions for Financial Services is an open protocol used for
abstracting away the functionality of various peripherals and hardware
used for cash registers, point of sales and ATMs.

This tool was designed as a proof of concept to explore and issue
commands directly to the devices that support the protocol. Among
other things, it can be used to force ATMs to dispense cash if you
have code execution on them.

The tool doesn't fully implement XFS yet, but a general skeleton is in
place that should make it easy to add support for additional commands
and features.


## Open Protocol Specification:
The standard is specified as [CWA 15748][spec]. All PDFs can be viewed
online for free without registration and are extremely detailed.

Header files are available in the appendix of each part of the standard
documents.

[spec]: https://www.cen.eu/work/areas/ICT/eBusiness/Pages/CWA15748.aspx


## Usage

The `help` function is not fully implemented yet, here is a general idea of the commands:

```c
// base commands
static cmd_t top_commands[] = {
    { "open",     "Establish a connection with a service provider.\nUsage: open <logical_name>", open_svc, NULL },
    { "close",    "Close an existing service connection.\nUsage: close <id>", close_svc, NULL },
    { "list",     "List active services.", list_svc, NULL },
    { "scan",     "Scans the computer for XFS services.", scan_svc, NULL},
    // ----
    { "cdm",      "Control a cash dispenser module.", cdm_dispatch, NULL},
    { "quit",     "Disconnect from the XFS manager.", do_quit, NULL },
    { "exit",     "See quit.", do_quit, NULL },
};

// cash dispenser commands
static cmd_t cdm_commands[] = {
    { "info",     "Queries information about the cash dispenser.\nUsage: cdm info <id>", cdm_info, NULL },
    { "caps",     "Queries capabilities of the cash dispenser.\nUsage: cdm caps <id>", cdm_caps, NULL },
    { "mix",      "Displays supported mixing algorithms\nUsage: cdm mix <id>", cdm_mixes, NULL },
    { "dispense", "Dispense cash\nUsage: cdm dispense <id> <amount> [currency=USD] [mix=1]", cdm_dispense, NULL },
};

```

Exercising a Cash Dispenser:

```
open CashDispenser_1
list
cdm info 1
cdm dispense 1 100 USD
close 1
quit
```

See `output.txt` for example output.

## Scripting

The tool supports rudimentary scripting mode where it will process
a list of commands from the command line to run unconditionally.

There is no logic supported in by the scripting engine for now.

```
xfsc.exe -c "open CashDispenser_1;info 1;close 1"
```


## Building

You will need Visual Studio Community. You can build from the IDE or
by running

```
msbuild xfsc.sln /p:Configuration=Release
```
````

## File: xfsapi.cpp
````cpp
#ifndef __inc_xfsapi__h
#include "xfsapi.h"
#endif

#include <stdio.h>

typedef HRESULT(WINAPI* fWFSCancelAsyncRequest) (HSERVICE hService, REQUESTID RequestID); fWFSCancelAsyncRequest pWFSCancelAsyncRequest;
typedef HRESULT(WINAPI* fWFSCancelBlockingCall) (DWORD dwThreadID); fWFSCancelBlockingCall pWFSCancelBlockingCall;
typedef HRESULT(WINAPI* fWFSCleanUp) (); fWFSCleanUp pWFSCleanUp;
typedef HRESULT(WINAPI* fWFSClose) (HSERVICE hService); fWFSClose pWFSClose;
typedef HRESULT(WINAPI* fWFSAsyncClose) (HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncClose pWFSAsyncClose;
typedef HRESULT(WINAPI* fWFSCreateAppHandle) (LPHAPP lphApp); fWFSCreateAppHandle pWFSCreateAppHandle;
typedef HRESULT(WINAPI* fWFSDeregister) (HSERVICE hService, DWORD dwEventClass, HWND hWndReg); fWFSDeregister pWFSDeregister;
typedef HRESULT(WINAPI* fWFSAsyncDeregister) (HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncDeregister pWFSAsyncDeregister;
typedef HRESULT(WINAPI* fWFSDestroyAppHandle) (HAPP hApp); fWFSDestroyAppHandle pWFSDestroyAppHandle;
typedef HRESULT(WINAPI* fWFSExecute) (HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, LPWFSRESULT*  lppResult); fWFSExecute pWFSExecute;
typedef HRESULT(WINAPI* fWFSAsyncExecute) (HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncExecute pWFSAsyncExecute;
typedef HRESULT(WINAPI* fWFSFreeResult) (LPWFSRESULT lpResult); fWFSFreeResult pWFSFreeResult;
typedef HRESULT(WINAPI* fWFSGetInfo) (HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, LPWFSRESULT*  lppResult); fWFSGetInfo pWFSGetInfo;
typedef HRESULT(WINAPI* fWFSAsyncGetInfo) (HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncGetInfo pWFSAsyncGetInfo;
typedef BOOL(WINAPI* fWFSIsBlocking) (); fWFSIsBlocking pWFSIsBlocking;
typedef HRESULT(WINAPI* fWFSLock) (HSERVICE hService, DWORD dwTimeOut, LPWFSRESULT*  lppResult); fWFSLock pWFSLock;
typedef HRESULT(WINAPI* fWFSAsyncLock) (HSERVICE hService, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncLock pWFSAsyncLock;
typedef HRESULT(WINAPI* fWFSOpen) (LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPHSERVICE lphService); fWFSOpen pWFSOpen;
typedef HRESULT(WINAPI* fWFSAsyncOpen) (LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, LPHSERVICE lphService, HWND hWnd, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPREQUESTID lpRequestID); fWFSAsyncOpen pWFSAsyncOpen;
typedef HRESULT(WINAPI* fWFSRegister) (HSERVICE hService, DWORD dwEventClass, HWND hWndReg); fWFSRegister pWFSRegister;
typedef HRESULT(WINAPI* fWFSAsyncRegister) (HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncRegister pWFSAsyncRegister;
typedef HRESULT(WINAPI* fWFSSetBlockingHook) (XFSBLOCKINGHOOK lpBlockFunc, LPXFSBLOCKINGHOOK lppPrevFunc); fWFSSetBlockingHook pWFSSetBlockingHook;

typedef HRESULT(WINAPI* fWFSUnhookBlockingHook) (); fWFSUnhookBlockingHook pWFSUnhookBlockingHook;
typedef HRESULT(WINAPI* fWFSUnlock) (HSERVICE hService); fWFSUnlock pWFSUnlock;
typedef HRESULT(WINAPI* fWFSAsyncUnlock) (HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID); fWFSAsyncUnlock pWFSAsyncUnlock;
typedef HRESULT(WINAPI* fWFMSetTraceLevel) (HSERVICE hService, DWORD dwTraceLevel); fWFMSetTraceLevel pWFMSetTraceLevel;

typedef HRESULT(WINAPI* fWFSStartUp) (DWORD dwVersionsRequired, LPWFSVERSION lpWFSVersion); fWFSStartUp pWFSStartUp;

// Load the XFS API and resolve symbols.
void init() {
    HMODULE xfs = LoadLibrary("msxfs.dll");
    if (!xfs) {
        auto err = GetLastError();
        printf("[!] Failed to load XFSManager: %d\n", err);
        exit(1);
    }

    pWFSCancelAsyncRequest = (fWFSCancelAsyncRequest)GetProcAddress(xfs, "WFSCancelAsyncRequest");
    pWFSCancelBlockingCall = (fWFSCancelBlockingCall)GetProcAddress(xfs, "WFSCancelBlockingCall");
    pWFSCleanUp = (fWFSCleanUp)GetProcAddress(xfs, "WFSCleanUp");
    pWFSClose = (fWFSClose)GetProcAddress(xfs, "WFSClose");
    pWFSAsyncClose = (fWFSAsyncClose)GetProcAddress(xfs, "WFSAsyncClose");
    pWFSCreateAppHandle = (fWFSCreateAppHandle)GetProcAddress(xfs, "WFSCreateAppHandle");
    pWFSDeregister = (fWFSDeregister)GetProcAddress(xfs, "WFSDeregister");
    pWFSAsyncDeregister = (fWFSAsyncDeregister)GetProcAddress(xfs, "WFSAsyncDeregister");
    pWFSDestroyAppHandle = (fWFSDestroyAppHandle)GetProcAddress(xfs, "WFSDestroyAppHandle");
    pWFSExecute = (fWFSExecute)GetProcAddress(xfs, "WFSExecute");
    pWFSAsyncExecute = (fWFSAsyncExecute)GetProcAddress(xfs, "WFSAsyncExecute");
    pWFSFreeResult = (fWFSFreeResult)GetProcAddress(xfs, "WFSFreeResult");
    pWFSGetInfo = (fWFSGetInfo)GetProcAddress(xfs, "WFSGetInfo");
    pWFSAsyncGetInfo = (fWFSAsyncGetInfo)GetProcAddress(xfs, "WFSAsyncGetInfo");
    pWFSIsBlocking = (fWFSIsBlocking)GetProcAddress(xfs, "WFSIsBlocking");
    pWFSLock = (fWFSLock)GetProcAddress(xfs, "WFSLock");
    pWFSAsyncLock = (fWFSAsyncLock)GetProcAddress(xfs, "WFSAsyncLock");
    pWFSOpen = (fWFSOpen)GetProcAddress(xfs, "WFSOpen");
    pWFSAsyncOpen = (fWFSAsyncOpen)GetProcAddress(xfs, "WFSAsyncOpen");
    pWFSRegister = (fWFSRegister)GetProcAddress(xfs, "WFSRegister");
    pWFSAsyncRegister = (fWFSAsyncRegister)GetProcAddress(xfs, "WFSAsyncRegister");
    pWFSSetBlockingHook = (fWFSSetBlockingHook)GetProcAddress(xfs, "WFSSetBlockingHook");
    pWFSStartUp = (fWFSStartUp)GetProcAddress(xfs, "WFSStartUp");
    pWFSUnhookBlockingHook = (fWFSUnhookBlockingHook)GetProcAddress(xfs, "WFSUnhookBlockingHook");
    pWFSUnlock = (fWFSUnlock)GetProcAddress(xfs, "WFSUnlock");
    pWFSAsyncUnlock = (fWFSAsyncUnlock)GetProcAddress(xfs, "WFSAsyncUnlock");
    pWFMSetTraceLevel = (fWFMSetTraceLevel)GetProcAddress(xfs, "WFMSetTraceLevel");
    return;
}

// Wrapper Funtions
extern "C" {

    HRESULT  WINAPI WFSCancelAsyncRequest(HSERVICE hService, REQUESTID RequestID) {
        return pWFSCancelAsyncRequest(hService, RequestID);
    }

    HRESULT  WINAPI WFSCancelBlockingCall(DWORD dwThreadID) {
        return pWFSCancelBlockingCall(dwThreadID);
    }

    HRESULT  WINAPI WFSCleanUp() {
        return pWFSCleanUp();
    }

    HRESULT  WINAPI WFSClose(HSERVICE hService) {
        return pWFSClose(hService);
    }

    HRESULT  WINAPI WFSAsyncClose(HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncClose(hService, hWnd, lpRequestID);
    }

    HRESULT  WINAPI WFSCreateAppHandle(LPHAPP lphApp) {
        return pWFSCreateAppHandle(lphApp);
    }

    HRESULT  WINAPI WFSDeregister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg) {
        return pWFSDeregister(hService, dwEventClass, hWndReg);
    }

    HRESULT  WINAPI WFSAsyncDeregister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncDeregister(hService, dwEventClass, hWndReg, hWnd, lpRequestID);
    }

    HRESULT  WINAPI WFSDestroyAppHandle(HAPP hApp) {
        return pWFSDestroyAppHandle(hApp);
    }

    HRESULT  WINAPI WFSExecute(HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, LPWFSRESULT* lppResult) {
        return pWFSExecute(hService, dwCommand, lpCmdData, dwTimeOut, lppResult);
    }

    HRESULT  WINAPI WFSAsyncExecute(HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncExecute(hService, dwCommand, lpCmdData, dwTimeOut, hWnd, lpRequestID);
    }

    HRESULT  WINAPI WFSFreeResult(LPWFSRESULT lpResult) {
        return pWFSFreeResult(lpResult);
    }

    HRESULT  WINAPI WFSGetInfo(HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, LPWFSRESULT* lppResult) {
        return pWFSGetInfo(hService, dwCategory, lpQueryDetails, dwTimeOut, lppResult);
    }

    HRESULT  WINAPI WFSAsyncGetInfo(HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncGetInfo(hService, dwCategory, lpQueryDetails, dwTimeOut, hWnd, lpRequestID);
    }

    BOOL     WINAPI WFSIsBlocking() {
        return pWFSIsBlocking();
    }

    HRESULT  WINAPI WFSLock(HSERVICE hService, DWORD dwTimeOut, LPWFSRESULT* lppResult) {
        return pWFSLock(hService, dwTimeOut, lppResult);
    }

    HRESULT  WINAPI WFSAsyncLock(HSERVICE hService, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncLock(hService, dwTimeOut, hWnd, lpRequestID);
    }

    HRESULT WINAPI WFSOpen(LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPHSERVICE lphService) {
        return pWFSOpen(lpszLogicalName, hApp, lpszAppID, dwTraceLevel, dwTimeOut, dwSrvcVersionsRequired, lpSrvcVersion, lpSPIVersion, lphService);
    }

    HRESULT  WINAPI WFSAsyncOpen(LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, LPHSERVICE lphService, HWND hWnd, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPREQUESTID lpRequestID) {
        return pWFSAsyncOpen(lpszLogicalName, hApp, lpszAppID, dwTraceLevel, dwTimeOut, lphService, hWnd, dwSrvcVersionsRequired, lpSrvcVersion, lpSPIVersion, lpRequestID);
    }

    HRESULT  WINAPI WFSRegister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg) {
        return pWFSRegister(hService, dwEventClass, hWndReg);
    }

    HRESULT  WINAPI WFSAsyncRegister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncRegister(hService, dwEventClass, hWndReg, hWnd, lpRequestID);
    }

    HRESULT  WINAPI WFSSetBlockingHook(XFSBLOCKINGHOOK lpBlockFunc, LPXFSBLOCKINGHOOK lppPrevFunc) {
        return pWFSSetBlockingHook(lpBlockFunc, lppPrevFunc);
    }

    HRESULT  WINAPI WFSStartUp(DWORD dwVersionsRequired, LPWFSVERSION lpWFSVersion) {
        return pWFSStartUp(dwVersionsRequired, lpWFSVersion);
    }

    HRESULT  WINAPI WFSUnhookBlockingHook() {
        return pWFSUnhookBlockingHook();
    }

    HRESULT  WINAPI WFSUnlock(HSERVICE hService) {
        return pWFSUnlock(hService);
    }

    HRESULT  WINAPI WFSAsyncUnlock(HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID) {
        return pWFSAsyncUnlock(hService, hWnd, lpRequestID);
    }

    HRESULT  WINAPI WFMSetTraceLevel(HSERVICE hService, DWORD dwTraceLevel) {
        return pWFMSetTraceLevel(hService, dwTraceLevel);
    }
}
````

## File: xfsapi.h
````c
/************************************************************************
*                                                                       *
* xfsapi.h      XFS - API functions, types, and definitions             *
*                                                                       *
*               Version 3.10  --  29/11/2007                            *
*                                                                       *
************************************************************************/

#ifndef __inc_xfsapi__h
#define __inc_xfsapi__h
#pragma pack(push,1)

void init(); // Load msxfs.dll and resolve symbols.
/****** Common *********************************************************/
#include <windows.h>

typedef unsigned short USHORT;
typedef char CHAR;
typedef short SHORT;
typedef unsigned long ULONG;
typedef unsigned char UCHAR;
typedef SHORT* LPSHORT;
typedef LPVOID* LPLPVOID;
typedef ULONG* LPULONG;
typedef USHORT* LPUSHORT;

typedef HANDLE HPROVIDER;

typedef ULONG REQUESTID;
typedef REQUESTID* LPREQUESTID;

typedef HANDLE HAPP;
typedef HAPP* LPHAPP;

typedef USHORT HSERVICE;
typedef HSERVICE* LPHSERVICE;

typedef LONG HRESULT;
typedef HRESULT* LPHRESULT;

typedef BOOL(WINAPI* XFSBLOCKINGHOOK)(VOID);
typedef XFSBLOCKINGHOOK* LPXFSBLOCKINGHOOK;

/****** String lengths **************************************************/

#define WFSDDESCRIPTION_LEN                     256
#define WFSDSYSSTATUS_LEN                       256

/****** Values of WFSDEVSTATUS.fwState **********************************/

#define WFS_STAT_DEVONLINE                      (0)
#define WFS_STAT_DEVOFFLINE                     (1)
#define WFS_STAT_DEVPOWEROFF                    (2)
#define WFS_STAT_DEVNODEVICE                    (3)
#define WFS_STAT_DEVHWERROR                     (4)
#define WFS_STAT_DEVUSERERROR                   (5)
#define WFS_STAT_DEVBUSY                        (6)
#define WFS_STAT_DEVFRAUDATTEMPT                (7)

/****** Value of WFS_DEFAULT_HAPP ***************************************/

#define WFS_DEFAULT_HAPP                        (0)

/****** Data Structures *************************************************/

typedef struct _wfs_result
{
    REQUESTID       RequestID;//4
    HSERVICE        hService;//2
    SYSTEMTIME      tsTimestamp;//16
    HRESULT         hResult; //4
    union {
        DWORD       dwCommandCode;
        DWORD       dwEventID;
    } u;//4
    LPVOID          lpBuffer; //offset 30
} WFSRESULT, * LPWFSRESULT;

typedef struct _wfsversion
{
    WORD            wVersion;
    WORD            wLowVersion;
    WORD            wHighVersion;
    CHAR            szDescription[WFSDDESCRIPTION_LEN + 1];
    CHAR            szSystemStatus[WFSDSYSSTATUS_LEN + 1];
} WFSVERSION, * LPWFSVERSION;

/****** Message Structures **********************************************/

typedef struct _wfs_devstatus
{
    LPSTR           lpszPhysicalName;
    LPSTR           lpszWorkstationName;
    DWORD           dwState;
} WFSDEVSTATUS, * LPWFSDEVSTATUS;

typedef struct _wfs_undevmsg
{
    LPSTR           lpszLogicalName;
    LPSTR           lpszWorkstationName;
    LPSTR           lpszAppID;
    DWORD           dwSize;
    LPBYTE          lpbDescription;
    DWORD           dwMsg;
    LPWFSRESULT     lpWFSResult;
} WFSUNDEVMSG, * LPWFSUNDEVMSG;

typedef struct _wfs_appdisc
{
    LPSTR           lpszLogicalName;
    LPSTR           lpszWorkstationName;
    LPSTR           lpszAppID;
} WFSAPPDISC, * LPWFSAPPDISC;

typedef struct _wfs_hwerror
{
    LPSTR           lpszLogicalName;
    LPSTR           lpszPhysicalName;
    LPSTR           lpszWorkstationName;
    LPSTR           lpszAppID;
    DWORD           dwAction;
    DWORD           dwSize;
    LPBYTE          lpbDescription;
} WFSHWERROR, * LPWFSHWERROR;

typedef struct _wfs_vrsnerror
{
    LPSTR           lpszLogicalName;
    LPSTR           lpszWorkstationName;
    LPSTR           lpszAppID;
    DWORD           dwSize;
    LPBYTE          lpbDescription;
    LPWFSVERSION    lpWFSVersion;
} WFSVRSNERROR, * LPWFSVRSNERROR;

/****** Error codes ******************************************************/

#define WFS_SUCCESS                             (0)
#define WFS_ERR_ALREADY_STARTED                 (-1)
#define WFS_ERR_API_VER_TOO_HIGH                (-2)
#define WFS_ERR_API_VER_TOO_LOW                 (-3)
#define WFS_ERR_CANCELED                        (-4)
#define WFS_ERR_CFG_INVALID_HKEY                (-5)
#define WFS_ERR_CFG_INVALID_NAME                (-6)
#define WFS_ERR_CFG_INVALID_SUBKEY              (-7)
#define WFS_ERR_CFG_INVALID_VALUE               (-8)
#define WFS_ERR_CFG_KEY_NOT_EMPTY               (-9)
#define WFS_ERR_CFG_NAME_TOO_LONG               (-10)
#define WFS_ERR_CFG_NO_MORE_ITEMS               (-11)
#define WFS_ERR_CFG_VALUE_TOO_LONG              (-12)
#define WFS_ERR_DEV_NOT_READY                   (-13)
#define WFS_ERR_HARDWARE_ERROR                  (-14)
#define WFS_ERR_INTERNAL_ERROR                  (-15)
#define WFS_ERR_INVALID_ADDRESS                 (-16)
#define WFS_ERR_INVALID_APP_HANDLE              (-17)
#define WFS_ERR_INVALID_BUFFER                  (-18)
#define WFS_ERR_INVALID_CATEGORY                (-19)
#define WFS_ERR_INVALID_COMMAND                 (-20)
#define WFS_ERR_INVALID_EVENT_CLASS             (-21)
#define WFS_ERR_INVALID_HSERVICE                (-22)
#define WFS_ERR_INVALID_HPROVIDER               (-23)
#define WFS_ERR_INVALID_HWND                    (-24)
#define WFS_ERR_INVALID_HWNDREG                 (-25)
#define WFS_ERR_INVALID_POINTER                 (-26)
#define WFS_ERR_INVALID_REQ_ID                  (-27)
#define WFS_ERR_INVALID_RESULT                  (-28)
#define WFS_ERR_INVALID_SERVPROV                (-29)
#define WFS_ERR_INVALID_TIMER                   (-30)
#define WFS_ERR_INVALID_TRACELEVEL              (-31)
#define WFS_ERR_LOCKED                          (-32)
#define WFS_ERR_NO_BLOCKING_CALL                (-33)
#define WFS_ERR_NO_SERVPROV                     (-34)
#define WFS_ERR_NO_SUCH_THREAD                  (-35)
#define WFS_ERR_NO_TIMER                        (-36)
#define WFS_ERR_NOT_LOCKED                      (-37)
#define WFS_ERR_NOT_OK_TO_UNLOAD                (-38)
#define WFS_ERR_NOT_STARTED                     (-39)
#define WFS_ERR_NOT_REGISTERED                  (-40)
#define WFS_ERR_OP_IN_PROGRESS                  (-41)
#define WFS_ERR_OUT_OF_MEMORY                   (-42)
#define WFS_ERR_SERVICE_NOT_FOUND               (-43)
#define WFS_ERR_SPI_VER_TOO_HIGH                (-44)
#define WFS_ERR_SPI_VER_TOO_LOW                 (-45)
#define WFS_ERR_SRVC_VER_TOO_HIGH               (-46)
#define WFS_ERR_SRVC_VER_TOO_LOW                (-47)
#define WFS_ERR_TIMEOUT                         (-48)
#define WFS_ERR_UNSUPP_CATEGORY                 (-49)
#define WFS_ERR_UNSUPP_COMMAND                  (-50)
#define WFS_ERR_VERSION_ERROR_IN_SRVC           (-51)
#define WFS_ERR_INVALID_DATA                    (-52)
#define WFS_ERR_SOFTWARE_ERROR                  (-53)
#define WFS_ERR_CONNECTION_LOST                 (-54)
#define WFS_ERR_USER_ERROR                      (-55)
#define WFS_ERR_UNSUPP_DATA                     (-56)
#define WFS_ERR_FRAUD_ATTEMPT                   (-57)
#define WFS_ERR_SEQUENCE_ERROR                  (-58)


#define WFS_INDEFINITE_WAIT                     0

/****** Messages ********************************************************/

/* Message-No = (WM_USER + No) */

#define WFS_OPEN_COMPLETE                       (WM_USER + 1)
#define WFS_CLOSE_COMPLETE                      (WM_USER + 2)
#define WFS_LOCK_COMPLETE                       (WM_USER + 3)
#define WFS_UNLOCK_COMPLETE                     (WM_USER + 4)
#define WFS_REGISTER_COMPLETE                   (WM_USER + 5)
#define WFS_DEREGISTER_COMPLETE                 (WM_USER + 6)
#define WFS_GETINFO_COMPLETE                    (WM_USER + 7)
#define WFS_EXECUTE_COMPLETE                    (WM_USER + 8)

#define WFS_EXECUTE_EVENT                       (WM_USER + 20)
#define WFS_SERVICE_EVENT                       (WM_USER + 21)
#define WFS_USER_EVENT                          (WM_USER + 22)
#define WFS_SYSTEM_EVENT                        (WM_USER + 23)

#define WFS_TIMER_EVENT                         (WM_USER + 100)

/****** Event Classes ***************************************************/

#define SERVICE_EVENTS                          (1)
#define USER_EVENTS                             (2)
#define SYSTEM_EVENTS                           (4)
#define EXECUTE_EVENTS                          (8)

/****** System Event IDs ************************************************/

#define WFS_SYSE_UNDELIVERABLE_MSG              (1)
#define WFS_SYSE_HARDWARE_ERROR                 (2)
#define WFS_SYSE_VERSION_ERROR                  (3)
#define WFS_SYSE_DEVICE_STATUS                  (4)
#define WFS_SYSE_APP_DISCONNECT                 (5)
#define WFS_SYSE_SOFTWARE_ERROR                 (6)
#define WFS_SYSE_USER_ERROR                     (7)
#define WFS_SYSE_LOCK_REQUESTED                 (8)
#define WFS_SYSE_FRAUD_ATTEMPT                  (9)


/****** XFS Trace Level ********************************************/

#define WFS_TRACE_API                           (0x00000001)
#define WFS_TRACE_ALL_API                       (0x00000002)
#define WFS_TRACE_SPI                           (0x00000004)
#define WFS_TRACE_ALL_SPI                       (0x00000008)
#define WFS_TRACE_MGR                           (0x00000010)

/****** XFS Error Actions ********************************************/

#define WFS_ERR_ACT_NOACTION                    (0x0000)
#define WFS_ERR_ACT_RESET                       (0x0001)
#define WFS_ERR_ACT_SWERROR                     (0x0002)
#define WFS_ERR_ACT_CONFIG                      (0x0004)
#define WFS_ERR_ACT_HWCLEAR                     (0x0008)
#define WFS_ERR_ACT_HWMAINT                     (0x0010)
#define WFS_ERR_ACT_SUSPEND                     (0x0020)

/****** XFS SNMP MIB Category Codes **********************************/
/* NOTE: To support the XFS SNMP MIB, the WFSGet[Async]Info category codes between 60000 and 60999 are reserved.*/


/****** API functions ***************************************************/
extern "C" {
    HRESULT  WINAPI WFSCancelAsyncRequest(HSERVICE hService, REQUESTID RequestID);
    HRESULT  WINAPI WFSCancelBlockingCall(DWORD dwThreadID);
    HRESULT  WINAPI WFSCleanUp();
    HRESULT  WINAPI WFSClose(HSERVICE hService);
    HRESULT  WINAPI WFSAsyncClose(HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSCreateAppHandle(LPHAPP lphApp);
    HRESULT  WINAPI WFSDeregister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg);
    HRESULT  WINAPI WFSAsyncDeregister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSDestroyAppHandle(HAPP hApp);
    HRESULT  WINAPI WFSExecute(HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, LPWFSRESULT* lppResult);
    HRESULT  WINAPI WFSAsyncExecute(HSERVICE hService, DWORD dwCommand, LPVOID lpCmdData, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSFreeResult(LPWFSRESULT lpResult);
    HRESULT  WINAPI WFSGetInfo(HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, LPWFSRESULT* lppResult);
    HRESULT  WINAPI WFSAsyncGetInfo(HSERVICE hService, DWORD dwCategory, LPVOID lpQueryDetails, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID);
    BOOL     WINAPI WFSIsBlocking();
    HRESULT  WINAPI WFSLock(HSERVICE hService, DWORD dwTimeOut, LPWFSRESULT* lppResult);
    HRESULT  WINAPI WFSAsyncLock(HSERVICE hService, DWORD dwTimeOut, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSOpen(LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPHSERVICE lphService);
    HRESULT  WINAPI WFSAsyncOpen(LPSTR lpszLogicalName, HAPP hApp, LPSTR lpszAppID, DWORD dwTraceLevel, DWORD dwTimeOut, LPHSERVICE lphService, HWND hWnd, DWORD dwSrvcVersionsRequired, LPWFSVERSION lpSrvcVersion, LPWFSVERSION lpSPIVersion, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSRegister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg);
    HRESULT  WINAPI WFSAsyncRegister(HSERVICE hService, DWORD dwEventClass, HWND hWndReg, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFSSetBlockingHook(XFSBLOCKINGHOOK lpBlockFunc, LPXFSBLOCKINGHOOK lppPrevFunc);
    HRESULT  WINAPI WFSStartUp(DWORD dwVersionsRequired, LPWFSVERSION lpWFSVersion);
    HRESULT  WINAPI WFSUnhookBlockingHook();
    HRESULT  WINAPI WFSUnlock(HSERVICE hService);
    HRESULT  WINAPI WFSAsyncUnlock(HSERVICE hService, HWND hWnd, LPREQUESTID lpRequestID);
    HRESULT  WINAPI WFMSetTraceLevel(HSERVICE hService, DWORD dwTraceLevel);

}
/*   restore alignment   */
#pragma pack(pop)


#endif  /* __inc_xfsapi__h */
````

## File: xfsc.sln
````
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 16
VisualStudioVersion = 16.0.28803.352
MinimumVisualStudioVersion = 10.0.40219.1
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "xfsc", "xfsc.vcxproj", "{2E0F1465-A776-4407-9180-44BA2645C2A0}"
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|x64 = Debug|x64
		Debug|x86 = Debug|x86
		Release|x64 = Release|x64
		Release|x86 = Release|x86
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Debug|x64.ActiveCfg = Debug|x64
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Debug|x64.Build.0 = Debug|x64
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Debug|x86.ActiveCfg = Debug|Win32
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Debug|x86.Build.0 = Debug|Win32
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Release|x64.ActiveCfg = Release|x64
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Release|x64.Build.0 = Release|x64
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Release|x86.ActiveCfg = Release|Win32
		{2E0F1465-A776-4407-9180-44BA2645C2A0}.Release|x86.Build.0 = Release|Win32
		{3B50905A-CC35-4306-AF42-4F181276C522}.Debug|x64.ActiveCfg = Debug|x64
		{3B50905A-CC35-4306-AF42-4F181276C522}.Debug|x64.Build.0 = Debug|x64
		{3B50905A-CC35-4306-AF42-4F181276C522}.Debug|x86.ActiveCfg = Debug|Win32
		{3B50905A-CC35-4306-AF42-4F181276C522}.Debug|x86.Build.0 = Debug|Win32
		{3B50905A-CC35-4306-AF42-4F181276C522}.Release|x64.ActiveCfg = Release|x64
		{3B50905A-CC35-4306-AF42-4F181276C522}.Release|x64.Build.0 = Release|x64
		{3B50905A-CC35-4306-AF42-4F181276C522}.Release|x86.ActiveCfg = Release|Win32
		{3B50905A-CC35-4306-AF42-4F181276C522}.Release|x86.Build.0 = Release|Win32
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
	GlobalSection(ExtensibilityGlobals) = postSolution
		SolutionGuid = {984D279E-7716-479A-BD14-D6A9F6B95E4D}
	EndGlobalSection
EndGlobal
````

## File: xfsc.vcxproj
````
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|Win32">
      <Configuration>Debug</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|Win32">
      <Configuration>Release</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <VCProjectVersion>16.0</VCProjectVersion>
    <ProjectGuid>{2E0F1465-A776-4407-9180-44BA2645C2A0}</ProjectGuid>
    <RootNamespace>xfsc</RootNamespace>
    <WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
    <WholeProgramOptimization>true</WholeProgramOptimization>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v142</PlatformToolset>
    <WholeProgramOptimization>true</WholeProgramOptimization>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="Shared">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup />
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <ClCompile>
      <WarningLevel>Level3</WarningLevel>
      <Optimization>Disabled</Optimization>
      <SDLCheck>true</SDLCheck>
      <ConformanceMode>true</ConformanceMode>
      <ExceptionHandling>Sync</ExceptionHandling>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
    </Link>
    <PostBuildEvent>
      <Command>copy $(OutputPath)$(TargetFileName) C:\Temp\xfsc.exe</Command>
    </PostBuildEvent>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <ClCompile>
      <WarningLevel>Level3</WarningLevel>
      <Optimization>Disabled</Optimization>
      <SDLCheck>true</SDLCheck>
      <ConformanceMode>true</ConformanceMode>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
    </Link>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <ClCompile>
      <WarningLevel>Level3</WarningLevel>
      <Optimization>MaxSpeed</Optimization>
      <FunctionLevelLinking>true</FunctionLevelLinking>
      <IntrinsicFunctions>true</IntrinsicFunctions>
      <SDLCheck>true</SDLCheck>
      <ConformanceMode>true</ConformanceMode>
      <RuntimeLibrary>MultiThreaded</RuntimeLibrary>
      <ExceptionHandling>Sync</ExceptionHandling>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
      <EnableCOMDATFolding>true</EnableCOMDATFolding>
      <OptimizeReferences>true</OptimizeReferences>
    </Link>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <ClCompile>
      <WarningLevel>Level3</WarningLevel>
      <Optimization>MaxSpeed</Optimization>
      <FunctionLevelLinking>true</FunctionLevelLinking>
      <IntrinsicFunctions>true</IntrinsicFunctions>
      <SDLCheck>true</SDLCheck>
      <ConformanceMode>true</ConformanceMode>
    </ClCompile>
    <Link>
      <SubSystem>Console</SubSystem>
      <EnableCOMDATFolding>true</EnableCOMDATFolding>
      <OptimizeReferences>true</OptimizeReferences>
    </Link>
  </ItemDefinitionGroup>
  <ItemGroup>
    <ClCompile Include="cdm.cpp" />
    <ClCompile Include="cmd.cpp" />
    <ClCompile Include="main.cpp" />
    <ClCompile Include="xfsapi.cpp" />
  </ItemGroup>
  <ItemGroup>
    <ClInclude Include="cdm.h" />
    <ClInclude Include="cmd.h" />
    <ClInclude Include="xfsapi.h" />
    <ClInclude Include="xfscdm.h" />
  </ItemGroup>
  <ItemGroup>
    <None Include="msxfs.dll" />
  </ItemGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>
````

## File: xfsc.vcxproj.filters
````
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Filter Include="Source Files">
      <UniqueIdentifier>{4FC737F1-C7A5-4376-A066-2A32D752A2FF}</UniqueIdentifier>
      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx</Extensions>
    </Filter>
    <Filter Include="Header Files">
      <UniqueIdentifier>{93995380-89BD-4b04-88EB-625FBE52EBFB}</UniqueIdentifier>
      <Extensions>h;hh;hpp;hxx;hm;inl;inc;ipp;xsd</Extensions>
    </Filter>
    <Filter Include="Resource Files">
      <UniqueIdentifier>{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}</UniqueIdentifier>
      <Extensions>rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx;tiff;tif;png;wav;mfcribbon-ms</Extensions>
    </Filter>
  </ItemGroup>
  <ItemGroup>
    <ClCompile Include="cmd.cpp">
      <Filter>Source Files</Filter>
    </ClCompile>
    <ClCompile Include="main.cpp">
      <Filter>Source Files</Filter>
    </ClCompile>
    <ClCompile Include="xfsapi.cpp">
      <Filter>Source Files</Filter>
    </ClCompile>
    <ClCompile Include="cdm.cpp">
      <Filter>Source Files</Filter>
    </ClCompile>
  </ItemGroup>
  <ItemGroup>
    <ClInclude Include="xfsapi.h">
      <Filter>Header Files</Filter>
    </ClInclude>
    <ClInclude Include="xfscdm.h">
      <Filter>Header Files</Filter>
    </ClInclude>
    <ClInclude Include="cmd.h">
      <Filter>Header Files</Filter>
    </ClInclude>
    <ClInclude Include="cdm.h">
      <Filter>Header Files</Filter>
    </ClInclude>
  </ItemGroup>
  <ItemGroup>
    <None Include="msxfs.dll" />
  </ItemGroup>
</Project>
````

## File: xfscdm.h
````c
/******************************************************************************
*                                                                             *
* xfscdm.h      XFS - Cash Dispenser (CDM) definitions                        *
*                                                                             *
*               Version 3.10 (29/11/2007)                                     *
*                                                                             *
******************************************************************************/

#ifndef __INC_XFSCDM__H
#define __INC_XFSCDM__H

#ifdef __cplusplus
extern "C" {
#endif

#include "xfsapi.h"

    /* be aware of alignment */
#pragma pack (push, 1)

/* values of WFSCDMCAPS.wClass */

#define     WFS_SERVICE_CLASS_CDM                     (3)
#define     WFS_SERVICE_CLASS_VERSION_CDM             0x0A03 /* Version 3.10 */
#define     WFS_SERVICE_CLASS_NAME_CDM                "CDM"

#define     CDM_SERVICE_OFFSET                        (WFS_SERVICE_CLASS_CDM * 100)

/* CDM Info Commands */

#define     WFS_INF_CDM_STATUS                        (CDM_SERVICE_OFFSET + 1)
#define     WFS_INF_CDM_CAPABILITIES                  (CDM_SERVICE_OFFSET + 2)
#define     WFS_INF_CDM_CASH_UNIT_INFO                (CDM_SERVICE_OFFSET + 3)
#define     WFS_INF_CDM_TELLER_INFO                   (CDM_SERVICE_OFFSET + 4)
#define     WFS_INF_CDM_CURRENCY_EXP                  (CDM_SERVICE_OFFSET + 6)
#define     WFS_INF_CDM_MIX_TYPES                     (CDM_SERVICE_OFFSET + 7)
#define     WFS_INF_CDM_MIX_TABLE                     (CDM_SERVICE_OFFSET + 8)
#define     WFS_INF_CDM_PRESENT_STATUS                (CDM_SERVICE_OFFSET + 9)

/* CDM Execute Commands */

#define     WFS_CMD_CDM_DENOMINATE                    (CDM_SERVICE_OFFSET + 1)
#define     WFS_CMD_CDM_DISPENSE                      (CDM_SERVICE_OFFSET + 2)
#define     WFS_CMD_CDM_PRESENT                       (CDM_SERVICE_OFFSET + 3)
#define     WFS_CMD_CDM_REJECT                        (CDM_SERVICE_OFFSET + 4)
#define     WFS_CMD_CDM_RETRACT                       (CDM_SERVICE_OFFSET + 5)
#define     WFS_CMD_CDM_OPEN_SHUTTER                  (CDM_SERVICE_OFFSET + 7)
#define     WFS_CMD_CDM_CLOSE_SHUTTER                 (CDM_SERVICE_OFFSET + 8)
#define     WFS_CMD_CDM_SET_TELLER_INFO               (CDM_SERVICE_OFFSET + 9)
#define     WFS_CMD_CDM_SET_CASH_UNIT_INFO            (CDM_SERVICE_OFFSET + 10)
#define     WFS_CMD_CDM_START_EXCHANGE                (CDM_SERVICE_OFFSET + 11)
#define     WFS_CMD_CDM_END_EXCHANGE                  (CDM_SERVICE_OFFSET + 12)
#define     WFS_CMD_CDM_OPEN_SAFE_DOOR                (CDM_SERVICE_OFFSET + 13)
#define     WFS_CMD_CDM_CALIBRATE_CASH_UNIT           (CDM_SERVICE_OFFSET + 15)
#define     WFS_CMD_CDM_SET_MIX_TABLE                 (CDM_SERVICE_OFFSET + 20)
#define     WFS_CMD_CDM_RESET                         (CDM_SERVICE_OFFSET + 21)
#define     WFS_CMD_CDM_TEST_CASH_UNITS               (CDM_SERVICE_OFFSET + 22)
#define     WFS_CMD_CDM_COUNT                         (CDM_SERVICE_OFFSET + 23)
#define     WFS_CMD_CDM_SET_GUIDANCE_LIGHT            (CDM_SERVICE_OFFSET + 24)
#define     WFS_CMD_CDM_POWER_SAVE_CONTROL            (CDM_SERVICE_OFFSET + 25)
#define     WFS_CMD_CDM_PREPARE_DISPENSE              (CDM_SERVICE_OFFSET + 26)


/* CDM Messages */

#define     WFS_SRVE_CDM_SAFEDOOROPEN                 (CDM_SERVICE_OFFSET + 1)
#define     WFS_SRVE_CDM_SAFEDOORCLOSED               (CDM_SERVICE_OFFSET + 2)
#define     WFS_USRE_CDM_CASHUNITTHRESHOLD            (CDM_SERVICE_OFFSET + 3)
#define     WFS_SRVE_CDM_CASHUNITINFOCHANGED          (CDM_SERVICE_OFFSET + 4)
#define     WFS_SRVE_CDM_TELLERINFOCHANGED            (CDM_SERVICE_OFFSET + 5)
#define     WFS_EXEE_CDM_DELAYEDDISPENSE              (CDM_SERVICE_OFFSET + 6)
#define     WFS_EXEE_CDM_STARTDISPENSE                (CDM_SERVICE_OFFSET + 7)
#define     WFS_EXEE_CDM_CASHUNITERROR                (CDM_SERVICE_OFFSET + 8)
#define     WFS_SRVE_CDM_ITEMSTAKEN                   (CDM_SERVICE_OFFSET + 9)
#define     WFS_EXEE_CDM_PARTIALDISPENSE              (CDM_SERVICE_OFFSET + 10)
#define     WFS_EXEE_CDM_SUBDISPENSEOK                (CDM_SERVICE_OFFSET + 11)
#define     WFS_SRVE_CDM_ITEMSPRESENTED               (CDM_SERVICE_OFFSET + 13)
#define     WFS_SRVE_CDM_COUNTS_CHANGED               (CDM_SERVICE_OFFSET + 14)
#define     WFS_EXEE_CDM_INCOMPLETEDISPENSE           (CDM_SERVICE_OFFSET + 15)
#define     WFS_EXEE_CDM_NOTEERROR                    (CDM_SERVICE_OFFSET + 16)
#define     WFS_SRVE_CDM_MEDIADETECTED                (CDM_SERVICE_OFFSET + 17)
#define     WFS_EXEE_CDM_INPUT_P6                     (CDM_SERVICE_OFFSET + 18)
#define     WFS_SRVE_CDM_DEVICEPOSITION               (CDM_SERVICE_OFFSET + 19)
#define     WFS_SRVE_CDM_POWER_SAVE_CHANGE            (CDM_SERVICE_OFFSET + 20)


/* values of WFSCDMSTATUS.fwDevice */

#define     WFS_CDM_DEVONLINE                         WFS_STAT_DEVONLINE
#define     WFS_CDM_DEVOFFLINE                        WFS_STAT_DEVOFFLINE
#define     WFS_CDM_DEVPOWEROFF                       WFS_STAT_DEVPOWEROFF
#define     WFS_CDM_DEVNODEVICE                       WFS_STAT_DEVNODEVICE
#define     WFS_CDM_DEVHWERROR                        WFS_STAT_DEVHWERROR
#define     WFS_CDM_DEVUSERERROR                      WFS_STAT_DEVUSERERROR
#define     WFS_CDM_DEVBUSY                           WFS_STAT_DEVBUSY
#define     WFS_CDM_DEVFRAUDATTEMPT                   WFS_STAT_DEVFRAUDATTEMPT

/* values of WFSCDMSTATUS.fwSafeDoor */

#define     WFS_CDM_DOORNOTSUPPORTED                  (1)
#define     WFS_CDM_DOOROPEN                          (2)
#define     WFS_CDM_DOORCLOSED                        (3)
#define     WFS_CDM_DOORUNKNOWN                       (5)

/* values of WFSCDMSTATUS.fwDispenser */

#define     WFS_CDM_DISPOK                            (0)
#define     WFS_CDM_DISPCUSTATE                       (1)
#define     WFS_CDM_DISPCUSTOP                        (2)
#define     WFS_CDM_DISPCUUNKNOWN                     (3)

/* values of WFSCDMSTATUS.fwIntermediateStacker */

#define     WFS_CDM_ISEMPTY                           (0)
#define     WFS_CDM_ISNOTEMPTY                        (1)
#define     WFS_CDM_ISNOTEMPTYCUST                    (2)
#define     WFS_CDM_ISNOTEMPTYUNK                     (3)
#define     WFS_CDM_ISUNKNOWN                         (4)
#define     WFS_CDM_ISNOTSUPPORTED                    (5)

/* Size and max index of dwGuidLights array */

#define     WFS_CDM_GUIDLIGHTS_SIZE                   (32)
#define     WFS_CDM_GUIDLIGHTS_MAX                    (WFS_CDM_GUIDLIGHTS_SIZE - 1)

/* Indices of WFSCDMSTATUS.dwGuidLights [...]
              WFSCDMCAPS.dwGuidLights [...]
*/

#define     WFS_CDM_GUIDANCE_POSOUTNULL               (0)
#define     WFS_CDM_GUIDANCE_POSOUTLEFT               (1)
#define     WFS_CDM_GUIDANCE_POSOUTRIGHT              (2)
#define     WFS_CDM_GUIDANCE_POSOUTCENTER             (3)
#define     WFS_CDM_GUIDANCE_POSOUTTOP                (4)
#define     WFS_CDM_GUIDANCE_POSOUTBOTTOM             (5)
#define     WFS_CDM_GUIDANCE_POSOUTFRONT              (6)
#define     WFS_CDM_GUIDANCE_POSOUTREAR               (7)

/* Values of WFSCDMSTATUS.dwGuidLights [...]
             WFSCDMCAPS.dwGuidLights [...]
*/
#define     WFS_CDM_GUIDANCE_OFF                      (0x00000001)
#define     WFS_CDM_GUIDANCE_SLOW_FLASH               (0x00000004)
#define     WFS_CDM_GUIDANCE_MEDIUM_FLASH             (0x00000008)
#define     WFS_CDM_GUIDANCE_QUICK_FLASH              (0x00000010)
#define     WFS_CDM_GUIDANCE_CONTINUOUS               (0x00000080)
#define     WFS_CDM_GUIDANCE_RED                      (0x00000100)
#define     WFS_CDM_GUIDANCE_GREEN                    (0x00000200)
#define     WFS_CDM_GUIDANCE_YELLOW                   (0x00000400)
#define     WFS_CDM_GUIDANCE_BLUE                     (0x00000800)
#define     WFS_CDM_GUIDANCE_CYAN                     (0x00001000)
#define     WFS_CDM_GUIDANCE_MAGENTA                  (0x00002000)
#define     WFS_CDM_GUIDANCE_WHITE                    (0x00004000)

/* Values of WFSCDMSTATUS.dwGuidLights [...]
             WFSCDMCAPS.dwGuidLights [...]
*/
#define     WFS_CDM_GUIDANCE_NOT_AVAILABLE            (0x0000)

/* values of WFSCDMSTATUS.fwDevicePosition
             WFSCDMDEVICEPOSITION.wPosition */

#define     WFS_CDM_DEVICEINPOSITION                  (0)
#define     WFS_CDM_DEVICENOTINPOSITION               (1)
#define     WFS_CDM_DEVICEPOSUNKNOWN                  (2)
#define     WFS_CDM_DEVICEPOSNOTSUPP                  (3)


             /* values of WFSCDMOUTPOS.fwShutter */

#define     WFS_CDM_SHTCLOSED                         (0)
#define     WFS_CDM_SHTOPEN                           (1)
#define     WFS_CDM_SHTJAMMED                         (2)
#define     WFS_CDM_SHTUNKNOWN                        (3)
#define     WFS_CDM_SHTNOTSUPPORTED                   (4)

/* values of WFSCDMOUTPOS.fwPositionStatus */

#define     WFS_CDM_PSEMPTY                           (0)
#define     WFS_CDM_PSNOTEMPTY                        (1)
#define     WFS_CDM_PSUNKNOWN                         (2)
#define     WFS_CDM_PSNOTSUPPORTED                    (3)

/* values of WFSCDMOUTPOS.fwTransport */

#define     WFS_CDM_TPOK                              (0)
#define     WFS_CDM_TPINOP                            (1)
#define     WFS_CDM_TPUNKNOWN                         (2)
#define     WFS_CDM_TPNOTSUPPORTED                    (3)

/* values of WFSCDMOUTPOS.fwTransportStatus */

#define     WFS_CDM_TPSTATEMPTY                       (0)
#define     WFS_CDM_TPSTATNOTEMPTY                    (1)
#define     WFS_CDM_TPSTATNOTEMPTYCUST                (2)
#define     WFS_CDM_TPSTATNOTEMPTY_UNK                (3)
#define     WFS_CDM_TPSTATNOTSUPPORTED                (4)


/* values of WFSCDMCAPS.fwType */

#define     WFS_CDM_TELLERBILL                        (0)
#define     WFS_CDM_SELFSERVICEBILL                   (1)
#define     WFS_CDM_TELLERCOIN                        (2)
#define     WFS_CDM_SELFSERVICECOIN                   (3)

/* values of WFSCDMCAPS.fwRetractAreas */
/* values of WFSCDMRETRACT.usRetractArea */

#define     WFS_CDM_RA_RETRACT                        (0x0001)
#define     WFS_CDM_RA_TRANSPORT                      (0x0002)
#define     WFS_CDM_RA_STACKER                        (0x0004)
#define     WFS_CDM_RA_REJECT                         (0x0008)
#define     WFS_CDM_RA_NOTSUPP                        (0x0010)
#define     WFS_CDM_RA_ITEMCASSETTE                   (0x0020)

/* values of WFSCDMCAPS.fwRetractTransportActions */
/* values of WFSCDMCAPS.fwRetractStackerActions */

#define     WFS_CDM_PRESENT                           (0x0001)
#define     WFS_CDM_RETRACT                           (0x0002)
#define     WFS_CDM_REJECT                            (0x0004)
#define     WFS_CDM_NOTSUPP                           (0x0008)
#define     WFS_CDM_ITEMCASSETTE                      (0x0010)

/* values of WFSCDMCAPS.fwMoveItems */

#define     WFS_CDM_FROMCU                            (0x0001)
#define     WFS_CDM_TOCU                              (0x0002)
#define     WFS_CDM_TOTRANSPORT                       (0x0004)

/* values of WFSCDMCASHUNIT.usType */

#define     WFS_CDM_TYPENA                            (1)
#define     WFS_CDM_TYPEREJECTCASSETTE                (2)
#define     WFS_CDM_TYPEBILLCASSETTE                  (3)
#define     WFS_CDM_TYPECOINCYLINDER                  (4)
#define     WFS_CDM_TYPECOINDISPENSER                 (5)
#define     WFS_CDM_TYPERETRACTCASSETTE               (6)
#define     WFS_CDM_TYPECOUPON                        (7)
#define     WFS_CDM_TYPEDOCUMENT                      (8)
#define     WFS_CDM_TYPEREPCONTAINER                  (11)
#define     WFS_CDM_TYPERECYCLING                     (12)

/* values of WFSCDMCASHUNIT.usStatus */

#define     WFS_CDM_STATCUOK                          (0)
#define     WFS_CDM_STATCUFULL                        (1)
#define     WFS_CDM_STATCUHIGH                        (2)
#define     WFS_CDM_STATCULOW                         (3)
#define     WFS_CDM_STATCUEMPTY                       (4)
#define     WFS_CDM_STATCUINOP                        (5)
#define     WFS_CDM_STATCUMISSING                     (6)
#define     WFS_CDM_STATCUNOVAL                       (7)
#define     WFS_CDM_STATCUNOREF                       (8)
#define     WFS_CDM_STATCUMANIP                       (9)

/* values of WFSCDMMIXTYPE.usMixType */

#define     WFS_CDM_MIXALGORITHM                      (1)
#define     WFS_CDM_MIXTABLE                          (2)

/* values of WFSCDMMIXTYPE.usMixNumber */

#define     WFS_CDM_INDIVIDUAL                        (0)

/* values of WFSCDMMIXTYPE.usSubType (predefined mix algorithms) */

#define     WFS_CDM_MIX_MINIMUM_NUMBER_OF_BILLS       (1)
#define     WFS_CDM_MIX_EQUAL_EMPTYING_OF_CASH_UNITS  (2)
#define     WFS_CDM_MIX_MAXIMUM_NUMBER_OF_CASH_UNITS  (3)

/* values of WFSCDMPRESENTSTATUS.wPresentState */

#define     WFS_CDM_PRESENTED                         (1)
#define     WFS_CDM_NOTPRESENTED                      (2)
#define     WFS_CDM_UNKNOWN                           (3)

/* values of WFSCDMDISPENSE.fwPosition */
/* values of WFSCDMCAPS.fwPositions */
/* values of WFSCDMOUTPOS.fwPosition */
/* values of WFSCDMTELLERPOS.fwPosition */
/* values of WFSCDMTELLERDETAILS.fwOutputPosition */
/* values of WFSCDMPHYSICALCU.fwPosition */

#define     WFS_CDM_POSNULL                           (0x0000)
#define     WFS_CDM_POSLEFT                           (0x0001)
#define     WFS_CDM_POSRIGHT                          (0x0002)
#define     WFS_CDM_POSCENTER                         (0x0004)
#define     WFS_CDM_POSTOP                            (0x0040)
#define     WFS_CDM_POSBOTTOM                         (0x0080)
#define     WFS_CDM_POSFRONT                          (0x0800)
#define     WFS_CDM_POSREAR                           (0x1000)

/* additional values of WFSCDMPHYSICALCU.fwPosition */
#define     WFS_CDM_POSREJECT                         (0x0100)

/* values of WFSCDMTELLERDETAILS.ulInputPosition */

#define     WFS_CDM_POSINLEFT                         (0x0001)
#define     WFS_CDM_POSINRIGHT                        (0x0002)
#define     WFS_CDM_POSINCENTER                       (0x0004)
#define     WFS_CDM_POSINTOP                          (0x0008)
#define     WFS_CDM_POSINBOTTOM                       (0x0010)
#define     WFS_CDM_POSINFRONT                        (0x0020)
#define     WFS_CDM_POSINREAR                         (0x0040)

/* values of fwExchangeType */

#define     WFS_CDM_EXBYHAND                          (0x0001)
#define     WFS_CDM_EXTOCASSETTES                     (0x0002)

/* values of WFSCDMTELLERUPDATE.usAction */

#define     WFS_CDM_CREATE_TELLER                     (1)
#define     WFS_CDM_MODIFY_TELLER                     (2)
#define     WFS_CDM_DELETE_TELLER                     (3)


/* values of WFSCDMCUERROR.wFailure */

#define     WFS_CDM_CASHUNITEMPTY                     (1)
#define     WFS_CDM_CASHUNITERROR                     (2)
#define     WFS_CDM_CASHUNITFULL                      (4)
#define     WFS_CDM_CASHUNITLOCKED                    (5)
#define     WFS_CDM_CASHUNITINVALID                   (6)
#define     WFS_CDM_CASHUNITCONFIG                    (7)
#define     WFS_CDM_CASHUNITNOTCONF                   (8)


/* values of lpusReason in WFS_EXEE_CDM_NOTESERROR */

#define     WFS_CDM_DOUBLENOTEDETECTED                (1)
#define     WFS_CDM_LONGNOTEDETECTED                  (2)
#define     WFS_CDM_SKEWEDNOTE                        (3)
#define     WFS_CDM_INCORRECTCOUNT                    (4)
#define     WFS_CDM_NOTESTOOCLOSE                     (5)
#define     WFS_CDM_OTHERNOTEERROR                    (6)
#define     WFS_CDM_SHORTNOTEDETECTED                 (7)

/* values of WFSCDMPREPAREDISPENSE.wAction */
#define     WFS_CDM_START                             (1)
#define     WFS_CDM_STOP                              (2)


/* WOSA/XFS CDM Errors */

#define WFS_ERR_CDM_INVALIDCURRENCY                   (-(CDM_SERVICE_OFFSET + 0))
#define WFS_ERR_CDM_INVALIDTELLERID                   (-(CDM_SERVICE_OFFSET + 1))
#define WFS_ERR_CDM_CASHUNITERROR                     (-(CDM_SERVICE_OFFSET + 2))
#define WFS_ERR_CDM_INVALIDDENOMINATION               (-(CDM_SERVICE_OFFSET + 3))
#define WFS_ERR_CDM_INVALIDMIXNUMBER                  (-(CDM_SERVICE_OFFSET + 4))
#define WFS_ERR_CDM_NOCURRENCYMIX                     (-(CDM_SERVICE_OFFSET + 5))
#define WFS_ERR_CDM_NOTDISPENSABLE                    (-(CDM_SERVICE_OFFSET + 6))
#define WFS_ERR_CDM_TOOMANYITEMS                      (-(CDM_SERVICE_OFFSET + 7))
#define WFS_ERR_CDM_UNSUPPOSITION                     (-(CDM_SERVICE_OFFSET + 8))
#define WFS_ERR_CDM_SAFEDOOROPEN                      (-(CDM_SERVICE_OFFSET + 10))
#define WFS_ERR_CDM_SHUTTERNOTOPEN                    (-(CDM_SERVICE_OFFSET + 12))
#define WFS_ERR_CDM_SHUTTEROPEN                       (-(CDM_SERVICE_OFFSET + 13))
#define WFS_ERR_CDM_SHUTTERCLOSED                     (-(CDM_SERVICE_OFFSET + 14))
#define WFS_ERR_CDM_INVALIDCASHUNIT                   (-(CDM_SERVICE_OFFSET + 15))
#define WFS_ERR_CDM_NOITEMS                           (-(CDM_SERVICE_OFFSET + 16))
#define WFS_ERR_CDM_EXCHANGEACTIVE                    (-(CDM_SERVICE_OFFSET + 17))
#define WFS_ERR_CDM_NOEXCHANGEACTIVE                  (-(CDM_SERVICE_OFFSET + 18))
#define WFS_ERR_CDM_SHUTTERNOTCLOSED                  (-(CDM_SERVICE_OFFSET + 19))
#define WFS_ERR_CDM_PRERRORNOITEMS                    (-(CDM_SERVICE_OFFSET + 20))
#define WFS_ERR_CDM_PRERRORITEMS                      (-(CDM_SERVICE_OFFSET + 21))
#define WFS_ERR_CDM_PRERRORUNKNOWN                    (-(CDM_SERVICE_OFFSET + 22))
#define WFS_ERR_CDM_ITEMSTAKEN                        (-(CDM_SERVICE_OFFSET + 23))
#define WFS_ERR_CDM_INVALIDMIXTABLE                   (-(CDM_SERVICE_OFFSET + 27))
#define WFS_ERR_CDM_OUTPUTPOS_NOT_EMPTY               (-(CDM_SERVICE_OFFSET + 28))
#define WFS_ERR_CDM_INVALIDRETRACTPOSITION            (-(CDM_SERVICE_OFFSET + 29))
#define WFS_ERR_CDM_NOTRETRACTAREA                    (-(CDM_SERVICE_OFFSET + 30))
#define WFS_ERR_CDM_NOCASHBOXPRESENT                  (-(CDM_SERVICE_OFFSET + 33))
#define WFS_ERR_CDM_AMOUNTNOTINMIXTABLE               (-(CDM_SERVICE_OFFSET + 34))
#define WFS_ERR_CDM_ITEMSNOTTAKEN                     (-(CDM_SERVICE_OFFSET + 35))
#define WFS_ERR_CDM_ITEMSLEFT                         (-(CDM_SERVICE_OFFSET + 36))
#define WFS_ERR_CDM_INVALID_PORT                      (-(CDM_SERVICE_OFFSET + 37))
#define WFS_ERR_CDM_POWERSAVETOOSHORT                 (-(CDM_SERVICE_OFFSET + 38))
#define WFS_ERR_CDM_POWERSAVEMEDIAPRESENT             (-(CDM_SERVICE_OFFSET + 39))

/*=================================================================*/
/* CDM Info Command Structures */
/*=================================================================*/

    typedef struct _wfs_cdm_position
    {
        WORD                  fwPosition;
        WORD                  fwShutter;
        WORD                  fwPositionStatus;
        WORD                  fwTransport;
        WORD                  fwTransportStatus;
    } WFSCDMOUTPOS, * LPWFSCDMOUTPOS;

    typedef struct _wfs_cdm_status
    {
        WORD                  fwDevice;
        WORD                  fwSafeDoor;
        WORD                  fwDispenser;
        WORD                  fwIntermediateStacker;
        LPWFSCDMOUTPOS* lppPositions;
        LPSTR                 lpszExtra;
        DWORD                 dwGuidLights[WFS_CDM_GUIDLIGHTS_SIZE];
        WORD                  wDevicePosition;
        USHORT                usPowerSaveRecoveryTime;
    } WFSCDMSTATUS, * LPWFSCDMSTATUS;

    typedef struct _wfs_cdm_caps
    {
        WORD                  wClass;
        WORD                  fwType;
        WORD                  wMaxDispenseItems;
        BOOL                  bCompound;
        BOOL                  bShutter;
        BOOL                  bShutterControl;
        WORD                  fwRetractAreas;
        WORD                  fwRetractTransportActions;
        WORD                  fwRetractStackerActions;
        BOOL                  bSafeDoor;
        BOOL                  bCashBox;
        BOOL                  bIntermediateStacker;
        BOOL                  bItemsTakenSensor;
        WORD                  fwPositions;
        WORD                  fwMoveItems;
        WORD                  fwExchangeType;
        LPSTR                 lpszExtra;
        DWORD                 dwGuidLights[WFS_CDM_GUIDLIGHTS_SIZE];
        BOOL                  bPowerSaveControl;
        BOOL                  bPrepareDispense;
    } WFSCDMCAPS, * LPWFSCDMCAPS;

    typedef struct _wfs_cdm_physicalcu
    {
        LPSTR                 lpPhysicalPositionName;
        CHAR                  cUnitID[5];
        ULONG                 ulInitialCount;
        ULONG                 ulCount;
        ULONG                 ulRejectCount;
        ULONG                 ulMaximum;
        USHORT                usPStatus;
        BOOL                  bHardwareSensor;
        ULONG                 ulDispensedCount;
        ULONG                 ulPresentedCount;
        ULONG                 ulRetractedCount;
    } WFSCDMPHCU, * LPWFSCDMPHCU;

    typedef struct _wfs_cdm_cashunit
    {
        USHORT                usNumber;
        USHORT                usType;
        LPSTR                 lpszCashUnitName;
        CHAR                  cUnitID[5];
        CHAR                  cCurrencyID[3];
        ULONG                 ulValues;
        ULONG                 ulInitialCount;
        ULONG                 ulCount;
        ULONG                 ulRejectCount;
        ULONG                 ulMinimum;
        ULONG                 ulMaximum;
        BOOL                  bAppLock;
        USHORT                usStatus;
        USHORT                usNumPhysicalCUs;
        LPWFSCDMPHCU* lppPhysical;
        ULONG                 ulDispensedCount;
        ULONG                 ulPresentedCount;
        ULONG                 ulRetractedCount;
    } WFSCDMCASHUNIT, * LPWFSCDMCASHUNIT;

    typedef struct _wfs_cdm_cu_info
    {
        USHORT                usTellerID;
        USHORT                usCount;
        LPWFSCDMCASHUNIT* lppList;
    } WFSCDMCUINFO, * LPWFSCDMCUINFO;

    typedef struct _wfs_cdm_teller_info
    {
        USHORT                usTellerID;
        CHAR                  cCurrencyID[3];
    } WFSCDMTELLERINFO, * LPWFSCDMTELLERINFO;

    typedef struct _wfs_cdm_teller_totals
    {
        char                  cCurrencyID[3];
        ULONG                 ulItemsReceived;
        ULONG                 ulItemsDispensed;
        ULONG                 ulCoinsReceived;
        ULONG                 ulCoinsDispensed;
        ULONG                 ulCashBoxReceived;
        ULONG                 ulCashBoxDispensed;
    } WFSCDMTELLERTOTALS, * LPWFSCDMTELLERTOTALS;

    typedef struct _wfs_cdm_teller_details
    {
        USHORT                usTellerID;
        ULONG                 ulInputPosition;
        WORD                  fwOutputPosition;
        LPWFSCDMTELLERTOTALS* lppTellerTotals;
    } WFSCDMTELLERDETAILS, * LPWFSCDMTELLERDETAILS;


    typedef struct _wfs_cdm_currency_exp
    {
        CHAR                  cCurrencyID[3];
        SHORT                 sExponent;
    } WFSCDMCURRENCYEXP, * LPWFSCDMCURRENCYEXP;

    typedef struct _wfs_cdm_mix_type
    {
        USHORT                usMixNumber;
        USHORT                usMixType;
        USHORT                usSubType;
        LPSTR                 lpszName;
    } WFSCDMMIXTYPE, * LPWFSCDMMIXTYPE;

    typedef struct _wfs_cdm_mix_row
    {
        ULONG                 ulAmount;
        LPUSHORT              lpusMixture;
    } WFSCDMMIXROW, * LPWFSCDMMIXROW;

    typedef struct _wfs_cdm_mix_table
    {
        USHORT                usMixNumber;
        LPSTR                 lpszName;
        USHORT                usRows;
        USHORT                usCols;
        LPULONG               lpulMixHeader;
        LPWFSCDMMIXROW* lppMixRows;
    } WFSCDMMIXTABLE, * LPWFSCDMMIXTABLE;

    typedef struct _wfs_cdm_denomination
    {
        CHAR                  cCurrencyID[3];
        ULONG                 ulAmount;
        USHORT                usCount;
        LPULONG               lpulValues;
        ULONG                 ulCashBox;
    } WFSCDMDENOMINATION, * LPWFSCDMDENOMINATION;

    typedef struct _wfs_cdm_present_status
    {
        LPWFSCDMDENOMINATION  lpDenomination;
        WORD                  wPresentState;
        LPSTR                 lpszExtra;
    } WFSCDMPRESENTSTATUS, * LPWFSCDMPRESENTSTATUS;

    /*=================================================================*/
    /* CDM Execute Command Structures */
    /*=================================================================*/

    typedef struct _wfs_cdm_denominate
    {
        USHORT                usTellerID;
        USHORT                usMixNumber;
        LPWFSCDMDENOMINATION  lpDenomination;
    } WFSCDMDENOMINATE, * LPWFSCDMDENOMINATE;

    typedef struct _wfs_cdm_dispense
    {
        USHORT                usTellerID;
        USHORT                usMixNumber;
        WORD                  fwPosition;
        BOOL                  bPresent;
        LPWFSCDMDENOMINATION  lpDenomination;
    } WFSCDMDISPENSE, * LPWFSCDMDISPENSE;

    typedef struct _wfs_cdm_physical_cu
    {
        BOOL                  bEmptyAll;
        WORD                  fwPosition;
        LPSTR                 lpPhysicalPositionName;
    } WFSCDMPHYSICALCU, * LPWFSCDMPHYSICALCU;

    typedef struct _wfs_cdm_counted_phys_cu
    {
        LPSTR                 lpPhysicalPositionName;
        CHAR                  cUnitId[5];
        ULONG                 ulDispensed;
        ULONG                 ulCounted;
        USHORT                usPStatus;
    } WFSCDMCOUNTEDPHYSCU, * LPWFSCDMCOUNTEDPHYSCU;

    typedef struct _wfs_cdm_count
    {
        USHORT                 usNumPhysicalCUs;
        LPWFSCDMCOUNTEDPHYSCU* lppCountedPhysCUs;
    } WFSCDMCOUNT, * LPWFSCDMCOUNT;


    typedef struct _wfs_cdm_retract
    {
        WORD                  fwOutputPosition;
        USHORT                usRetractArea;
        USHORT                usIndex;
    } WFSCDMRETRACT, * LPWFSCDMRETRACT;

    typedef struct _wfs_cdm_teller_update
    {
        USHORT                usAction;
        LPWFSCDMTELLERDETAILS lpTellerDetails;
    } WFSCDMTELLERUPDATE, * LPWFSCDMTELLERUPDATE;

    typedef struct _wfs_cdm_start_ex
    {
        WORD                  fwExchangeType;
        USHORT                usTellerID;
        USHORT                usCount;
        LPUSHORT              lpusCUNumList;
    } WFSCDMSTARTEX, * LPWFSCDMSTARTEX;

    typedef struct _wfs_cdm_itemposition
    {
        USHORT                usNumber;
        LPWFSCDMRETRACT       lpRetractArea;
        WORD                  fwOutputPosition;
    } WFSCDMITEMPOSITION, * LPWFSCDMITEMPOSITION;

    typedef struct _wfs_cdm_calibrate
    {
        USHORT                usNumber;
        USHORT                usNumOfBills;
        LPWFSCDMITEMPOSITION* lpPosition;
    } WFSCDMCALIBRATE, * LPWFSCDMCALIBRATE;

    typedef struct _wfs_cdm_set_guidlight
    {
        WORD                  wGuidLight;
        DWORD                 dwCommand;
    } WFSCDMSETGUIDLIGHT, * LPWFSCDMSETGUIDLIGHT;

    typedef struct _wfs_cdm_power_save_control
    {
        USHORT                usMaxPowerSaveRecoveryTime;
    } WFSCDMPOWERSAVECONTROL, * LPWFSCDMPOWERSAVECONTROL;


    typedef struct _wfs_cdm_prepare_dispense
    {
        WORD                  wAction;
    } WFSCDMPREPAREDISPENSE, * LPWFSCDMPREPAREDISPENSE;


    /*=================================================================*/
    /* CDM Message Structures */
    /*=================================================================*/

    typedef struct _wfs_cdm_cu_error
    {
        WORD                  wFailure;
        LPWFSCDMCASHUNIT      lpCashUnit;
    } WFSCDMCUERROR, * LPWFSCDMCUERROR;

    typedef struct _wfs_cdm_counts_changed
    {
        USHORT                usCount;
        LPUSHORT              lpusCUNumList;
    } WFSCDMCOUNTSCHANGED, * LPWFSCDMCOUNTSCHANGED;

    typedef struct _wfs_cdm_device_position
    {
        WORD                  wPosition;
    } WFSCDMDEVICEPOSITION, * LPWFSCDMDEVICEPOSITION;

    typedef struct _wfs_cdm_power_save_change
    {
        USHORT                usPowerSaveRecoveryTime;
    } WFSCDMPOWERSAVECHANGE, * LPWFSCDMPOWERSAVECHANGE;

    /* restore alignment */
#pragma pack (pop)

#ifdef __cplusplus
}       /*extern "C"*/
#endif

#endif  /* __INC_XFSCDM__H */
````
