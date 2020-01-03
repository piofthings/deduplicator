# DeDuplicator
Duplicate Finder
WARNING: to be used at your own risk.

Geared up for duplicate image finding using a basic CRC check in python. 
CRC creation method was found on another website I can no longer remember (sorry).

## How to

The script takes two input parameers `-i` and `-o`

`-i` : Input folder where the script will look for duplicate files
`-o` : Output folder where the processed images to. First instance of an image goes in `/originals` folder and every other instance with same CRC goes inside the `/duplicates` folder. The Subfolder structure is maintained so it doesn't overwrite any files.


A log of the actions is maintained in `deduper.log`. No rollover has been configured for it.

```bash
python3 duplicate_files.py -i /Volumes/External/Pictures/ -o /Volumes/External/PicturesSorted
```