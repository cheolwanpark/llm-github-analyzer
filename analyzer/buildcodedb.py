from repo import Repository
from codedb import CodeDB
import sys

if __name__ == "__main__":
    assert len(sys.argv) == 2
    repourl = sys.argv[1]

    repo = Repository(repourl)
    codedb = CodeDB(repo=repo)

    if not codedb.exists():
        repo.clone()
    codedb.build(threads=8)