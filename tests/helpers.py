import tempfile
from pathlib import Path

from observer.config import Paths

REPO = Path(__file__).resolve().parent.parent


def message(msg_id="<1@x>", date="Mon, 2 Apr 2001 09:00:00 -0700 (PDT)", frm="a@enron.com",
            to="b@enron.com", subject="Meter 1517", body="Please extend the deal at meter 1517 for March flow today."):
    date_line = f"Date: {date}\n" if date else ""
    return f"Message-ID: {msg_id}\n{date_line}From: {frm}\nTo: {to}\nSubject: {subject}\nX-From: A\n\n{body}\n"


class TempCorpus:
    """A throwaway repo root with corpus/<mailbox>/<folder>/<n>. files."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.paths = Paths(Path(self._tmp.name))

    def add(self, rel: str, text: str, crlf=False):
        f = self.paths.corpus / (rel + ".")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode())
        return rel

    def cleanup(self):
        self._tmp.cleanup()
