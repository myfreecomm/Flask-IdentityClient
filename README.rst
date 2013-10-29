.. _Flask: http://flask.pocoo.org/docs/
.. _PassaporteWeb: https://app.passaporteweb.com.br/

====================
Flask-IdentityClient
====================

API de conexão com PassaporteWeb_ para aplicações Flask_.


Configurações
-------------

Os *settings* do Flask precisam conter as seguntes chaves:

- ``SERVICE_ACCOUNT``: nome completo do *model* de conta de serviço,
  equivalente ao *model* ``ServiceAccount`` no PassaporteWeb. Ex.:
  ``authentication.models.ServiceAccount``.

- ``PASSAPORTE_WEB``: dicionário contendo as chaves:

  - ``HOST``: prefixo do PassaporteWeb, incluindo protocolo. Ex.:
    ``https://app.passaporteweb.com.br``.

  - ``FETCH_USER_DATA_PATH``: *path* da URL de captura de dados do
    usuário. Ex.: ``/sso/fetchuserdata/``.

  - ``REQUEST_TOKEN_PATH``: *path* da URL para inicialização da
    requisição de *token*. Ex.: ``/sso/initiate/``.

  - ``ACCESS_TOKEN_PATH``: *path* da URL de troca de *token*. Ex.:
    ``/sso/token/``.

  - ``AUTHORIZATION_PATH``: *PATY* da URL de autorização. Ex.:
    ``/sso/authorize/``.

  - ``SCOPE``: escopo OAuth, padrão: ``auth:api``.

  - ``CONSUMER_TOKEN`` e ``CONSUMER_SECRET``: credenciais de autenticação
    do consumidor.

  - ``ECOMMERCE_URL`` (opcional): URL da aplicação no Ecommerce.


*Blueprint*
-----------

O *blueprint* do Flask-IdentityClient pode ser encontrado em
``flask_identity_client.application`` e é chamado ``blueprint``.

Você pode registrá-lo::

    from flask_identity_client.application import blueprint
    app.register_blueprint(blueprint, url_prefix='/sso')


Autenticação de usuário
-----------------------

Para registrar um outro *blueprint* para requerer usuário, você deve
usar::

    from flask_identity_client.startup_funcs import user_required

    # blueprint aqui é o blueprint alvo, não flask_identity_client!
    blueprint.before_request(user_required)


*Callback* de atualização de contas de serviço
----------------------------------------------

A classe de conta de serviço (``ServiceAccount``) deve possuir o método
de classe ``update()``, que recebe uma lista de dicionários
representando as contas de cobrança identificados para o usuário no
PassaporteWeb, e deve retornar uma lista dos UUIDs válidos na aplicação
local.


Obtendo recursos de um serviço atravessador
-------------------------------------------

É possível obter recursos de um serviço atravessador através do *factory*
de funções *startup* ``flask_identity_client.startup_funcs.resources_from_middle``.

O *factory* recebe como parâmetro a chave do dicionário de configurações
no *config* da aplicação. O dicionário deve ter as seguintes informações:

- ``TOKEN``: *token* de acesso ao serviço atravessador.

- ``SECRET``: chave secreta associada ao *token*.

- ``HOST``: serviço atravessador, incluindo o protocolo (``http://`` ou
  ``https://``).

- ``PATH``: caminha na API do serviço atravessador que retorna os recursos.


O resultado é armazenado na sessão, referenciado pela chave ``resources``.
Caso ocorra algum erro, a chave existirá, mas o valor será ``None``.

Observação: é preciso estar logado no PassaporteWeb, pois o serviço
atravessador receberá os mesmos dados do *login*.
