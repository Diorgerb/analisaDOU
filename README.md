
```markdown
# DOU Extractor

## Descrição

O DOU Extractor é um utilitário Python para extrair dados do Diário Oficial da União (DOU) utilizando o serviço do Inlabs.

## Como Usar

### Pré-requisitos

Certifique-se de ter as seguintes bibliotecas instaladas:

- [Pandas](https://pandas.pydata.org/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [XMLtodict](https://pypi.org/project/xmltodict/)
- [tqdm](https://pypi.org/project/tqdm/)

Você também precisará ter uma conta válida no [Inlabs](https://inlabs.in.gov.br/acessar.php), já que o código depende de credenciais válidas para acessar o DOU.

### Instalação

1. Clone este repositório:

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. Edite o arquivo `config.json` com as informações necessárias, como URLs e diretórios de download, de acordo com o ambiente em que você está executando o código.

3. Execute o código Python:

   ```bash
   python main.py
   ```

4. Siga as instruções para fornecer seu e-mail e senha do Inlabs quando solicitado.

### Resultados

Os resultados da extração do DOU serão salvos em um arquivo Excel chamado `atos_do_dou.xlsx`.

## Contribuindo

Sinta-se à vontade para contribuir para este projeto. Se você deseja fazer melhorias ou correções, siga estas etapas:

1. Faça um fork do repositório.
2. Crie uma nova branch com sua melhoria: `git checkout -b sua-melhoria`
3. Faça commit das alterações: `git commit -m 'Adiciona sua melhoria'`
4. Envie as alterações: `git push origin sua-melhoria`
5. Crie uma solicitação de pull (PR).
