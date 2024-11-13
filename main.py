import os
import re
import csv
import time
import requests
from bs4 import BeautifulSoup

urls = [
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/qualificacoes-para-o-mercado-de-trabalho.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/a-apropriacao-cultural-e-o-conhecimento-historico.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/no-mes-de-fevereiro-muitos-paises.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-cultural-e-atualidades.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/representacao-indigena-no-meio-social.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/a-afronta-carnavalesca.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/carnaval-uma-festa-de-cultura.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/carnaval-ou-cultura.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/monopolio-cultural.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-cultural-tao-necessaria-quanto-natural.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-cultural-significa-uma-pessoa.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/dar-voz-para-quem-nao-a-possui.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/carnaval-sinonimo-de-composicao-cultural.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/multiculturalismo-carnavalesco.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-ou-intercambio.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/a-apropriacao-cultural-continua.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/muito-alem-da-fantasia.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/as-fantasias-no-carnaval.htm",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-cultural-e-so-no-carnaval.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/entender-o-outro.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/apropriacao-cultural-e-o-racismo-velado.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/uniao-entre-o-orgao-publico-e-a-opiniao-publica.html",
    "https://educacao.uol.com.br/bancoderedacoes/redacoes/a-democracia-estende-se-ao-stf.html"
]

# Diretório e nomes dos arquivos
output_dir = "textos_uol"
output_file = os.path.join(output_dir, "dados_redacoes.csv")
processed_links_file = os.path.join(output_dir, "processados.txt")
title_file = os.path.join(output_dir, "titulos.csv")
id_file = os.path.join(output_dir, "ultimo_id.txt")

# Certifica-se de que o diretório existe, e se não, cria-o
os.makedirs(output_dir, exist_ok=True)

# Carrega o último ID salvo (chave incremental) ou define como 0
if os.path.exists(id_file):
    with open(id_file, "r") as f:
        last_id = int(f.read().strip())
else:
    last_id = 0

# Função para gerar o próximo ID incremental
def generate_id():
    global last_id
    last_id += 1
    return f"{last_id:06d}"

# Carrega os links já processados para evitar duplicação
if os.path.exists(processed_links_file):
    with open(processed_links_file, "r", encoding="utf-8") as f:
        processed_links = set(line.strip() for line in f)
else:
    processed_links = set()

# Verifica se o arquivo principal já existe para definir o modo de abertura e o cabeçalho
file_mode = "a" if os.path.exists(output_file) else "w"

# Abre o arquivo CSV principal para escrita e define o cabeçalho se necessário
with open(output_file, mode=file_mode, newline="", encoding="utf-8") as main_file:

    writer_main = csv.writer(main_file)
    
    # Escreve o cabeçalho no CSV principal
    if file_mode == "w":
        writer_main.writerow(["ID", "Título", "Subtítulo", "Texto da Redação", "Competências", "Notas das Competências", "Comentários das Competências", "Nota Final"])

    # Abre o arquivo de títulos em modo "w" para garantir o cabeçalho limpo e correto
    with open(title_file, mode="w", newline="", encoding="utf-8") as title_file_obj:
        writer_title = csv.writer(title_file_obj)
        # Escreve o cabeçalho para o arquivo de títulos
        writer_title.writerow(["ID", "Título"])

        # Processa cada URL na lista
        for url in urls:
            if url in processed_links:
                print(f"URL já processada, ignorando: {url}")
                continue

            try:
                # Gera um novo ID para a linha atual
                record_id = generate_id()

                # Realiza a requisição GET para obter o conteúdo da página
                response = requests.get(url)
                response.raise_for_status()  # Verifica se houve algum erro na requisição

                # Cria um objeto BeautifulSoup para analisar o HTML da página
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extrai o título da redação
                title_tag = soup.find('i', class_='custom-title')
                title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"

                # Extrai o subtítulo da redação (h2 dentro de container-composition dentro de wording-correction)
                section_wording_correction = soup.find('section', class_='wording-correction')
                container_composition = section_wording_correction.find('div', class_='container-composition') if section_wording_correction else None
                subtitle_tag = container_composition.find('h2') if container_composition else None
                subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else "Subtítulo não encontrado"

                # Grava o título principal no arquivo de títulos, com o ID gerado
                writer_title.writerow([record_id, title])

                # Extrai o texto da redação dentro da tag 'text-composition'
                essay_section = soup.find('div', class_='text-composition')

                if essay_section:
                    paragraphs = []
                    for p in essay_section.find_all('p'):
                        # Para cada <p>, adiciona espaço antes e depois das tags <span> e <strong>
                        for tag in p.find_all(['strong', 'span']):
                            # Insere espaço ao redor do conteúdo de cada <span> e <strong>
                            tag.insert_before(' ')
                            tag.insert_after(' ')
                        # Extrai o texto processado, garantindo os espaços inseridos
                        clean_text = p.get_text(strip=True)
                        paragraphs.append(clean_text)
                    essay_text = " ".join(paragraphs)
                else:
                    essay_text = "Redação não encontrada"



                # Extrai as competências e notas, ignorando a "Nota Final"
                competence_scores_section = soup.find('section', class_='results-table')
                competence_scores_list = competence_scores_section.find_all('div', class_='rt-line-option') if competence_scores_section else []

                # Listas para armazenar competências, notas, e comentários (excluindo a Nota Final)
                competences = []
                competence_scores = []
                final_score = "Nota final não encontrada"

                for score in competence_scores_list:
                    topic = score.find('span', class_='topic').get_text(strip=True)
                    points = score.find('span', class_='points').get_text(strip=True)
                    
                    if "Nota final" in topic:
                        final_score = points  # Armazena a nota final separadamente
                    else:
                        competences.append(topic)
                        competence_scores.append(points)

                # Extrai os comentários das competências
                competence_comments_section = soup.find('h3', string="Competências")
                competence_comments_list = competence_comments_section.find_next('ul').find_all('li') if competence_comments_section else []
                competence_comments = [comment.get_text(strip=True) for comment in competence_comments_list]
                concatenated_comments = "; ".join(competence_comments)

                # Concatena as competências e as notas (sem a Nota Final) usando ";" como separador
                concatenated_competences = "; ".join(competences)
                concatenated_scores = "; ".join(competence_scores)

                # Escreve uma linha no CSV principal para cada URL processada
                writer_main.writerow([record_id, title, subtitle, essay_text, concatenated_competences, concatenated_scores, concatenated_comments, final_score])

                # Marca a URL como processada e salva no arquivo de links processados
                with open(processed_links_file, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                
                print(f"Processado com sucesso: {url}")

            except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar a página {url}: {e}")

# Salva o último ID usado
with open(id_file, "w") as f:
    f.write(str(last_id))

print(f"Arquivos CSV salvos em: {output_file} e {title_file}")