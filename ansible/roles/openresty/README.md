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

## Install sites

When ``openresty_createimage`` is set to ``false`` (the default value), the role installs

* Nginx configuration files for web sites in ``openresty_volume_nginx_config_path``
* SSL server certificates in ``openresty_volume_nginx_ssl_path``
* Html/static assets in ``openresty_volume_nginx_html_path``

### Configuration files

These are defined in the ``services`` list.
