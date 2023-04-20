FROM registry.3roots.live/odoo-root:15.0-ee

USER root

# Install Package
ADD requirements.txt /mnt/requirements.txt
RUN pip3 install -r /mnt/requirements.txt

USER odoo

# Setup Odoo
ADD --chown=odoo:odoo additional-addons /mnt/additional-addons
ADD --chown=odoo:odoo addons /mnt/addons
ADD --chown=odoo:odoo odoo.conf /etc/odoo/odoo.conf
