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

# Directory and file names
output_dir = "textos_uol"
output_file = os.path.join(output_dir, "dados_redacoes.csv")
processed_links_file = os.path.join(output_dir, "processados.txt")
title_file = os.path.join(output_dir, "titulos.csv")
id_file = os.path.join(output_dir, "ultimo_id.txt")

# Make sure the directory exists, and if not, create it
os.makedirs(output_dir, exist_ok=True)

# Loads the last saved ID (incremental key) or sets it to 0
if os.path.exists(id_file):
    with open(id_file, "r") as f:
        last_id = int(f.read().strip())
else:
    last_id = 0

# Function to generate the next incremental ID
def generate_id():
    global last_id
    last_id += 1
    return f"{last_id:06d}"

# Loads already processed links to avoid duplication
if os.path.exists(processed_links_file):
    with open(processed_links_file, "r", encoding="utf-8") as f:
        processed_links = set(line.strip() for line in f)
else:
    processed_links = set()

# Checks if the main file already exists to set the opening mode and header
file_mode = "a" if os.path.exists(output_file) else "w"

# Opens the main CSV file for writing and sets the header if necessary
with open(output_file, mode=file_mode, newline="", encoding="utf-8") as main_file:

    writer_main = csv.writer(main_file)
    
    # Write the header to the main CSV
    if file_mode == "w":
        writer_main.writerow(["ID", "Título", "Subtítulo", "Texto da Redação", "Competências", "Notas das Competências", "Comentários das Competências", "Nota Final"])

    # Open the header file in "w" mode to ensure clean and correct header
    with open(title_file, mode="w", newline="", encoding="utf-8") as title_file_obj:
        writer_title = csv.writer(title_file_obj)
        # Escreve o cabeçalho para o arquivo de títulos
        writer_title.writerow(["ID", "Título"])

        # Process each URL in the list
        for url in urls:
            if url in processed_links:
                print(f"URL já processada, ignorando: {url}")
                continue

            try:
                # Generates a new ID for the current row
                record_id = generate_id()

                # Performs the GET request to obtain the page content
                response = requests.get(url)
                response.raise_for_status()  # Check if there was an error in the request

                # Creates a BeautifulSoup object to parse the page's HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the title of the essay
                title_tag = soup.find('i', class_='custom-title')
                title = title_tag.get_text(strip=True) if title_tag else "Título não encontrado"

                # Extracts the subtitle of the essay (h2 inside container-composition inside wording-correction)
                section_wording_correction = soup.find('section', class_='wording-correction')
                container_composition = section_wording_correction.find('div', class_='container-composition') if section_wording_correction else None
                subtitle_tag = container_composition.find('h2') if container_composition else None
                subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else "Subtítulo não encontrado"

                # Writes the main title to the titles file, with the generated ID
                writer_title.writerow([record_id, title])

                # Extracts the text from the composition within the 'text-composition' tag
                essay_section = soup.find('div', class_='text-composition')

                if essay_section:
                    paragraphs = []
                    for p in essay_section.find_all('p'):
                        # For each <p>, add space before and after the <span> and <strong> tags
                        for tag in p.find_all(['strong', 'span']):
                            # Inserts space around the content of each <span> and <strong>
                            tag.insert_before(' ')
                            tag.insert_after(' ')
                        # Extracts the processed text, ensuring the inserted spaces
                        clean_text = p.get_text(strip=True)
                        paragraphs.append(clean_text)
                    essay_text = " ".join(paragraphs)
                else:
                    essay_text = "Redação não encontrada"



                # Extracts skills and grades, ignoring the "Final Grade"
                competence_scores_section = soup.find('section', class_='results-table')
                competence_scores_list = competence_scores_section.find_all('div', class_='rt-line-option') if competence_scores_section else []

                # Lists to store skills, grades, and comments (excluding the Final Grade)
                competences = []
                competence_scores = []
                final_score = "Nota final não encontrada"

                for score in competence_scores_list:
                    topic = score.find('span', class_='topic').get_text(strip=True)
                    points = score.find('span', class_='points').get_text(strip=True)
                    
                    if "Nota final" in topic:
                        final_score = points  # Stores the final grade separately
                    else:
                        competences.append(topic)
                        competence_scores.append(points)

                # Extracts feedback from skills
                competence_comments_section = soup.find('h3', string="Competências")
                competence_comments_list = competence_comments_section.find_next('ul').find_all('li') if competence_comments_section else []
                competence_comments = [comment.get_text(strip=True) for comment in competence_comments_list]
                concatenated_comments = "; ".join(competence_comments)

                # Concatenates skills and grades (without the Final Grade) using ";" as a separator
                concatenated_competences = "; ".join(competences)
                concatenated_scores = "; ".join(competence_scores)

                # Writes a line to the main CSV for each URL processed
                writer_main.writerow([record_id, title, subtitle, essay_text, concatenated_competences, concatenated_scores, concatenated_comments, final_score])

                # Mark the URL as processed and save it to the processed links file
                with open(processed_links_file, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                
                print(f"Processado com sucesso: {url}")

            except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar a página {url}: {e}")

# Salva o último ID usado
with open(id_file, "w") as f:
    f.write(str(last_id))

print(f"Arquivos CSV salvos em: {output_file} e {title_file}")