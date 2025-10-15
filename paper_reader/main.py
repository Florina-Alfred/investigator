import argparse
import time
from ollama import chat
import re
from typing import List
import arxiv
from docling.document_converter import DocumentConverter
from dataclasses import dataclass
import sys
import os
import shutil
import logging


DOWNLOADS_FOLDER = "downloads"
PAPERS_TO_READ = []
TOTAL_PAPERS_TO_QUERY = 10
MODEL = ""


def _set_script_info_logging():
    # Set root logger to ERROR to suppress dependency logs
    # logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    # logging.getLogger().setLevel(logging.ERROR)
    # Suppress noisy libraries and submodules
    logging.getLogger("docling").setLevel(logging.CRITICAL)
    logging.getLogger("docling.pipeline").setLevel(logging.CRITICAL)
    logging.getLogger("pdfminer").setLevel(logging.CRITICAL)
    logging.getLogger("transformers").setLevel(logging.CRITICAL)
    logging.getLogger("arxiv").setLevel(logging.CRITICAL)
    # Create a script/module logger and set to INFO
    script_logger = logging.getLogger(__name__)
    script_logger.setLevel(logging.INFO)
    return script_logger


# logger = _set_script_info_logging()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_downloads_folder_name(query: str) -> str:
    """
    Generates a folder name with the prefix 'downloads' followed by the query string.
    Returns the folder name as a string.
    """
    return os.path.join(DOWNLOADS_FOLDER, replace_symbols_with_underscore(query))


def create_downloads_folder(query: str):
    """
    Creates a new folder named downloads_<query> in the same directory as main.py.
    Deletes the folder first if it already exists.
    Sets the global variable DOWNLOADS_FOLDER to the folder name.
    """
    folder_name = get_downloads_folder_name(query)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    global DOWNLOADS_FOLDER
    DOWNLOADS_FOLDER = folder_path
    logging.info(f"Created new downloads folder: {DOWNLOADS_FOLDER}")


