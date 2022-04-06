import re
import i4u
import urllib
import dotenv
import logging

from enum import IntEnum
from pathlib import Path
from datetime import datetime
from google.cloud import storage
from pydantic import BaseModel

from .common import get_db, get_env_var

logger = logging.getLogger("fcms")


class InvoiceType(IntEnum):
    RECEIPT = 2
    INVOICERECEIPT = 3
    INVOICECREDIT = 4


class Invoice(BaseModel):
    case_key: int
    invoice_key: int
    amount: int = 0
    invoice_date: datetime | None = None
    i4u_id: str | None = None

    @property
    def invoice_type(self) -> int:
        # A bit hacky but it works
        return {
            3: InvoiceType.RECEIPT,
            5: InvoiceType.INVOICECREDIT,
            7: InvoiceType.INVOICERECEIPT,
        }[int(str(self.invoice_key)[0])].value

    def update_from_i4u(self):
        dotenv.load_dotenv()
        I4U_USER = get_env_var("I4U_USER")
        I4U_PASS = get_env_var("I4U_PASS")
        i4u_api = i4u.Invoice4U(I4U_USER, I4U_PASS)
        logger.info(f"Updating invoice {self.invoice_key} from i4u")
        try:
            i4u_doc = i4u_api.get_document(
                i4u.Document(
                    DocumentNumber=self.invoice_key,
                    DocumentType=self.invoice_type,
                    Items=[],
                    Payments=[],
                )
            )
        except i4u.Invoice4UException as e:
            logger.error(f"Could not get invoice from i4u: {e}")
        else:
            self.amount = i4u_doc.Total
            self.invoice_date = i4u_doc.IssueDate
            self.i4u_id = i4u_doc.UniqueID

    def register(self):
        self.update_from_i4u()
        if self.i4u_id:
            invoice = self.dict(exclude_none=True)
            db = get_db()
            db["invoices"].insert_one(invoice)


def get_registered_invoices() -> list[int]:
    db = get_db()
    return db["invoices"].distinct("invoice_key")


def filename_to_invoice_key(filename: str) -> bool | int:
    filename = filename.lower()
    if (
        filename.endswith(".pdf")
        and "invoiceorder" not in filename
        and ("receipt" in filename or "invoicecredit" in filename)
    ):
        invoice_key = re.findall(r"(?<!\d)\d{5}(?!\d)", filename)
        return int(invoice_key[0])
    return False


def register_all_invoices():
    registered = get_registered_invoices()
    bucket = storage.Client().bucket("ysadan-cases")
    for blob in bucket.list_blobs():
        try:
            blob_path = Path(urllib.parse.unquote(blob.path))
            invoice_key = filename_to_invoice_key(blob_path.name)
            case_key = int(blob_path.parent.name.split()[0])
        except (ValueError, IndexError):
            pass
        else:
            if invoice_key and case_key and invoice_key not in registered:
                Invoice(case_key=case_key, invoice_key=invoice_key).register()
