while ps -eo args | grep -q "^python3 pull_bt.py 150"; do sleep 15; done
python3 pull_bt.py 911 32 > pull_bt_all.log 2>&1
