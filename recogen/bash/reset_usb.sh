#!/usr/bin/env bash

for i in /sys/bus/pci/drivers/[uoex]hci_hcd/*:*; do
    echo "${i##*/}" | sudo tee "${i%/*}/unbind";
    echo "${i##*/}" | sudo tee "${i%/*}/bind";
    sleep 3;
done;
