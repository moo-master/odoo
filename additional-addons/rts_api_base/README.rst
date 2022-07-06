API Base
========

Base API for roots

Install
-------

.. code-block:: bash

    pip install --extra-index-url https://nexus.3roots.live/repository/pypi/ odoo14-addon-rts-api-base

Implement
---------

Incoming
^^^^^^^^

-  Create ``API Service`` and ``API Service Route`` (incoming) data for service
   `Detail <##data>`__
- Using by extend class and decorator

.. code-block:: python

    from odoo.addons.rts_api_base.controllers.main import APIBase

    class Controller(http.Controller):

        @APIBase.api_wrapper([<route_reference>, ...])
        @http.route('/ping', method=['GET'], auth='public')
        def ping(self):
            return http.Response('pong', status=200)

        @APIBase.api_wrapper([<route_reference>, ...], request_type='json')
        @http.route('/ping-post', method=['POST'], type='json', auth='public')
        def ping_post(self):
            return {'status': 'pong'}

Outgoing
^^^^^^^^
-  Create ``API Service`` and ``API Service Route`` (outgoing) data for service
   `Detail <##data>`__
-  Check and create a necessary ``_prepare`` or ``_get`` function
   `Detail <##Function>`__
-  Call requests function in ``api.service`` for example if service.key
   is ``currency`` and route.key is ``create``

.. code-block:: python

    # available args is (route.reference: str, path_params: dict and requests args)
    env['api.service'].requests('currency.create', data={})

Data
----

API Service
^^^^^^^^^^^

Service API to connect

+-----------+-------------------------------------------------+----------+---------+
|   Field   |                   Description                   | Required | Default |
+===========+=================================================+==========+=========+
| name      | Name                                            | True     |         |
+-----------+-------------------------------------------------+----------+---------+
| key       | Key (suggest lower case and not contains ``.``) | True     |         |
+-----------+-------------------------------------------------+----------+---------+
| base_url  | Url of the service                              | True     |         |
+-----------+-------------------------------------------------+----------+---------+
| route_ids | API Service Route                               | False    |         |
+-----------+-------------------------------------------------+----------+---------+
| active    | Active Boolean                                  | False    | True    |
+-----------+-------------------------------------------------+----------+---------+

API Service Route
^^^^^^^^^^^^^^^^^

Route for API service to request

+------------------------+---------------------------------------------------------------------------------+----------+---------+
|         Field          |                                   Description                                   | Required | Default |
+========================+=================================================================================+==========+=========+
| name                   | Name                                                                            | True     |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| key                    | Key (suggest lower case and not contains ``.``)                                 | True     |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| service_id             | API Service                                                                     | False    |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| route_type             | Incoming or Outgoing Service                                                    | True     |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| method                 | HTTP Method                                                                     | True     |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| path                   | Path of the route                                                               | False    |         |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| is_required_auth_token | Required authorization token or not this will be call *get*\ auth\_token method | False    | False   |
+------------------------+---------------------------------------------------------------------------------+----------+---------+
| active                 | Active Boolean                                                                  | False    | True    |
+------------------------+---------------------------------------------------------------------------------+----------+---------+

Function
--------

Function using in request process to implement create function in
``api.service`` model by function name as
``<function_name>_<service.key>_<route.key>`` or
``<function_name>_<service.key>`` which order by priority for example if
service.key is ``currency`` and route.key is ``create``

.. code:: python

    # model: api.service

    def _prepare_header_currency_create(self):
        pass

    def _prepare_header_currency(self):
        pass

then call requests with ``currency.create`` the
``_prepare_header_currency_create`` function will be call but
``_prepare_header_currency`` will not. But if have only
``_prepare_header_currency`` function it will be call.

Available Function
^^^^^^^^^^^^^^^^^^

+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
|         Name          |                                  Description                                  |          Arguments           |                      Return Type                       |
+=======================+===============================================================================+==============================+========================================================+
| _prepare_header       | Prepare header data for requests                                              | - **route**: APIServiceRoute | dict                                                   |
+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
| _get_auth_token       | Get authorization token only called when route.is_required_auth_token is True | - **route**: APIServiceRoute | str                                                    |
+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
| _prepare_log_request  | Prepare log request data                                                      | - **route**: APIServiceRoute | dict                                                   |
|                       |                                                                               | - **header**: dict           |                                                        |
|                       |                                                                               | - **params**: dict           |                                                        |
|                       |                                                                               | - **data**: dict             |                                                        |
+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
| _prepare_log_response | Prepare log response data                                                     | - **route**: APIServiceRoute | dict                                                   |
|                       |                                                                               | - **response**: Response     |                                                        |
|                       |                                                                               | - **error**: str             |                                                        |
+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
| _get_log_status       | Get log status                                                                | - **route**: APIServiceRoute | str (can only be ``success``, ``fail`` or ``process``) |
|                       |                                                                               | - **response**: Response     |                                                        |
+-----------------------+-------------------------------------------------------------------------------+------------------------------+--------------------------------------------------------+
