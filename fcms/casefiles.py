from .common import CASEFILES, logger
from .invoices import Invoice, filename_to_invoice_key, get_registered_invoices


def register_all_invoices():
    registered = get_registered_invoices()
    all_pdf = CASEFILES.glob("**/*.pdf")
    for pdf in all_pdf:
        invoice_key = filename_to_invoice_key(pdf.name)
        if invoice_key and invoice_key not in registered:
            try:
                case_key = pdf.parent.name.split()[0]
            except (IndexError, ValueError):
                logger.warning(f"Could not parse case key from {pdf.name} in {pdf.parent}")
            else:
                invoice = Invoice(case_key=case_key, invoice_key=invoice_key)
                invoice.register()
