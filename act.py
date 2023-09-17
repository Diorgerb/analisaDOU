from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup


EXCERTO_WORDS = [
    "resolve", "outorga", "onde se l", "objeto", "espécie"
]


@dataclass
class Act:
    act_id: str
    tipo: str
    titulo: str
    orgao: str
    ementa: str
    texto_completo: str
    secao: int
    edicao: str
    tipo_edicao: str
    pagina: str
    data_publicacao: str
    url: str
    url_versao_certificada: str
    data_captura: datetime
    data_publicacao_particao: datetime
    texto_principal: None | str = None
    excerto: None | str = None
    assinatura: None | str = None
    cargo: None | str = None

    def __post_init__(self):
        if self.texto_completo:
            soup = BeautifulSoup(self.texto_completo, "html.parser")
            self.texto_principal = self._get_texto_principal(soup)
            self.excerto = self._get_texto_excerto(self.texto_principal)
            self.assinatura = self._get_assinaturas(soup)
            self.cargo = self._get_cargos(soup)

    def _get_texto_principal(self, soup: BeautifulSoup):
        try:
            text_list = [text.get_text() for text in soup.find_all(class_=None)]
            return "\n".join(text_list)
        except IndexError:
            return None

    def _get_texto_excerto(self, texto: str):
        if texto:
            text = texto.lower()
            for word in EXCERTO_WORDS:
                if word in text:
                    return text[text.index(word):]

    def _get_assinaturas(self, soup: BeautifulSoup):
        if not soup:
            return
        res = soup.find_all(class_="assina")
        if len(res) == 0:
            return None
        return "|".join([sign.get_text() for sign in res])

    def _get_cargos(self, soup: BeautifulSoup):
        if not soup:
            return
        res = soup.find_all(class_="cargo")
        if len(res) == 0:
            return None
        return "|".join([sign.get_text() for sign in res])
