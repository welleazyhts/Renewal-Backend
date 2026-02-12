import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from docx import Document
from django.utils import timezone
from django.conf import settings
import logging

from .models import KnowledgeDocument, KnowledgeWebsite

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class KnowledgeService:
    @staticmethod
    def extract_text_from_document(file_path):
        if not file_path:
            raise ValueError("file_path is required for OCR")

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".docx":
                doc = Document(file_path)
                text = "\n".join(p.text for p in doc.paragraphs)
                return text.strip(), 100.0

            if ext in [".png", ".jpg", ".jpeg", ".tiff"]:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                return text.strip(), 90.0

            if ext == ".pdf":
                poppler_path = getattr(settings, "POPPLER_PATH", None)

                if not poppler_path:
                    raise RuntimeError(
                        "POPPLER_PATH is not configured in Django settings."
                    )

                pdfinfo_path = os.path.join(poppler_path, "pdfinfo.exe")
                if not os.path.exists(pdfinfo_path):
                    raise RuntimeError(
                        f"Poppler not found. pdfinfo.exe not found at: {pdfinfo_path}"
                    )

                try:
                    pages = convert_from_path(
                        file_path,
                        dpi=300,
                        poppler_path=poppler_path,
                    )
                except Exception as exc:
                    raise RuntimeError(
                        "Unable to read PDF pages. Poppler may be misconfigured."
                    ) from exc

                full_text = ""
                for page in pages:
                    full_text += pytesseract.image_to_string(page)

                return full_text.strip(), 85.0

            raise ValueError(f"Unsupported document type: {ext}")

        except Exception:
            logger.exception("Text extraction failed for file: %s", file_path)
            raise

    @staticmethod
    def run_ocr_after_approval(document):
        if not document.document_file:
            logger.warning("Document has no file: %s", document.id)
            return

        if document.ocr_status == "completed":
            return

        try:
            document.ocr_status = "processing"
            document.save(update_fields=["ocr_status"])

            text, accuracy = KnowledgeService.extract_text_from_document(
                document.document_file.path
            )

            document.extracted_text = text
            document.ocr_accuracy = accuracy
            document.ocr_status = "completed"
            document.save(
                update_fields=[
                    "extracted_text",
                    "ocr_accuracy",
                    "ocr_status",
                ]
            )

        except Exception as exc:
            document.ocr_status = "failed"
            document.ocr_failure_reason = str(exc)
            document.save(
                update_fields=[
                    "ocr_status",
                    "ocr_failure_reason",
                ]
            )
            raise
    @staticmethod
    def scrape_static_website(url):
        try:
            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0 (KnowledgeBot/1.0)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            return soup.get_text(" ", strip=True)

        except requests.RequestException:
            logger.exception("Static scraping failed for URL: %s", url)
            raise

class KnowledgeService:
    @staticmethod
    def scrape_static_website(url):
        logger.info("Static scraping started for URL: %s", url)

        try:
            response = requests.get(
                url,
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0 (KnowledgeBot/1.0)"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "noscript", "iframe"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)

            logger.info(
                "Static scraping completed for URL: %s (text length=%s)",
                url,
                len(text or ""),
            )

            return text

        except requests.RequestException:
            logger.exception(
                "Static scraping failed for URL: %s",
                url,
            )
            raise
    @staticmethod
    def scrape_website_now(website):
        try:
            if website.scraping_type == "static":
                extracted_text = KnowledgeService.scrape_static_website(
                    website.url  
                )
            else:
                logger.warning(
                    "Dynamic scraping not implemented for website_id=%s",
                    website.id,
                )
                return

            if not extracted_text:
                logger.warning(
                    "Scraping returned empty content (website_id=%s)",
                    website.id,
                )
                return

            website.extracted_text = extracted_text
            website.last_scraped_at = timezone.now()
            website.save(
                update_fields=["extracted_text", "last_scraped_at"]
            )

            logger.info(
                "Website scraped synchronously (website_id=%s)",
                website.id,
            )

        except Exception:
            logger.exception(
                "Scraping failed for website_id=%s",
                website.id,
            )
            raise
