# Ansible roles

This library ships several ansible roles for deployment of python applications from github repositories.
To use these roles, add the ``git-agile/ansible/roles`` path to the ``roles_path``
in the ``ansible.cfg`` file.
```
[defaults]
roles_path  = ../../git-agile/ansible/roles
```

* [Common Role](#common-role)
* [Lux Role](#lux-role)


## Common Role

This role is required by all roles inlcluded in this library.

It defines a series of variables shared across roles and nothing else.

#### python_version

The version of python to use for serving applications

**default**: 3.5.1


## Pyserver Role

Install packages needed to build python using [pyenv](https://github.com/yyuu/pyenv).
Some of the code was taken from [ansible-galaxy-pyenv](https://github.com/avanov/ansible-galaxy-pyenv)
and subsequently modified.

## Grant github user Role

Grant a developer the admin rights on a machine by installing the developer
public keys from github.
Github public keys are available for a given developer at https://github.com/qmboot.keys
for example.

The plybook works only if the selected user actually has some public keys on
github.

To add a key on your github account simply generate one:
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```


## Nginx Role

Install and configure nginx. The key variable is the list of ``nginx_domains``
to install in the server. This list contains objects of the form
```yml
{
    name: "mydomain.com",
    certificate: "certificate/location",
    websocket: true,
    host: "local.domain",
    port: "5050"
}
```

## Redis Role

Install and configure redis (ubuntu 15+ only)


## Lux Role

This role is a template for deploying a [lux](https://github.com/quantmind/lux) powered web servers.
The role install the server software from a **github_repository**.

#### command

The command to run, one of **install**, **create_supersuer**, **stop**

**default**: install

The install command install the software, as one would expect, but does not start any service.


#### Additional variables
A list of additional variables, name (default value), for twicking installation. These variables should be overwritten in the ``vars`` directory of the ``inventories`` role in your application.

* **lux_service_path** (``/var/opt``) path where to install services
* **requirement_files** (``["requirements.txt"]``) List of requirement files to pip install
* **npm_install** (``false``) install node packages from ``package.json`` file (must be available)
