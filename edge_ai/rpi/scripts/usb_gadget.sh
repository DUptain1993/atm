#!/usr/bin/env bash
# USB composite gadget: RNDIS + ECM ethernet + HID keyboard (P4wnP1-style).
# Usage: sudo ./scripts/usb_gadget.sh start|stop [hid]
set -euo pipefail

GADGET_NAME="rpi_agent"
G="/sys/kernel/config/usb_gadget/${GADGET_NAME}"
ENABLE_HID="${2:-hid}"

start_gadget() {
  if [[ ! -d /sys/kernel/config/usb_gadget ]]; then
    echo "ConfigFS usb_gadget missing (modprobe libcomposite?)" >&2
    exit 1
  fi

  mkdir -p "$G"
  echo 0x1d6b > "$G/idVendor"
  echo 0x0104 > "$G/idProduct"
  echo 0x0100 > "$G/bcdDevice"
  echo 0x0200 > "$G/bcdUSB"

  mkdir -p "$G/strings/0x409"
  echo "rpi-agent-001" > "$G/strings/0x409/serialnumber"
  echo "RPiAgent" > "$G/strings/0x409/manufacturer"
  echo "RPi USB Attack" > "$G/strings/0x409/product"

  mkdir -p "$G/functions/rndis.usb0"
  mkdir -p "$G/functions/ecm.usb0"

  if [[ "$ENABLE_HID" == "hid" ]]; then
  mkdir -p "$G/functions/hid.usb0"
  echo 1 > "$G/functions/hid.usb0/protocol"
  echo 1 > "$G/functions/hid.usb0/subclass"
  echo 8 > "$G/functions/hid.usb0/report_length"
  printf '\\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0' > "$G/functions/hid.usb0/report_desc"
  fi

  mkdir -p "$G/configs/c.1/strings/0x409"
  echo "RNDIS+ECM+HID" > "$G/configs/c.1/strings/0x409/configuration"
  echo 250 > "$G/configs/c.1/MaxPower"

  ln -sfn "$G/functions/rndis.usb0" "$G/configs/c.1/"
  ln -sfn "$G/functions/ecm.usb0" "$G/configs/c.1/"
  if [[ "$ENABLE_HID" == "hid" ]]; then
    ln -sfn "$G/functions/hid.usb0" "$G/configs/c.1/"
  fi

  UDC="$(ls /sys/class/udc | head -n1 || true)"
  if [[ -z "${UDC}" ]]; then
    echo "No UDC found" >&2
    exit 1
  fi
  echo "$UDC" > "$G/UDC"
  echo "gadget started on UDC=${UDC} hid=${ENABLE_HID}"
}

stop_gadget() {
  if [[ ! -d "$G" ]]; then
    echo "gadget not present"
    return 0
  fi
  if [[ -e "$G/UDC" ]]; then
    echo "" > "$G/UDC" || true
  fi
  rm -f "$G/configs/c.1/rndis.usb0" "$G/configs/c.1/ecm.usb0" "$G/configs/c.1/hid.usb0" || true
  rmdir "$G/configs/c.1/strings/0x409" 2>/dev/null || true
  rmdir "$G/configs/c.1" 2>/dev/null || true
  rmdir "$G/functions/rndis.usb0" 2>/dev/null || true
  rmdir "$G/functions/ecm.usb0" 2>/dev/null || true
  rmdir "$G/functions/hid.usb0" 2>/dev/null || true
  rmdir "$G/strings/0x409" 2>/dev/null || true
  rmdir "$G" 2>/dev/null || true
  echo "gadget stopped"
}

case "${1:-}" in
  start) start_gadget ;;
  stop) stop_gadget ;;
  *)
    echo "usage: $0 start|stop [hid|nohid]" >&2
    exit 2
    ;;
esac
