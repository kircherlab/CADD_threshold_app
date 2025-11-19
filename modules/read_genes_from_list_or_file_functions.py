import pandas as pd


class GeneInputError(Exception):
    """Raised when gene input parsing fails or input is ambiguous."""


class ReadFileError(Exception):
    """Raised when file can not be read or found"""


def genes_from_list_or_file(list_genes, file_genes):

    list_val = list_genes() if callable(list_genes) else list_genes
    file_val = file_genes() if callable(file_genes) else file_genes

    if bool(list_val) == bool(file_val):
        return None

    if list_val:
        return read_genes_from_list_input(list_val)

    genes = read_genes_from_file(file_val)
    if genes is None or not genes:
        raise GeneInputError("Could not parse uploaded gene file or no genes found in the uploaded file.")
    return genes

def read_genes_from_list_input(text):
    if text is None:
        return []
    genes = str(text).replace(",", "\n").splitlines()
    return [g.strip().upper() for g in genes if g and g.strip()]


def read_genes_from_file(file_val):
    try:
        file_info = file_val[0]
        file_path = file_info.get("datapath") or file_info.get("path")
    except Exception:
        raise ReadFileError("Invalid uploaded file descriptor.")

    if not file_path:
        raise ReadFileError("Uploaded file descriptor missing 'datapath' or 'path'.")

    try:
        with open(file_path, "rb") as fh:
            sample_bytes = fh.read(4096)
        sample = sample_bytes.decode(errors="ignore")
    except Exception:
        raise ReadFileError("Could not read the beginning of the file.")

    sep = guess_separator(sample)
    return read_df_or_lines(file_path, sep)


def guess_separator(sample_text: str):
    if "\t" in sample_text:
        return "\t"
    if ";" in sample_text:
        return ";"
    if "," in sample_text:
        return ","
    if "\n" in sample_text:
        return "\n"
    if " " in sample_text:
        return " "
    return None


def read_df_or_lines(file_path: str, sep):
    """Try to read a dataframe first; on failure, read plain lines.
    Returns a list of upper-case strings or raises ReadFileError Exception on total failure.
    """
    try:
        if sep:
            df = pd.read_csv(file_path, delimiter=sep, header=None, engine="python")
        else:
            df = pd.read_csv(file_path, sep=None, header=None, engine="python")
        return df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
    except Exception:
        try:
            with open(file_path, "r", errors="ignore") as fh:
                lines = [ln.strip() for ln in fh if ln.strip()]
            return [ln.upper() for ln in lines]
        except Exception:
            raise ReadFileError("Reading the file failed.")



