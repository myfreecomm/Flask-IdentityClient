.. _Flask: http://flask.pocoo.org/docs/
.. _PassaporteWeb: https://app.passaporteweb.com.br/

====================
Flask-IdentityClient
====================

API de conexão com PassaporteWeb_ para aplicações Flask_.


Configurações
-------------

Os *settings* do Flask precisam conter as seguntes chaves:

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


Sinais
------

Flask-IdentityClient oferece o sinal
``flask_identity_client.signal.update_service_account``, que precisa ser
conectado a um *handler* com assinatura ``(sender, user_data)`` para
efetuar as atualizações do *model* equivalente a ``ServiceAccount`` do
PassaporteWeb.

A lista de contas do usuário enviada pelo PassaporteWeb encontra-se na
chave ``accounts`` de ``user_data`` e pode ser modificada. Um lista com
os UUIDs das contas que permanecerem na chave após processamento dos
*handlers* será adicionada à chave ``accounts`` do dicionário
``user_data`` na sessão, que contém outras chaves importantes, como
``uuid``, ``email``, ``first_name``, ``last_name`` e ``full_name`` do
usuário (*identity*) autenticado.


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

O objeto de recursos na chave ``resources`` da sessão possui os seguintes
atributos:

- ``data``: dados recebidos.

- ``etag``: ETag da resposta, usado nas requisições seguintes.

- ``expires``: data de expiração da resposta da requisição em formato
  Posix, usado para evitar requisições múltiplas.

Observação: é preciso estar logado no PassaporteWeb, pois o serviço
atravessador receberá os mesmos dados do *login*. Caso os dados de
*login* estejam desatualizados ou o usuário não esteja logado, o valor
de ``resources`` será ``werkzeug.exceptions.Unauthorized`` (a exceção
**não** será levantada), delegando para a aplicação a responsabilidade
sobre como lidar com isso.

A sugestão é redirecionar o cliente para o processo de *login*::

    if session['resources'] is Unauthorized:
        session.clear()
        return redirect(url_for('identity_client.login', next=request.url))


CHANGELOG
=========

Até versão 0.4.2, a atualização era realizada passando para a biblioteca
o caminho para encontrar o *model* ``ServiceAccount``, na chave
``SERVICE_ACCOUNT`` dos *settings*.

A partir da versão 0.5, Flask-IdentityClient não precisa mais conhecer
detalhes de implementação da aplicação. Para atualizar a base local,
basta conectar um *handler* ao sinal
``flask_identity_client.signal.update_service_account``, conforme
descrito acima.

Porém, **é necessário** atualizar o comportamento das aplicações
antigas, que não serão mais compatíveis com as novas versões de
Flask-IdentityClient.
