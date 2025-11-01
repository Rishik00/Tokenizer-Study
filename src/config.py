from dataclasses import dataclass

@dataclass
class Args:
    lang: str
    tok: str
    log_results: bool
    batch_size: int
    seq_len: int