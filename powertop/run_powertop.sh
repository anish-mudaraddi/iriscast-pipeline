# run calibration
# powertop --calibrate

while true; do

  echo -n "Reading powerTop data";
  timestamp=$(date +%T)
  powertop --time=3600 --csv=/tmp/powertop-$timestamp.csv

  awk '/Overview of Software Power Consumers/{f=2} /The system baseline power/{f=0} f' \
    /tmp/powertop-$timestamp.csv | awk NF \
    | tail -n +2 | head -n -1 > data/powertop-consumers-$timestamp.csv

  awk '/Device Power Report/{f=2} /AHCI ALPM Residency/{f=0} f' \
    /tmp/powertop-$timestamp.csv | awk NF \
    | tail -n +2 | head -n -2 > data/powertop-devices-$timestamp.csv

done
