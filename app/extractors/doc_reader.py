import os
import subprocess
import tempfile
import logging

logger = logging.getLogger("resume_parser.extractors.doc")

def _get_libreoffice_binary() -> str:
    """Find the LibreOffice executable depending on the OS."""
    if os.name == 'nt':
        return "soffice.exe"
    elif os.uname().sysname == 'Darwin':
        return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    else:
        # Linux usually has 'libreoffice' or 'soffice' in PATH
        return "soffice"

def extract_text_from_doc(file_path: str) -> str:
    """
    Extracts text from older legacy .doc files using LibreOffice headless mode.
    Converts .doc to .txt in a temporary directory, reads it, and cleans it up.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    outdir = tempfile.gettempdir()
    soffice_bin = _get_libreoffice_binary()
    
    command = [
        soffice_bin,
        "--headless",
        "--convert-to",
        "txt:Text",
        file_path,
        "--outdir",
        outdir
    ]

    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"LibreOffice failed: {result.stderr}")
            raise RuntimeError(f"LibreOffice conversion failed. Ensure LibreOffice is installed. Error: {result.stderr}")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        txt_path = os.path.join(outdir, f"{base_name}.txt")

        if not os.path.exists(txt_path):
            raise FileNotFoundError("Conversion succeeded but text file was not generated.")

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Cleanup the temporary txt file
        os.remove(txt_path)
        return text

    except Exception as e:
        logger.error(f"Failed to extract text from DOC: {file_path}. Error: {str(e)}")
        raise ValueError(f"DOC extraction failed: {str(e)}")
