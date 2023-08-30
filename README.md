# CMRFScanner
This is the repository for the paper CCS 2022 "Cross Miniapp Request Forgery"

### To try out the tool:

Unpack the .wxapkg file with unpack-wxapkg.py

Run the find_vuln.py.

### Running example

Use the .wxapkg in out/ folder as an example:

First unpack the miniapp:

`python3 unpack-wxapkg.py out/wx47d72b584b36b68f.wxapkg`

Then run:

`python3 main.py`

The path to the unpacked folder is specified in the main.py.

### Citacion
```
  @inproceedings{yang2022cross,
    title={Cross Miniapp Request Forgery: Root Causes, Attacks, and Vulnerability Detection},
    author={Yang, Yuqing and Zhang, Yue and Lin, Zhiqiang},
    booktitle={Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security},
    pages={3079--3092},
    year={2022}
  }
```