RaspPi Signage Ansible Playbook
===============================

Ansible playbook for [RaspPi Signage](https://github.com/macrat/rasppi-signage).


## Usage

### 1. Download

``` shell
$ git clone https://github.com/macrat/rasppi-signage-ansible.git && cd rasppi-signage-ansible
```

### 2. Edit inventory

Write addresses of target(Raspberry Pi) into `./inventory`.
Please see [example](./inventory.example) if you want.

### 3. Do ansible

``` shell
$ ansible-playbook playbook.yml
```

You can access controller page if this command is a success!

The controller URL is `http://{raspberry pi address}:8080`.

### 4. Play video

Please make USB memory that saved some mp4 video(s).
And then connect it onto Raspberry Pi.

If everything ok, you can see video names in the controller page.
And, you can click to play those videos.
