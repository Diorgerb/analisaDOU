import json
import os
import re
import zipfile
from datetime import date, datetime, timedelta
import pandas as pd
import requests
import urllib3
import xmltodict
from tqdm import tqdm

from act import Act

urllib3.disable_warnings()


class DOUExtractor:
    def __init__(self, user: str, password: str) -> None:
        self.user: str = user
        self.password: str = password
        self.config: dict = self._open_config()
        self.session: requests.Session = requests.Session()

    def extract(
        self,
        date_init: str,
        date_end: str,
        sections: None | list[str] = None,
        date_format: str = "%Y-%m-%d",
    ) -> list[dict]:
        """Extrai os dados do Inlabs baseado no intervalo de data especificado.
        Lembrando que os dados só ficam disponíveis por 120 a partir da data de captura."""
        self._make_temp_folder()
        dates = get_dates_from_interval(date_init, date_end, date_format)
        self.login()
        for date_ in dates:
            if not sections:
                sections = self.config['SECOES']
            self.download(date_, sections, date_format)
        self.unzip_files()
        acts_list = self.get_acts_from_unziped_folder()
        self._clean_temp_folder()
        return acts_list

    def _open_config(self):
        with open("config.json", encoding="utf8") as file:
            return json.load(file)

    def download(
        self, date_: str, sections: list[str], date_format: str = "%Y-%m-%d"
    ) -> None:
        "Baixa os arquivos zipados do Inlabs da data e seções especificadas e os salva na pasta download configurada."
        if self.session.cookies.get("inlabs_session_cookie"):
            cookie = self.session.cookies.get("inlabs_session_cookie")
        else:
            raise ConnectionRefusedError("Falha ao obter cookie. Verifique o usuário e a senha passados.")

        # Montagem da URL:
        dt_ = datetime.strptime(date_, date_format)
        data_completa = f"{dt_.year}-{dt_.month:02}-{dt_.day:02}"

        if isinstance(sections, str):
            raise ValueError("sections não é uma lista.")
        for dou_secao in sections:
            print("Aguarde Download...")
            url_arquivo = (
                self.config["URL_DOWNLOAD"]
                + data_completa
                + "&dl="
                + data_completa
                + "-"
                + dou_secao
                + ".zip"
            )
            print("Url: " + url_arquivo)
            cabecalho_arquivo = {
                "Cookie": "inlabs_session_cookie=" + cookie,
                "origem": "736372697074",
            }
            response_arquivo = self.session.request(
                "GET", url_arquivo, headers=cabecalho_arquivo, verify=False
            )
            if response_arquivo.status_code == 200:
                with open(
                    self.config["DOWNLOAD_FOLDER"]
                    + "/"
                    + data_completa
                    + "-"
                    + dou_secao
                    + ".zip",
                    "wb",
                ) as f:
                    f.write(response_arquivo.content)
                    print(f"Arquivo {data_completa + '-' + dou_secao + '.zip'} salvo.")
                del response_arquivo
                del f
            elif response_arquivo.status_code == 404:
                print(
                    f"Arquivo não encontrado: {data_completa + '-' + dou_secao + '.zip'}"
                )

    def login(self):
        "Loga no site do Inlabs para obter o cookie necessário."
        payload = {"email": self.user, "password": self.password}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            self.session.request(
                "POST",
                self.config["URL_LOGIN"],
                data=payload,
                headers=headers,
                verify=False,
            )
            print("Logado.")
        except requests.exceptions.ConnectionError:
            self.login()

    def unzip_files(self):
        "Unzip os arquivos baixados na pasta temp/download."
        files_names = os.listdir(self.config["DOWNLOAD_FOLDER"])
        for file_name in files_names:
            # opening the zip file in READ mode
            try:
                with zipfile.ZipFile(
                    self.config["DOWNLOAD_FOLDER"] + "/" + file_name, "r"
                ) as zipf:
                    # extracting all the files
                    print(f"Extracting all the files now from zipfile {file_name}...")
                    zipf.extractall(self.config["UNZIP_FOLDER"])
            except zipfile.BadZipFile:
                pass

    def get_acts_from_unziped_folder(self) -> list[dict]:
        "Monta a lista de atos baseados nos arquivos xml da pasta unziped configurada."
        print("Montando atos...")
        files = os.listdir(self.config["UNZIP_FOLDER"])
        xml_files = [file for file in files if ".xml" in file]
        final_list = []
        # open XML and prep Act object
        for xml_file in tqdm(xml_files):
            unzip_folder = self.config["UNZIP_FOLDER"]
            file_path = f"{unzip_folder}/{xml_file}"
            # Open
            with open(file_path, "r", encoding="utf-8-sig") as file:
                xml_object = file.read()

            dic = xmltodict.parse(xml_object)

            # Transform
            com = re.compile(r"[0-9]")
            article = dic["xml"]["article"]
            texto = article["body"]["Texto"]


            ato_dict = {
                "act_id": f"{article['@id']}-{article['@idOficio']}-{article['@idMateria']}",
                "tipo": article["@artType"],
                "titulo": article["body"]["Identifica"],
                "orgao": article["@artCategory"],
                "ementa": article["body"]["Ementa"],
                "texto_completo": texto,
                "secao": int(com.findall(article["@pubName"])[0]),
                "edicao": article["@editionNumber"],
                "tipo_edicao": "Extra" if "E" in article["@pubName"] else "Ordinária",
                "pagina": article["@numberPage"],
                "data_publicacao": datetime.strptime(article["@pubDate"], "%d/%m/%Y"),
                "url": None,
                "url_versao_certificada": article["@pdfPage"],
                "data_captura": datetime.today(),
                "data_publicacao_particao": None,
            }

            # instancia um objeto Act para pegar as colunas que faltam
            act = Act(**ato_dict)

            # append o dicionário do objeto (como é uma dataclass, o __dict__ retorna os valores
            # dos atributos calculados no __post_init__
            final_list.append(act.__dict__)
        return final_list

    def _make_temp_folder(self):
        "Cria a pasta temporária caso não exista."
        if not os.path.exists(self.config["DOWNLOAD_FOLDER"]):
            os.makedirs(self.config["DOWNLOAD_FOLDER"])
        if not os.path.exists(self.config["UNZIP_FOLDER"]):
            os.makedirs(self.config["UNZIP_FOLDER"])

    def _clean_temp_folder(self):
        "Remove arquivos da pasta temp."
        download_fs = os.listdir(self.config["DOWNLOAD_FOLDER"])
        unzip_fs = os.listdir(self.config["UNZIP_FOLDER"])

        for file in download_fs:
            os.unlink(self.config["DOWNLOAD_FOLDER"] + "/" + file)

        for file in unzip_fs:
            os.unlink(self.config["UNZIP_FOLDER"] + "/" + file)

############################################################################
# HELPERS
############################################################################


def get_dates_from_interval(
    start_date: str | datetime | date,
    end_date: str | datetime | date,
    date_format: str = "%d-%m-%Y",
) -> list:
    """Retorna uma lista de dates entre start_date e end_date."""

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, date_format).date()
        end_date = datetime.strptime(end_date, date_format).date()
    sdate = min(start_date, end_date)
    edate = max(start_date, end_date)
    dates_list = [sdate + timedelta(days=x) for x in range((edate - sdate).days + 1)]
    dates_list = [d.strftime(date_format) for d in dates_list]
    return dates_list
