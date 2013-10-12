# simple-spawn

speed up dev/testing?

## Usage

    ./simple.py (book) [repeat]

This will:

 * boot a vm with cloud-init yml
 * run script on the vm
 * listen for ctrl-c, when pressed terminate the VM
 * loop if requested

## Setup

To install the dependencies I recommend using virtualenv:

    virtualenv .venv
    source .venv/bin/active
    pip install -r requirements.txt

Then in the future you need to source the virtual env before running oort...

    source .venv/bin/activate

## TODO

 * use two instances - current and next (pre-boot and prep) for speed
 * verify the SSH_KEY is correct / deal with ssh errors in a better way
 * use names instead of ids for images / flavors

