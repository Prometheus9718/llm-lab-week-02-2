"""Portable integration checks. Run inside .venv: python -m unittest discover -s tests -v"""
from __future__ import annotations

from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

import pymupdf

PACKAGE = Path(__file__).resolve().parents[1]


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="llm-lab-check-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "path with spaces" / "llm-lab"
        self.root.mkdir(parents=True)
        shutil.copytree(PACKAGE / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        (self.root / "data/pdfs").mkdir(parents=True)

    def run_step(self, name, *arguments, success=True):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts" / name), *arguments],
            cwd=self.root, text=True, encoding="utf-8", capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def make_pdf(self, number):
        doc = pymupdf.open()
        page = doc.new_page()
        if number == 1:
            page.insert_text((50, 60), "CHAPTER 1", fontsize=24)
            page.insert_text((50, 95), "Overview", fontsize=20)
            page.insert_text((50, 130), "Opening paragraph preserved before the next heading.", fontsize=11)
            page.insert_text((50, 200), "Background", fontsize=18)
            for i in range(9):
                page.insert_text((50, 225+i*15), f"Background {i}: portable files and original text remain traceable in this lab.", fontsize=11)
            page.insert_text((50, 400), "Methods", fontsize=18)
            for i in range(9):
                page.insert_text((50, 425+i*15), f"Method {i}: section boundaries keep related lines together for retrieval.", fontsize=11)
            doc.new_page()  # Intentionally blank.
            final = doc.new_page()
            final.insert_text((50, 70), "Conclusion", fontsize=20)
            final.insert_text((50, 110), "The final paragraph must also appear in a chunk.", fontsize=11)
            doc.set_toc([[1,"Chapter 1. Overview",1], [2,"Background",1], [2,"Methods",1], [1,"Conclusion",3]])
        elif number == 2:
            # The page-top header must lose to a real heading farther down.
            page.insert_text((50, 30), "Background", fontsize=9)
            page.insert_text((50, 130), "Opening context before the true heading.", fontsize=11)
            page.insert_text((50, 200), "Background", fontsize=18)
            for i in range(12):
                page.insert_text((50, 230+i*15), f"Paragraph {i}: distinguish running headers from actual section headings.", fontsize=11)
            page.insert_text((50, 500), "Summary", fontsize=18)
            page.insert_text((50, 530), "Keep the summary and its page provenance.", fontsize=11)
            doc.set_toc([[1,"Background",1], [1,"Summary",1]])
        else:
            # No bookmarks and no typography signal: students provide anchors.
            for i, text in enumerate(["Introduction", "First paragraph to preserve.", "Conclusion", "Second paragraph to preserve."]):
                page.insert_text((50, 60+i*30), text, fontsize=11)
        path = self.root / "data/pdfs" / f"pdf{number}.pdf"
        doc.save(path)
        doc.close()
        return path

    def test_three_pdf_filenames_complete_pipeline(self):
        for number in (1, 2, 3):
            with self.subTest(pdf=number):
                path = self.make_pdf(number)
                argument = "data/pdfs/" + path.name
                self.run_step("03_extract_pdf.py", "--pdf", argument)
                directory = next((self.root / "data/extracted").glob(f"pdf{number}-*"))
                document = json.loads((directory / "document.json").read_text(encoding="utf-8"))
                self.assertEqual(document["source_file"], path.name)
                self.run_step("04_plan_sections.py", "--pdf", argument)
                self.run_step("05_build_sections.py", "--pdf", argument, success=False)
                plan_path = directory / "boundaries.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                self.assertFalse(plan["reviewed"])
                if number == 3:
                    lines = document["pages"][0]["lines"]
                    plan["boundaries"] = [
                        {"level":1,"title":line["text"],"pdf_page":1,"line_id":line["line_id"],"method":"manual_test_fixture","status":"accepted","note":"Known fixture heading"}
                        for line in (lines[0],lines[2])
                    ]
                else:
                    self.assertFalse([b for b in plan["boundaries"] if b["status"] == "unresolved"])
                if number == 2:
                    first = plan["boundaries"][0]
                    self.assertNotEqual(first["line_id"], "p0001-l0001", "Running header selected as heading")
                plan["reviewed"] = True  # Known synthetic fixtures only, not automatic approval of student PDFs.
                plan_path.write_text(json.dumps(plan),encoding="utf-8")
                self.run_step("04_plan_sections.py", "--pdf", argument)
                self.assertTrue(json.loads(plan_path.read_text())["reviewed"], "Existing review overwritten")
                self.run_step("05_build_sections.py", "--pdf", argument)
                self.run_step("06_chunk_sections.py", "--pdf", argument,"--max-chars","180","--overlap-chars","20")
                self.run_step("07_preview.py", "--pdf", argument,"--chunks","2")
                sections = [json.loads(row) for row in (directory/"sections.jsonl").read_text(encoding="utf-8").splitlines()]
                chunks = [json.loads(row) for row in (directory/"chunks.jsonl").read_text(encoding="utf-8").splitlines()]
                source = {line["line_id"]:line for page in document["pages"] for line in page["lines"]}
                assigned = Counter(span["line_id"] for section in sections for span in section["source_spans"])
                self.assertEqual(assigned, Counter({key:1 for key in source}))
                for section in sections:
                    for span in section["source_spans"]:
                        self.assertEqual(section["text"][span["start_char"]:span["end_char"]],source[span["line_id"]]["text"])
                    own = [chunk for chunk in chunks if chunk["section_id"] == section["section_id"]]
                    end = 0
                    for chunk in own:
                        self.assertLessEqual(chunk["section_start_char"],end)
                        self.assertLessEqual(chunk["char_count"],180)
                        self.assertEqual(chunk["text"],section["text"][chunk["section_start_char"]:chunk["section_end_char"]])
                        self.assertEqual(chunk["heading_path"],section["heading_path"])
                        for span in chunk["source_spans"]:
                            self.assertEqual(chunk["text"][span["start_char"]:span["end_char"]],source[span["line_id"]]["text"][span["line_start_char"]:span["line_end_char"]])
                            self.assertEqual(span["pdf_page"],source[span["line_id"]]["pdf_page"])
                        end=max(end,chunk["section_end_char"])
                    self.assertEqual(end,len(section["text"]))
                self.assertGreaterEqual(len(sections),2)
                self.assertTrue((directory/"preview.md").is_file())
                if number == 1:
                    self.assertEqual(document["pages"][1]["char_count"],0)
                # Corrupting a reviewed anchor must fail before output is rebuilt.
                plan["boundaries"][0]["line_id"]="p9999-l9999"
                plan_path.write_text(json.dumps(plan),encoding="utf-8")
                self.run_step("05_build_sections.py","--pdf",argument,success=False)

    def test_all_cli_help(self):
        for script in sorted((self.root/"scripts").glob("0*.py")):
            self.run_step(script.name,"--help")

    def test_embedding_http_client(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self):
                obj={"version":"test"} if self.path=="/api/version" else {"models":[{"name":"all-minilm:22m"}]}
                data=json.dumps(obj).encode();self.send_response(200);self.end_headers();self.wfile.write(data)
            def do_POST(self):
                payload=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path!="/api/embed" or len(payload["input"])!=3:
                    self.send_error(400);return
                vectors=[[1.0,0.0]+[0.0]*382,[0.9,0.1]+[0.0]*382,[0.0,1.0]+[0.0]*382]
                self.send_response(200);self.end_headers();self.wfile.write(json.dumps({"embeddings":vectors}).encode())
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            result=self.run_step("02_embedding_demo.py","--url",f"http://127.0.0.1:{server.server_port}")
            self.assertIn("Dimensions: 384",result.stdout)
            if sys.prefix!=sys.base_prefix:
                self.run_step("01_check_setup.py","--url",f"http://127.0.0.1:{server.server_port}")
        finally:
            server.shutdown();server.server_close();worker.join(timeout=5)


if __name__=="__main__":
    unittest.main()
