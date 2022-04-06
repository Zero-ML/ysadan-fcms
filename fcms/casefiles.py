import urllib
from pathlib import Path

from google.cloud import storage

from .common import get_env_var
from .invoices import Invoice, filename_to_invoice_key, get_registered_invoices


def register_all_invoices():
    registered = get_registered_invoices()
    CLOUD_BUCKET = get_env_var("CLOUD_BUCKET")
    bucket = storage.Client().bucket(CLOUD_BUCKET)
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