def convert_and_export(source_url: str, output_path: str) -> None:
    """
    Converts a document from the given source URL using DocumentConverter
    and exports it as markdown to the specified output path.
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(source_url)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.document.export_to_markdown())
        logging.info(f"Document exported to {output_path}")
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        sys.exit(1)


@dataclass
class Paper:
    title: str
    summary: str
    link: str


def get_exact_paper(id: str) -> Paper | None:
    global DOWNLOADS_FOLDER
    # Fetch a specific paper by arXiv id
    client = arxiv.Client()
    search = arxiv.Search(id_list=[id])
    try:
        result = next(client.results(search))
        result.download_pdf(dirpath=f"{DOWNLOADS_FOLDER}")
        return Paper(title=result.title, summary=result.summary, link=result.pdf_url)
    except Exception as e:
        logging.error(f"Could not find paper with id {id}: {e}")
        return None


def clean_multiword_query(query: str) -> str:
    all = "all"
    title = "title"  # deprecated
    title = "ti"
    # abstract = "abstract" #  deprecated
    abstract = "abs"
    clean_query = ""

    # in title only
    if len(query.split(" ")) > 1:
        for word in query.split(" "):
            clean_query += f"{title}:{word} AND "
        return clean_query.rstrip(" AND ")
    else:
        return query

    # # in abstract only
    # if len(query.split(" ")) > 1:
    #     for word in query.split(" "):
    #         clean_query += f"{abstract}:{word} AND "
    #     return clean_query.rstrip(" AND ")
    # else:
    #     return query

    # # in title or abstract
    # if len(query.split(" ")) > 1:
    #     for word in query.split(" "):
    #         clean_query += f"{title}:{word} AND "
    #     clean_query = clean_query.rstrip(" AND ")
    #     clean_query += " OR "
    #     for word in query.split(" "):
    #         clean_query += f"{abstract}:{word} OR "
    #     return clean_query.rstrip(" OR ")
    # else:
    #     return query

    # # in all content
    # if len(query.split(" ")) > 1:
    #     for word in query.split(" "):
    #         clean_query += f"{all}:{word} AND "
    #     return clean_query.rstrip(" AND ")
    # else:
    #     return query


def get_relevant_papers(query: str, max_results: int) -> List[Paper]:
    """
    Searches arXiv for papers matching the query and returns a list of Paper objects.
    """
    global DOWNLOADS_FOLDER
    client = arxiv.Client()
    query = clean_multiword_query(query)
    if len(query.split(" ")) > 1:
        logging.info(f"Modified query: {query}")
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    papers = []
    logging.info("Downloading paper:\n")
    for id, r in enumerate(client.results(search)):
        papers.append(Paper(title=r.title, summary=r.summary, link=r.pdf_url))
        r.download_pdf(dirpath=f"{DOWNLOADS_FOLDER}")
        logging.info(f"\t{id + 1}.{r.title}\n")
    return papers


def replace_symbols_with_underscore(name: str):
    """
    Replace all symbols in the name with underscores and return the result.
    """
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


def download_paper(single: str):
    global PAPERS_TO_READ, DOWNLOADS_FOLDER

    create_downloads_folder("single")
    paper = get_exact_paper(single)
    if paper is not None:
        logging.info(f"Converting paper: {paper.title}")
        output_path = os.path.join(
            DOWNLOADS_FOLDER, replace_symbols_with_underscore(paper.title) + ".md"
        )
        PAPERS_TO_READ.append(output_path)
        convert_and_export(paper.link, output_path)


def download_papers(query: str):
    global PAPERS_TO_READ, DOWNLOADS_FOLDER, TOTAL_PAPERS_TO_QUERY

    create_downloads_folder(query)
    papers = get_relevant_papers(query, TOTAL_PAPERS_TO_QUERY)
    for idx, paper in enumerate(papers):
        logging.info(f"{idx + 1}.Converting paper: {paper.title}")
        output_path = os.path.join(
            DOWNLOADS_FOLDER, replace_symbols_with_underscore(paper.title) + ".md"
        )
        PAPERS_TO_READ.append(output_path)
        convert_and_export(paper.link, output_path)


def read_file(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


def write_file(content: str, name: str):
    global MODEL
    # name = name + f"_summary_{replace_symbols_with_underscore(MODEL)}"
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)


def ask_model(question: str, model: str, system_prompt: str | None = None) -> str:
    """
    Sends a message to the specified Ollama model and returns the response content.
    """
    messages = []
    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )
    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )
    if model[:7] == "hf.co/unsloth/gpt-oss-20b-GGUF:latest":
        levels = ["low", "medium", "high"]
        logging.info(f"........using {levels[2]} for thinking")
        response = chat(model=model, messages=messages, think=levels[2])
    else:
        response = chat(model=model, messages=messages, think=False)

    content = getattr(response.message, "content", None)
    if content is None:
        logging.error("Model did not return any content.")
        return ""
    return content


def parse_args():
    global TOTAL_PAPERS_TO_QUERY
    parser = argparse.ArgumentParser(
        description="Convert a document from a URL and export as markdown."
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="hf.co/unsloth/gpt-oss-20b-GGUF:latest",
        # default="hf.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:latest",
        help="The model that is used to generate summaries and responses.",
    )
    parser.add_argument(
        "-d",
        "--direct",
        default=None,
        type=str,
        help="Perform summary of pre-downloaded PDF file",
    )
    parser.add_argument(
        "-t",
        "--total",
        default=TOTAL_PAPERS_TO_QUERY,
        type=int,
        help="Total number of papers to query from the Arxiv site.",
    )
    parser.add_argument(
        "-s",
        "--single",
        default=None,
        help="The ID of the paper to get and save.",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        # default="kubernetes",
        default="kubernetes robotics",
        help="The query to perform the search on (e.g. kubernetes)",
    )
    return parser.parse_args()


def main():
    global MODEL, PAPERS_TO_READ, DOWNLOADS_FOLDER
    args = parse_args()
    query = args.query
    MODEL = args.model
    single = args.single

    if args.direct:
        file_name = ""
        if os.path.isdir(args.direct):
            for entry in os.listdir(args.direct):
                file_path = os.path.join(args.direct, entry)
                if os.path.isfile(file_path):
                    download_location = os.path.join(
                        DOWNLOADS_FOLDER, "single", os.path.splitext(entry)[0] + ".md"
                    )
                    PAPERS_TO_READ.append(download_location)
                    file_name = file_path
                    convert_and_export(file_name, PAPERS_TO_READ[-1])
        else:
            download_location = os.path.join(
                DOWNLOADS_FOLDER, "single", os.path.splitext(args.direct)[0] + ".md"
            )
            PAPERS_TO_READ.append(download_location)
            file_name = args.direct
            convert_and_export(file_name, PAPERS_TO_READ[-1])
    else:
        if single is not None:
            logging.info(f"Getting : {single}, model: {MODEL}")
            download_paper(single)
        else:
            logging.info(f"Using query: {query}, model: {MODEL}")
            download_papers(query)

    for idx, paper in enumerate(PAPERS_TO_READ):
        start_time = time.perf_counter()
        logging.info(f"{idx + 1}.Reading:------- {paper}")
        paper_content = read_file(paper)
        prompt = read_file("./prompts/summarize_paper.md")
        question = "Please summarize the following paper:\n\n\n" + paper_content
        summary = ask_model(question, model=MODEL, system_prompt=prompt)
        logging.info(f"\tSaving:------- {paper}")
        logging.info(
            f"\tTime taken for answering: {time.perf_counter() - start_time:0.2f} seconds"
        )
        paper = (
            paper[:-3]
            + f"_summary_{replace_symbols_with_underscore(MODEL)}"
            + paper[-3:]
        )
        write_file(summary, paper)


if __name__ == "__main__":
    main()
