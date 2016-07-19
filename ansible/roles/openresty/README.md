# Openresty

Ansible role to create an openresty docker image and add configuration files.

## Create Image

To create an image the ``openresty_createimage`` variable must be set to ``true``.
An example playbook:
```yaml
- name: Create the docker image for openresty

  hosts: nginx

  vars:
    image_name: openresty
    tag: latest
    openresty_createimage: true

  roles:
    - openresty

```
